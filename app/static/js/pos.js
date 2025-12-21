/**
 * POS Logic
 */


const state = {
    cart: [],
    products: [],
    categories: [],
    tables: [],
    activeSales: [],
    selectedCategoryId: null,
    saleId: null, // If null, it's a direct immediate sale
    currentSale: null
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);

    // Check URL params
    const urlParams = new URLSearchParams(window.location.search);
    const saleId = urlParams.get('sale_id');
    if (saleId) state.saleId = parseInt(saleId);

    loadPos();
});

async function loadPos() {
    try {
        const [products, categories, tables, activeSales] = await Promise.all([
            api.getProducts(),
            api.getCategories(),
            api.getTables(),
            api.getActiveSales()
        ]);

        state.products = products;
        state.categories = [{ id: null, name: 'Todos' }, ...categories];
        state.tables = tables;
        state.activeSales = activeSales;
        state.selectedCategoryId = null;

        renderCategories();
        renderProductsGrid();
        renderOpenTablesSideList();

        // Load existing sale if in edit mode
        if (state.saleId) {
            const sale = await api.getSale(state.saleId);
            state.currentSale = sale;

            // Populate cart with existing lines for full editing
            state.cart = sale.lines.map(line => {
                const product = state.products.find(p => p.id === line.product_id);
                // If product not found (e.g. deleted), we might have issues. 
                // For now assuming active products.
                return {
                    product: product || { id: line.product_id, name: 'Producto Desconocido', price: line.price_unit },
                    quantity: line.quantity
                };
            });

            renderCart();
            updateSaleInfo(sale);
        }

    } catch (err) {
        console.error(err);
        showToast('Error cargando datos', 'error');
    }
}

function updateSaleInfo(sale) {
    const infoEl = document.getElementById('sale-info');
    if (infoEl) {
        let tableName = 'Sin Mesa';
        if (sale.table_id) {
            const table = state.tables.find(t => t.id === sale.table_id);
            if (table) tableName = table.name;
            else tableName = `Mesa #${sale.table_id}`;
        }

        infoEl.innerHTML = `
            <div>Mesa: <b>${tableName}</b></div>
            <div>Ticket: #${sale.id} - Previo: <b>${sale.total.toFixed(2)}€</b></div>
        `;
    }
}

function renderCategories() {
    const bar = document.getElementById('pos-categories');
    bar.innerHTML = state.categories.map(c => `
        <div class="category-pill ${c.id === state.selectedCategoryId ? 'active' : ''}"
             onclick="selectCategory(${c.id})">
            ${c.name}
        </div>
    `).join('');
}

function selectCategory(categoryId) {
    state.selectedCategoryId = categoryId;
    renderCategories(); // Re-render to update active class
    renderProductsGrid();
}

function renderProductsGrid() {
    const grid = document.getElementById('pos-products');

    let filteredProducts = state.products;
    if (state.selectedCategoryId !== null) {
        filteredProducts = state.products.filter(p => p.category_id === state.selectedCategoryId);
    }

    if (filteredProducts.length === 0) {
        grid.innerHTML = '<div style="color: var(--text-muted); grid-column: 1/-1; text-align: center; margin-top: 2rem;">No hay productos en esta categoría</div>';
        return;
    }

    grid.innerHTML = filteredProducts.map(p => `
        <div class="product-card" onclick="addToCart(${p.id})">

            <div>
                <div class="product-name">${p.name}</div>
                <div class="product-category-name">${p.category ? p.category.name : '-'}</div>
            </div>
            <div class="product-price">${p.price.toFixed(2)}€</div>
        </div>
    `).join('');
}

function addToCart(productId) {
    const product = state.products.find(p => p.id === productId);
    if (!product) return;

    const existing = state.cart.find(item => item.product.id === productId);
    if (existing) {
        existing.quantity++;
    } else {
        state.cart.push({ product, quantity: 1 });
    }
    renderCart();
}

function removeFromCart(index) {
    state.cart.splice(index, 1);
    renderCart();
}

function renderCart() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');

    let total = 0;

    if (state.cart.length === 0) {
        container.innerHTML = `
            <div class="text-center" style="color: var(--text-muted); margin-top: 2rem;">
                Ticket vacío
            </div>
        `;
    } else {
        container.innerHTML = state.cart.map((item, index) => {
            const itemTotal = item.product.price * item.quantity;
            total += itemTotal;
            return `
                <div class="cart-item">
                    <div class="cart-item-info">
                        <div class="cart-item-title">${item.product.name}</div>
                        <div class="cart-item-price">${item.quantity} x ${item.product.price.toFixed(2)}€</div>
                    </div>
                    <div class="cart-item-actions">
                        <div class="product-price">${itemTotal.toFixed(2)}€</div>
                        <button class="btn-icon" onclick="removeFromCart(${index})">✕</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    totalEl.textContent = `${total.toFixed(2)}€`;

    // If working on an open table, we might show grand total (existing + new)
    if (state.currentSale) {
        // logic to show grand total could go here
    }
}

async function saveOrder() {
    if (state.cart.length === 0) {
        showToast('El carrito está vacío', 'warning');
        return;
    }

    if (state.saleId) {
        // Active sale exists, add to it
        await addToActiveSale(state.saleId);
    } else {
        // No active sale, prompt for table
        openTableModal();
    }
}

async function addToActiveSale(saleId, redirect = true) {
    // Logic changed: Now we REPLACE the sale content with current cart to support edits/removals
    const lines = state.cart.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
    }));

    // Schema expects payment_method? strict check? Schema says optional.
    const saleData = {
        lines: lines
    };

    try {
        await api.updateSale(saleId, saleData);
        showToast('Pedido actualizado');
        // state.cart = []; // Do NOT clear cart if we stay, but if we redirect it doesn't matter.
        // If we stay, active editing implies cart should remain?
        // Actually, if we are in "Edit Mode", the cart IS the ticket.
        // So clearing it means clearing the ticket for the user visually unless we re-fetch.

        if (redirect) {
            if (confirm("Pedido guardado. ¿Volver a mesas?")) {
                window.location.href = 'active_orders.html';
            } else {
                // Reload to confirm sync
                const sale = await api.getSale(saleId);
                state.currentSale = sale;
                // Ensure cart matches returned state (in case of pricing changes etc)
                // But simply re-rendering what we have is faster.
                updateSaleInfo(sale);
            }
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Table Selection Logic
let availableTables = [];
let activeSalesForSelection = [];

async function openTableModal() {
    const modal = document.getElementById('table-selection-modal');
    const grid = document.getElementById('table-selection-grid');
    grid.innerHTML = '<div class="text-center">Cargando mesas...</div>';
    modal.classList.add('active'); // Assuming shared.css has .modal-overlay.active

    try {
        const [tables, activeSales] = await Promise.all([
            api.getTables(),
            api.getActiveSales()
        ]);
        availableTables = tables;
        activeSalesForSelection = activeSales;
        renderTableSelection();
    } catch (err) {
        grid.innerHTML = `<div class="text-center error">Error al cargar mesas: ${err.message}</div>`;
    }
}

function closeTableModal() {
    document.getElementById('table-selection-modal').classList.remove('active');
}

function renderTableSelection() {
    const grid = document.getElementById('table-selection-grid');
    grid.innerHTML = availableTables.map(table => {
        const sale = activeSalesForSelection.find(s => s.table_id === table.id);
        const isBusy = !!sale;
        const total = sale ? sale.total.toFixed(2) + '€' : 'Libre';
        const statusClass = isBusy ? 'status-busy' : 'status-free';

        return `
            <div class="table-card ${statusClass}" 
                 onclick="selectTableForSave(${table.id}, ${isBusy ? (sale ? sale.id : 'null') : 'null'})">
                <div class="table-icon">🪑</div>
                <div class="table-name">${table.name}</div>
                <div class="table-info">${isBusy ? 'Ocupada' : 'Disponible'}</div>
                ${isBusy ? `<div class="table-total">${total}</div>` : ''}
            </div>
        `;
    }).join('');

    // Grid styling is now handled by active_orders.css included in pos.html
    // but we can ensure the container has the class
    grid.className = 'tables-grid';
    grid.style.display = 'grid'; // Ensure grid display if css fails or overrides
    // Remove manual style injections that conflict with css class
    grid.style.gridTemplateColumns = '';
    grid.style.gap = '';
}

function renderOpenTablesSideList() {
    const container = document.getElementById('open-tables-list');
    if (!container) return; // Guard clause

    // Filter active sales that are assigned to a table
    const tableSales = state.activeSales.filter(s => s.table_id);

    if (tableSales.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem; font-style: italic;">No hay mesas abiertas</div>';
        return;
    }

    container.innerHTML = tableSales.map(sale => {
        const table = state.tables.find(t => t.id === sale.table_id);
        const tableName = table ? table.name : `Mesa #${sale.table_id}`;

        return `
            <div onclick="window.location.href='pos.html?sale_id=${sale.id}'" 
                 style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 0.75rem; 
                        cursor: pointer; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">🪑</span>
                    <span style="font-weight: 500;">${tableName}</span>
                </div>
                <div style="font-weight: 600; color: var(--primary-color);">${sale.total.toFixed(2)}€</div>
            </div>
        `;
    }).join('');
}

async function selectTableForSave(tableId, existingSaleId) {
    if (existingSaleId) {
        // Add to existing sale
        if (confirm("Esta mesa ya tiene una cuenta abierta. ¿Añadir productos a ella?")) {
            // We need to switch context to that sale? Or just add lines?
            // "Guardar en mesa" implies adding to it.
            // We assign active saleId to state and call save logic
            state.saleId = existingSaleId;
            closeTableModal();
            await saveOrder(); // Recursive call, but now state.saleId is set
        }
    } else {
        // Open new sale
        try {
            const sale = await api.openSale({ table_id: tableId });
            state.saleId = sale.id;
            closeTableModal();
            await saveOrder(); // Recursive call
        } catch (err) {
            showToast(err.message, 'error');
        }
    }
}

async function checkout() {
    // If empty cart and no open sale, ignore
    if (state.cart.length === 0 && !state.saleId) return;

    // If active sale:
    // 1. If cart has items, add them first (auto-save) or just confirm?
    // Let's assume we must add items first if any.

    const paymentMethod = document.getElementById('payment-method').value;

    try {
        if (state.saleId) {
            // Update sale with current cart content (Sync before close)
            const lines = state.cart.map(item => ({
                product_id: item.product.id,
                quantity: item.quantity
            }));

            // If cart is empty, do we allow closing? (Empty Sale)
            // Backend might complain if lines is empty for creation, but for update?
            // If sale has lines and we send [], it deletes them.

            if (state.cart.length > 0) {
                await api.updateSale(state.saleId, { lines: lines });
            } else {
                // Warn or allow? Assuming we allow closing zero.
            }

            // Close sale
            await api.closeSale(state.saleId, paymentMethod);
            showToast('Cuenta cerrada y cobrada');
            setTimeout(() => window.location.href = 'active_orders.html', 1000);

        } else {
            // Direct sale (Legacy/Quick mode)
            const saleData = {
                payment_method: paymentMethod,
                lines: state.cart.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity
                }))
            };
            await api.createSale(saleData);
            showToast('Venta realizada con éxito');
            state.cart = [];
            renderCart();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}
