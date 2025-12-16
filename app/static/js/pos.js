/**
 * POS Logic
 */

const state = {
    cart: [],
    products: []
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadPos();
});

async function loadPos() {
    try {
        state.products = await api.getProducts();
        renderProductsGrid();
    } catch (err) {
        console.error(err);
        showToast('Error cargando productos', 'error');
    }
}

function renderProductsGrid() {
    const grid = document.getElementById('pos-products');
    grid.innerHTML = state.products.map(p => `
        <div class="product-card" onclick="addToCart(${p.id})">
            <div>
                <div class="product-name">${p.name}</div>
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
}

async function checkout() {
    if (state.cart.length === 0) return;

    const paymentMethod = document.getElementById('payment-method').value;

    const saleData = {
        payment_method: paymentMethod,
        lines: state.cart.map(item => ({
            product_id: item.product.id,
            quantity: item.quantity
        }))
    };

    try {
        await api.createSale(saleData);
        showToast('Venta realizada con éxito');
        state.cart = [];
        renderCart();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
