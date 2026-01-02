


const state = {
    cart: [],
    products: [],
    categories: [],
    tables: [],
    activeSales: [],
    selectedCategoryId: null,
    saleId: null,
    currentSale: null,
    currentSale: null,
    selectedCartIndex: null,
    numpadBuffer: ''
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);

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

            state.cart = sale.lines.map(line => {
                const product = state.products.find(p => p.id === line.product_id);

                return {
                    product: product || { id: line.product_id, name: 'Producto Desconocido', price: line.price_unit },
                    quantity: line.quantity
                };
            });

            renderCart();
            updateSaleInfo(sale);
            updateSaleInfo(sale);
            updateTableButtonUI(true);
        } else {
            updateTableButtonUI(false);
        }

    } catch (err) {
        console.error(err);
        showToast('Error cargando datos', 'error');
    }
}

function updateSaleInfo(sale) {

    const tableNameEl = document.getElementById('header-table-name');
    if (tableNameEl) {
        let tableName = 'Sin Mesa';
        if (sale.table_id) {
            const table = state.tables.find(t => t.id === sale.table_id);
            if (table) tableName = table.name;
            else tableName = `Mesa #${sale.table_id}`;
        }
        tableNameEl.textContent = tableName + (sale.id ? ` (Tkt: ${sale.id})` : '');
    }
}

function renderCategories() {
    const bar = document.getElementById('pos-categories');
    bar.innerHTML = state.categories.map(c => `
        <div class="category-btn ${c.id === state.selectedCategoryId ? 'active' : ''}"
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

    grid.innerHTML = filteredProducts.map((p, index) => {
        // Color variation logic based on index or category could go here
        // For now simple cycle based on id just to vary it
        // Or keep css nth-child logic which handles it based on DOM position
        return `
        <div class="product-btn" onclick="addToCart(${p.id})">
            <div>${p.name}</div>
            <div style="font-size: 0.8rem; margin-top: 2px;">${p.price.toFixed(2)}€</div>
        </div>
    `;
    }).join('');
}

function addToCart(productId) {
    const product = state.products.find(p => p.id === productId);
    if (!product) return;

    // Check numpad buffer for quantity
    let quantity = 1;
    if (state.numpadBuffer) {
        quantity = parseInt(state.numpadBuffer);
        quantity = parseInt(state.numpadBuffer);
        state.numpadBuffer = '';
        updateNumpadDisplay();
    }

    const existing = state.cart.find(item => item.product.id === productId);
    if (existing) {
        existing.quantity += quantity;
    } else {
        state.cart.push({ product, quantity: quantity });
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
        container.innerHTML = ``; // Empty list
    } else {
        container.innerHTML = state.cart.map((item, index) => {
            const itemTotal = item.product.price * item.quantity;
            total += itemTotal;
            const isSelected = index === state.selectedCartIndex;

            return `
                <div class="cart-line ${isSelected ? 'selected' : ''}" onclick="selectCartItem(${index})">
                    <div>${item.quantity}</div>
                    <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${item.product.name}</div>
                    <div>${itemTotal.toFixed(2)}€</div>
                </div>
            `;
        }).join('');
    }

    totalEl.textContent = `${total.toFixed(2)}€`;
}

// Selection Logic
function selectCartItem(index) {
    state.selectedCartIndex = index;
    state.selectedCartIndex = index;
    renderCart();
}

function removeSelectedItem() {
    if (state.selectedCartIndex !== null && state.cart[state.selectedCartIndex]) {
        removeFromCart(state.selectedCartIndex);
        state.selectedCartIndex = null;
    }
}

// Numpad logic
// Numpad logic
function numpadInput(key) {
    if (key === 'C') {
        state.numpadBuffer = '';

    } else {
        if (state.numpadBuffer.length < 5) {
            state.numpadBuffer += key.toString();
        }
    }

    updateNumpadDisplay();

    // If a cart item is selected, we MIGHT update it immediately?
    // If item selected, numpad updates it directly? 
    if (state.selectedCartIndex !== null && state.cart[state.selectedCartIndex]) {
        // Future: implement type to edit selected
    }
}

function updateNumpadDisplay() {
    const el = document.getElementById('numpad-display');
    if (el) el.textContent = state.numpadBuffer;
}

function toggleOpenTablesList() {
    const modal = document.getElementById('open-tables-modal');
    modal.classList.add('active');
    renderOpenTablesModalContent();
}

function renderOpenTablesModalContent() {
    const container = document.getElementById('open-tables-list-modal-content');
    if (!container) return;

    const tableSales = state.activeSales.filter(s => s.table_id);

    if (tableSales.length === 0) {
        container.innerHTML = '<div style="color: grey;">No hay mesas abiertas</div>';
        return;
    }

    container.innerHTML = tableSales.map(sale => {
        const table = state.tables.find(t => t.id === sale.table_id);
        const tableName = table ? table.name : `Mesa #${sale.table_id}`;

        return `
            <div onclick="window.location.href='pos.html?sale_id=${sale.id}'" 
                 style="background: white; border: 1px solid #ddd; border-radius: 4px; padding: 10px; 
                        cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                <strong>${tableName}</strong>
                <span style="color: blue; font-weight: bold;">${sale.total.toFixed(2)}€</span>
            </div>
        `;
    }).join('');
}

async function saveOrder() {
    if (state.cart.length === 0) {
        showToast('El carrito está vacío', 'warning');
        return;
    }

    if (state.saleId) {
        if (state.saleId) {
            await addToActiveSale(state.saleId);
        } else {
            // No active sale, prompt for table
            openTableModal();
        }
    }

    async function addToActiveSale(saleId, redirect = true) {
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
            showToast('Pedido actualizado');


            if (redirect) {
                // Stay on page as requested
                const sale = await api.getSale(saleId);
                state.currentSale = sale;
                updateSaleInfo(sale);
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

            // Simplified table card for modal
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
            const tableName = table ? table.name : `Mesa #${sale.table_id} `;

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
            // Add to existing sale - DIRECTLY (No confirmation asked)
            state.saleId = existingSaleId;
            closeTableModal();
            await saveOrder(); // Recursive call, but now state.saleId is set

            // Fix: Update Header
            const sale = await api.getSale(state.saleId);
            state.currentSale = sale;
            updateSaleInfo(sale);
            updateTableButtonUI(true);
        } else {
            // Open new sale
            try {
                const sale = await api.openSale({ table_id: tableId });
                state.saleId = sale.id;
                // Fix: Set current sale immediately
                state.currentSale = sale;

                closeTableModal();
                await saveOrder(); // Recursive call

                // Fix: Update Header
                updateSaleInfo(sale);
                updateTableButtonUI(true);

            } catch (err) {
                showToast(err.message, 'error');
            }
        }
    }

    function openPaymentModal() {
        if (state.cart.length === 0 && !state.saleId) return;

        const currentTotal = parseFloat(document.getElementById('cart-total').textContent.replace('€', ''));

        // If we have an active sale (server side), the local cart might be partial updates?
        // But `state.activeSales` has the server total? 
        // Actually `renderCart` calculates total from `state.cart`.
        // If we are in edit mode, `state.cart` represents the full state.

        document.getElementById('payment-total-display').textContent = currentTotal.toFixed(2) + '€';

        const modal = document.getElementById('payment-modal');
        modal.classList.add('active');
    }

    function closePaymentModal() {
        document.getElementById('payment-modal').classList.remove('active');
    }

    async function processPayment(paymentMethod) {



        try {
            if (state.saleId) {
                // Update sale with current cart content (Sync before close)
                const lines = state.cart.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity
                }));

                if (state.cart.length > 0) {
                    await api.updateSale(state.saleId, { lines: lines });
                }

                // Close sale
                await api.closeSale(state.saleId, paymentMethod);
                closePaymentModal();
                showToast('Cuenta cerrada y cobrada');
                // Reset state using reusable function
                resetPosState();


            } else {
                // Direct sale
                const saleData = {
                    payment_method: paymentMethod,
                    lines: state.cart.map(item => ({
                        product_id: item.product.id,
                        quantity: item.quantity
                    }))
                };
                await api.createSale(saleData);
                closePaymentModal();
                showToast('Venta realizada con éxito');
                state.cart = [];
                state.numpadBuffer = '';
                renderCart();
                updateNumpadDisplay();
            }
        } catch (err) {
        }
    }

    function exitToIndex() {
        window.location.href = 'index.html';
    }

    function resetPosState() {
        state.saleId = null;
        state.currentSale = null;
        state.cart = [];
        state.numpadBuffer = '';

        // clear header info
        updateSaleInfo({});

        renderCart();
        updateNumpadDisplay();
        updateTableButtonUI(false);
    }

    function handleTableButton() {
        if (state.saleId) {
            resetPosState();
            showToast("Vista de mesa cerrada");
        } else {
            openTableModal();
        }
    }

    function updateTableButtonUI(isActive) {
        const btn = document.getElementById('table-action-btn');
        if (!btn) return;

        // We can change icon/text to indicate "Exit" vs "Table"
        const spanText = btn.querySelector('span:last-child');
        const spanIcon = btn.querySelector('.icon');

        if (isActive) {
            if (spanText) spanText.textContent = 'Salir Mesa';
            if (spanIcon) spanIcon.textContent = '🚪'; // Door icon for exit
            btn.classList.add('btn-warning'); // Make it look different
        } else {
            if (spanText) spanText.textContent = 'Mesa';
            if (spanIcon) spanIcon.textContent = '🪑';
            btn.classList.remove('btn-warning');
        }
    }

    // User Selection Logic
    async function openUserSelectionModal() {
        const modal = document.getElementById('user-selection-modal');
        const grid = document.getElementById('user-selection-grid');
        grid.innerHTML = '<div class="text-center">Cargando usuarios...</div>';
        modal.classList.add('active');

        try {
            const users = await api.getUsers();
            renderUserSelectionGrid(users);
        } catch (err) {
            console.error(err);
            grid.innerHTML = '<div class="text-center error">Error al cargar usuarios</div>';
        }
    }

    function closeUserSelectionModal() {
        document.getElementById('user-selection-modal').classList.remove('active');
    }

    function renderUserSelectionGrid(users) {
        const grid = document.getElementById('user-selection-grid');

        // Get current user name to highlight
        const currentUserName = document.getElementById('user-display').textContent;

        grid.innerHTML = users.map(user => {
            const isActive = user.username === currentUserName;
            return `
            <div class="user-card ${isActive ? 'active-user' : ''}" onclick="selectUser('${user.username}', ${user.id})">
                <div class="user-avatar">👤</div>
                <div class="user-name">${user.username}</div>
                <div class="user-role">${user.role}</div>
            </div>
        `;
        }).join('');
    }

    function selectUser(username, userId) {
        // Update UI
        const userDisplay = document.getElementById('user-display');
        if (userDisplay) {
            userDisplay.textContent = username;
        }

        // For now, we just update the UI active user as requested. 

        closeUserSelectionModal();
        showToast(`Usuario cambiado a ${username}`);
    }
}