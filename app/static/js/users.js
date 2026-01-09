
document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true);
    const role = localStorage.getItem('role');
    if (role !== 'admin') {
        alert('Acceso no autorizado');
        window.location.href = 'menu.html';
        return;
    }
    loadUsers();
});

async function loadUsers() {
    try {
        const users = await api.getUsers();
        const container = document.getElementById('users-list');

        if (users.length === 0) {
            container.innerHTML = '<p style="text-align: center;">No hay usuarios registrados</p>';
            return;
        }

        container.innerHTML = users.map(user => `
            <div class="user-card">
                <div class="user-info">
                    <div class="menu-icon" style="font-size: 1.5rem;">👤</div>
                    <div>
                        <div style="font-weight: 600;">${user.username}</div>
                        <div class="user-role">${user.role === 'admin' ? 'Administrador' : 'Empleado'}</div>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="deleteUser(${user.id})" style="padding: 0.5rem 1rem; font-size: 0.8rem;">Eliminar</button>
            </div>
        `).join('');

    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleCreateUser(e) {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const pin = form.pin.value;
    const role = form.role.value;

    try {
        await api.createUser({
            username: username,
            password: pin,
            role: role
        });
        showToast('Usuario creado con éxito');
        form.reset();
        loadUsers();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return;

    try {
        await api.deleteUser(userId);
        showToast('Usuario eliminado');
        setTimeout(() => window.location.reload(), 1000);
    } catch (err) {
        showToast(err.message, 'error');
    }
}
