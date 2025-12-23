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
