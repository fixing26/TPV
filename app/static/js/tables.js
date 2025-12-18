const state = {
    editingTableId: null
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    loadTables();
});

async function loadTables() {
    try {
        const tables = await api.getTables();
        const container = document.getElementById('tables-list');

        let html = tables.map(t => `
            <div class="table-card" onclick="openEditTable(${t.id}, '${t.name}', '${t.description || ''}')">
                <div class="table-icon">🪑</div>
                <div class="table-name">${t.name}</div>
                ${t.description ? `<div style="font-size:0.8rem; color:#666;">${t.description}</div>` : ''}
            </div>
        `).join('');

        // Add "New Table" button
        html += `
            <div class="table-card add-table-card" onclick="openNewTable()">
                <div class="table-icon">➕</div>
                <div class="table-name">Nueva Mesa</div>
            </div>
        `;

        container.innerHTML = html;
    } catch (err) {
        console.error(err);
        showToast(err.message, 'error');
    }
}

function openNewTable() {
    state.editingTableId = null;
    document.getElementById('modal-title').textContent = 'Nueva Mesa';
    document.getElementById('table-name').value = '';
    document.getElementById('table-desc').value = '';
    document.getElementById('btn-delete').style.display = 'none';
    document.getElementById('table-modal').classList.add('active');
}

function openEditTable(id, name, desc) {
    state.editingTableId = id;
    document.getElementById('modal-title').textContent = 'Editar Mesa';
    document.getElementById('table-name').value = name;
    document.getElementById('table-desc').value = desc;
    document.getElementById('btn-delete').style.display = 'block';
    document.getElementById('table-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('table-modal').classList.remove('active');
}

async function saveTable() {
    const name = document.getElementById('table-name').value;
    const description = document.getElementById('table-desc').value;

    if (!name) {
        showToast('El nombre es obligatorio', 'warning');
        return;
    }

    try {
        if (state.editingTableId) {
            await api.updateTable(state.editingTableId, { name, description });
            showToast('Mesa actualizada');
        } else {
            await api.createTable({ name, description });
            showToast('Mesa creada');
        }
        closeModal();
        loadTables();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteTable() {
    if (!state.editingTableId) return;
    if (!confirm('¿Estás seguro de eliminar esta mesa?')) return;

    try {
        await api.deleteTable(state.editingTableId);
        showToast('Mesa eliminada');
        closeModal();
        loadTables();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
