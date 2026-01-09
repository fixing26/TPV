
document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadSales();
});

async function loadSales() {
    try {


        const sales = await api.getSales();
        const container = document.getElementById('sales-list');

        if (sales.length === 0) {
            container.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">No hay ventas registradas</p>';
            return;
        }

        container.innerHTML = sales.map(sale => `
            <div class="sale-card" onclick='openSaleDetail(${JSON.stringify(sale).replace(/'/g, "&#39;")})'>
                <div class="sale-header">
                    <strong>Ticket #${sale.id}</strong>
                    <span>${new Date(sale.created_at * 1000).toLocaleString()}</span>
                </div>
                <div class="sale-details">
                    ${sale.lines.length} productos (${sale.payment_method})
                </div>
                <div class="sale-total">
                    Total: ${sale.total.toFixed(2)}€
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
        showToast('Error cargando ventas', 'error');
    }
}

function openSaleDetail(sale) {
    document.getElementById('detail-id').textContent = sale.id;
    document.getElementById('detail-date').textContent = new Date(sale.created_at * 1000).toLocaleString();
    document.getElementById('detail-status').textContent = sale.status;
    document.getElementById('detail-creator').textContent = sale.creator ? sale.creator.username : 'Sistema';
    document.getElementById('detail-closer').textContent = sale.closer ? sale.closer.username : (sale.status === 'CLOSED' ? 'Desconocido' : '-');
    document.getElementById('detail-table').textContent = (sale.table_id ? `Mesa ${sale.table_id}` : '') + (sale.name ? ` (${sale.name})` : '');
    document.getElementById('detail-payment').textContent = sale.payment_method.toUpperCase();
    document.getElementById('detail-total').textContent = sale.total.toFixed(2) + '€';

    const linesContainer = document.getElementById('detail-lines');
    linesContainer.innerHTML = sale.lines.map(line => `
        <div class="detail-line">
            <span>${line.quantity}x</span>
            <span>${line.product ? line.product.name : 'Producto ' + line.product_id}</span>
            <span style="text-align: right;">${line.price_unit.toFixed(2)}€</span>
            <span style="text-align: right;">${line.line_total.toFixed(2)}€</span>
        </div>
    `).join('');

    document.getElementById('sale-detail-modal').classList.add('active');
}

function closeSaleDetail() {
    document.getElementById('sale-detail-modal').classList.remove('active');
}
