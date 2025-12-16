/**
 * Sales Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadSales();
});

async function loadSales() {
    try {


        const sales = await api.getSales();
        const container = document.getElementById('sales-list');
        container.innerHTML = sales.map(sale => `
            <div class="sale-card">
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
