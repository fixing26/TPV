/**
 * Auth Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(false); // Redirect to menu if already logged in
});

async function handleLogin(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;

    try {
        const data = await api.login(username, password);
        api.setToken(data.access_token);
        // Store role for frontend permission checks
        localStorage.setItem('role', data.role || 'cashier');
        window.location.href = 'menu.html';
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;

    // Validate Email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(username)) {
        showToast('Por favor introduce un email válido', 'error');
        return;
    }

    // Validate Password
    if (password.length < 8) {
        showToast('La contraseña debe tener al menos 8 caracteres', 'error');
        return;
    }
    if (!/[A-Z]/.test(password)) {
        showToast('La contraseña debe contener al menos una mayúscula', 'error');
        return;
    }
    if (!/\d/.test(password)) {
        showToast('La contraseña debe contener al menos un número', 'error');
        return;
    }
    if (!/[!@#$%^&*]/.test(password)) {
        showToast('La contraseña debe contener al menos un carácter especial (!@#$%^&*)', 'error');
        return;
    }

    try {
        await api.register(username, password);
        showToast('Usuario registrado. Por favor inicia sesión.');
        showLogin();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function showLogin() {
    document.getElementById('register-screen').classList.add('hidden');
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('register-form').reset();
    document.getElementById('login-form').reset();
}

function showRegister() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('register-screen').classList.remove('hidden');
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
}
