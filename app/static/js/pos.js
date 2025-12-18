/**
 * POS Logic
 */


const state = {
    cart: [],
    products: [],
    categories: [],
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
        const [products, categories] = await Promise.all([
            api.getProducts(),
            api.getCategories()
        ]);

        state.products = products;
        state.categories = [{ id: null, name: 'Todos' }, ...categories];
        state.selectedCategoryId = null;

        renderCategories();
        renderProductsGrid();

        // Load existing sale if in edit mode
        if (state.saleId) {
            const sale = await api.getSale(state.saleId);
            state.currentSale = sale;
            // Load existing lines? 
            // Design decision: Do we load existing lines into the cart as editable? 
            // Or only show them as "Already ordered" and cart is "New items"?
            // Simple approach: Cart starts empty (new items), display total of existing sale somewhere.
            // OR: We don't display existing items in this cart array, but we show a summary.
            updateSaleInfo(sale);
        }

    } catch (err) {
        console.error(err);
        showToast('Error cargando datos', 'error');
    }
}

function updateSaleInfo(sale) {
    const totalEl = document.getElementById('cart-total-existing');
    if (totalEl) totalEl.textContent = `Previo: ${sale.total.toFixed(2)}€`;
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
    if (!state.saleId) {
        showToast('Esta función es solo para mesas abiertas', 'warning');
        return;
    }

    const lines = state.cart.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
    }));

    try {
        await api.addLinesToSale(state.saleId, lines);
        showToast('Pedido guardado en mesa');
        state.cart = [];
        // Reload sale to update totals
        const sale = await api.getSale(state.saleId);
        state.currentSale = sale;
        renderCart();
        // Redirect back to tables map?
        if (confirm("Pedido guardado. ¿Volver a mesas?")) {
            window.location.href = 'active_orders.html';
        }
    } catch (err) {
        showToast(err.message, 'error');
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
            // Add pending items if any
            if (state.cart.length > 0) {
                const lines = state.cart.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity
                }));
                await api.addLinesToSale(state.saleId, lines);
                state.cart = [];
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
