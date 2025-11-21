/**
 * API Utility Functions
 * Centralized API calls with error handling
 */

const API = {
    baseURL: 'http://localhost:8000',

    /**
     * Get authentication token from localStorage
     */
    getToken() {
        return localStorage.getItem('authToken');
    },

    /**
     * Set authentication token
     */
    setToken(token) {
        localStorage.setItem('authToken', token);
    },

    /**
     * Remove authentication token
     */
    removeToken() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
    },

    /**
     * Get headers for API requests
     */
    getHeaders(includeAuth = false) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Token ${token}`;
            }
        }

        return headers;
    },

    /**
     * Generic API request function
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.auth),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    data: data,
                    message: data.error || data.detail || 'Request failed'
                };
            }

            return { success: true, data };
        } catch (error) {
            console.error('API Error:', error);
            return {
                success: false,
                error: error.message || 'Network error',
                status: error.status,
                data: error.data
            };
        }
    },

    /**
     * GET request
     */
    async get(endpoint, auth = false) {
        return this.request(endpoint, {
            method: 'GET',
            auth
        });
    },

    /**
     * POST request
     */
    async post(endpoint, data, auth = false) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            auth
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data, auth = false) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            auth
        });
    },

    /**
     * PATCH request
     */
    async patch(endpoint, data, auth = false) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
            auth
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint, auth = false) {
        return this.request(endpoint, {
            method: 'DELETE',
            auth
        });
    }
};

// Make API available globally
window.API = API;
