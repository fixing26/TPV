document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadData();
});

async function loadData() {
    try {
        const [tables, activeSales] = await Promise.all([
            api.getTables(),
            api.getActiveSales()
        ]);

        renderTables(tables, activeSales);
        renderOtherOrders(activeSales);
    } catch (err) {
        console.error(err);
        showToast('Error: ' + err.message, 'error');
    }
}

function renderTables(tables, activeSales) {
    const grid = document.getElementById('tables-grid');

    grid.innerHTML = tables.map(table => {
        // Find active sale for this table
        const sale = activeSales.find(s => s.table_id === table.id);
        const isBusy = !!sale;
        const total = sale ? sale.total.toFixed(2) + '€' : 'Libre';
        const statusClass = isBusy ? 'status-busy' : 'status-free';

        // If busy, click goes to POS with sale_id
        // If free, click opens new sale dialog/action for this table
        const clickAction = isBusy
            ? `window.location.href='pos.html?sale_id=${sale.id}'`
            : `openTable(${table.id}, '${table.name}')`;

        return `
            <div class="table-card ${statusClass}" onclick="${clickAction}">
                <div class="table-icon">🪑</div>
                <div class="table-name">${table.name}</div>
                <div class="table-info">${isBusy ? 'Ocupada' : 'Disponible'}</div>
                ${isBusy ? `<div class="table-total">${total}</div>` : ''}
            </div>
        `;
    }).join('');
}

function renderOtherOrders(activeSales) {
    const grid = document.getElementById('other-orders-grid');
    // Filter sales without table_id
    const others = activeSales.filter(s => !s.table_id);

    grid.innerHTML = others.map(sale => `
        <div class="table-card status-busy" onclick="window.location.href='pos.html?sale_id=${sale.id}'">
            <div class="table-icon">🛍️</div>
            <div class="table-name">${sale.name || 'Pedido #' + sale.id}</div>
            <div class="table-total">${sale.total.toFixed(2)}€</div>
        </div>
    `).join('');
}

async function openTable(tableId, tableName) {
    if (confirm(`¿Abrir cuenta para ${tableName}?`)) {
        try {
            const sale = await api.openSale({ table_id: tableId });
            window.location.href = `pos.html?sale_id=${sale.id}`;
        } catch (err) {
            showToast(err.message, 'error');
        }
    }
}

async function openCustomOrder() {
    const name = prompt("Nombre/Referencia del pedido:");
    if (!name) return;
    try {
        const sale = await api.openSale({ name: name });
        window.location.href = `pos.html?sale_id=${sale.id}`;
    } catch (err) {
        showToast(err.message, 'error');
    }
}
