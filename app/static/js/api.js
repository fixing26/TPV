const API_URL = ''; // Relative path

/**
 * API Client
 * Handles all HTTP requests to the backend API.
 */
class ApiClient {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            this.logout();
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }

        return response.json();
    }

    // --- Auth Endpoints ---
    async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    }

    async register(username, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    }


    // --- Products Endpoints ---
    async getProducts() {
        return this.request('/products/');
    }

    async createProduct(product) {
        return this.request('/products/', {
            method: 'POST',
            body: JSON.stringify(product),
        });
    }

    async getCategories() {
        return this.request('/products/categories/');
    }


    async createCategory(category) {
        return this.request('/products/categories/', {
            method: 'POST',
            body: JSON.stringify(category),
        });
    }

    async updateCategory(id, category) {
        return this.request(`/products/categories/${id}`, {
            method: 'PUT',
            body: JSON.stringify(category),
        });
    }

    // --- Sales Endpoints & cash closing Endpoints ---
    async createSale(saleData) {
        return this.request('/sales/', {
            method: 'POST',
            body: JSON.stringify(saleData),
        });
    }

    async createCashClosing() {
        return this.request('/cash-closing/', {
            method: 'POST',
        });
    }

    async deleteSales() {
        return this.request('/cash-closing/sales', {
            method: 'DELETE',
        });
    }

    async getSales() {
        return this.request('/sales/');
    }
}

const api = new ApiClient();
