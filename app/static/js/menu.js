/**
 * Menu Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    checkAuth(true); // Redirect to login if not authenticated
    applyRolePermissions();
});

function applyRolePermissions() {
    const role = localStorage.getItem('role');

    if (role !== 'admin') {
        const restrictedLinks = [
            'products.html',
            'tables.html',
            'users.html'
        ];

        const cards = document.querySelectorAll('.menu-card');
        cards.forEach(card => {
            const href = card.getAttribute('href');
            if (restrictedLinks.includes(href)) {
                card.style.display = 'none';
            }
        });
    }
}

let selectedSwitchUser = null;

async function openSwitchUserModal() {
    try {
        const users = await api.getUsers();

        // Setup Views: Show Users Grid, Hide PIN
        document.getElementById('switch-view-pin').classList.add('hidden');
        document.getElementById('switch-view-users').classList.remove('hidden');

        const grid = document.getElementById('switch-user-grid');
        grid.innerHTML = users.map(user => `
            <div onclick="selectSwitchUser('${user.username}')" 
                 style="background: #fff; border: 1px solid #ccc; border-radius: 8px; 
                        display: flex; flex-direction: column; align-items: center; justify-content: center;
                        cursor: pointer; padding: 1rem; transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.05); aspect-ratio: 1;">
                <span style="font-size: 2.5rem; margin-bottom: 0.5rem;">👤</span>
                <div style="font-weight: 700; font-size: 1.1rem; text-align: center;">${user.username}</div>
            </div>
        `).join('');

        document.getElementById('switch-user-modal').classList.add('active');
    } catch (err) {
        showToast('Error cargando usuarios: ' + err.message, 'error');
    }
}

function closeSwitchUserModal() {
    document.getElementById('switch-user-modal').classList.remove('active');
    selectedSwitchUser = null;
    resetSwitchUser(); // Ensure reset for next open
}

function selectSwitchUser(username) {
    selectedSwitchUser = username;

    // Switch View: Hide Users, Show PIN
    document.getElementById('switch-view-users').classList.add('hidden');
    document.getElementById('switch-view-pin').classList.remove('hidden');
    document.getElementById('selected-username').textContent = username;

    // Reset PIN input
    document.getElementById('switch-pin-input').value = '';
}

function resetSwitchUser() {
    selectedSwitchUser = null;
    document.getElementById('switch-pin-input').value = '';
    // Switch View: Show Users, Hide PIN
    document.getElementById('switch-view-pin').classList.add('hidden');
    document.getElementById('switch-view-users').classList.remove('hidden');
}

// --- Keypad Logic ---
function appendPin(num) {
    const input = document.getElementById('switch-pin-input');
    if (input.value.length < 4) {
        input.value += num;
    }
}

function clearPin() {
    document.getElementById('switch-pin-input').value = '';
}

function submitPin() {
    // Trigger submit handler
    const form = document.getElementById('switch-pin-input').form;
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
}

async function handleSwitchUserLogin(e) {
    e.preventDefault();
    const pin = document.getElementById('switch-pin-input').value;

    if (!selectedSwitchUser || !pin) return;

    try {
        const data = await api.login(selectedSwitchUser, pin);
        api.setToken(data.access_token);
        localStorage.setItem('role', data.role || 'cashier');

        showToast('Sesión cambiada con éxito');
        setTimeout(() => window.location.reload(), 500);

    } catch (err) {
        showToast('PIN incorrecto', 'error');
        document.getElementById('switch-pin-input').value = '';
    }
}
