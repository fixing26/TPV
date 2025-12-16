/**
 * Shared Utility Functions
 */

/**
 * Checks authentication status and redirects if necessary.
 * @param {boolean} requireAuth - If true, redirects to login if not authenticated. If false (login page), redirects to menu if authenticated.
 */
function checkAuth(requireAuth = true) {
    const token = localStorage.getItem('token');

    if (requireAuth && !token) {
        window.location.href = 'index.html';
    } else if (!requireAuth && token) {
        window.location.href = 'menu.html';
    }
}

/**
 * Logs out the user.
 */
function logout() {
    api.logout();
}

/**
 * Shows a toast notification.
 * @param {string} msg - Message to display.
 * @param {string} type - 'success' or 'error'.
 */
function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.backgroundColor = type === 'error' ? 'var(--danger-color)' : 'var(--text-color)';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
