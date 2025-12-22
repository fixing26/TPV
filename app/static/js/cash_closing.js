/**
 * Cash Closing Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true); // Ensure user is logged in
});


async function handleClosing() {
    try {
        const result = await api.createCashClosing();
        showResult(result);
        showToast('Cierre realizado correctamente', 'success');

    } catch (err) {
        console.error(err);
        showToast(err.message || 'Error al realizar el cierre', 'error');
    }
}

// function confirmDelete() {
//     if (!confirm("¿ESTÁS SEGURO?\n\nEsta acción borrará todas las ventas actuales de la base de datos.\nNo se puede deshacer.")) {
//         return;
//     }
//     executeDelete();
// }

function openConfirmModal() {
    document.getElementById('confirm-modal').classList.add('active');
}

function closeConfirmModal() {
    document.getElementById('confirm-modal').classList.remove('active');
}

async function executeDelete() {
    closeConfirmModal();
    try {
        const result = await api.deleteSales();
        showToast('Ventas eliminadas correctamente', 'info');
        showResult(result);
    } catch (err) {
        console.error(err);
        showToast(err.message || 'Error al eliminar las ventas', 'error');
    }
}

function showResult(data) {
    const resultArea = document.getElementById('result-area');
    const resultContent = document.getElementById('result-content');

    resultArea.style.display = 'block';

    const formatted = `
ID Cierre: #${data.id}
Tipo:      ${data.closing_type}
Fecha:     ${new Date(data.date * 1000).toLocaleString()}
Usuario:   ${data.user_id}

Efectivo:  ${data.total_cash.toFixed(2)}€
Tarjeta:   ${data.total_card.toFixed(2)}€
--- Totales ---
Ventas:    ${data.total_sales}
Total:     ${data.total_total.toFixed(2)}€
----------------
    `.trim();

    resultContent.textContent = formatted;
}

