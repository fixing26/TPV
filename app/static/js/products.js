/**
 * Products Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadProducts();
});

async function loadProducts() {
    try {
        const products = await api.getProducts();
        const tbody = document.getElementById('products-table-body');
        tbody.innerHTML = products.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.price.toFixed(2)}€</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error(err);
        showToast('Error cargando productos', 'error');
    }
}

async function handleCreateProduct(e) {
    e.preventDefault();
    const data = {
        name: e.target.name.value,
        price: parseFloat(e.target.price.value),
        tax_rate: 21.0,
    };

    try {
        await api.createProduct(data);
        showToast('Producto creado');
        e.target.reset();
        loadProducts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
