
document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    if (localStorage.getItem('role') !== 'admin') {
        alert('Acceso restringido a administradores');
        window.location.href = 'menu.html';
        return;
    }
    loadData();
});

async function loadData() {
    try {
        const [products, categories] = await Promise.all([
            api.getProducts(),
            api.getCategories()
        ]);
        renderProducts(products);
        renderCategoryOptions(categories);
    } catch (err) {
        console.error(err);
        showToast('Error cargando datos', 'error');
    }
}

function renderProducts(products) {
    const tbody = document.getElementById('products-table-body');
    tbody.innerHTML = products.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.category ? p.category.name : '<span style="color: red;">Sin Categoría</span>'}</td>
            <td>${p.price.toFixed(2)}€</td>
        </tr>
    `).join('');
}

function renderCategoryOptions(categories) {
    const select = document.getElementById('category-select');
    select.innerHTML = '<option value="">Seleccionar Categoría...</option>' +
        categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    const list = document.getElementById('categories-list');
    if (list) {
        list.innerHTML = categories.map(c => `
            <div class="category-item">
                <span class="category-item-name">${c.name}</span>
                <div class="category-actions">
                    <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;"
                            onclick="openEditCategory(${c.id}, '${c.name.replace(/'/g, "\\'")}')">
                        Editar
                    </button>
                </div>
            </div>
        `).join('');
    }
}


async function handleCreateProduct(e) {
    e.preventDefault();
    const categoryId = e.target.category_id.value;

    if (!categoryId) {
        showToast('Debes seleccionar una categoría', 'error');
        return;
    }

    const data = {
        name: e.target.name.value,
        price: parseFloat(e.target.price.value),
        tax_rate: 21.0,
        category_id: parseInt(categoryId)
    };

    try {
        await api.createProduct(data);
        showToast('Producto creado');
        e.target.reset();
        loadData();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleCreateCategory(e) {
    e.preventDefault();
    const data = {
        name: e.target.name.value
    };

    try {
        await api.createCategory(data);
        showToast('Categoría creada', 'success');
        e.target.reset();
        loadData();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function openEditCategory(id, currentName) {
    const newName = prompt('Nuevo nombre para la categoría:', currentName);
    if (newName && newName !== currentName) {
        try {
            await api.updateCategory(id, { name: newName });
            showToast('Categoría actualizada');
            loadData();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }
}
