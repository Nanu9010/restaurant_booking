/**
 * Authentication Utility Functions
 * Handle user authentication state and redirects
 */

const Auth = {
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!API.getToken();
    },

    /**
     * Get current user from localStorage
     */
    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                return JSON.parse(userStr);
            } catch (e) {
                return null;
            }
        }
        return null;
    },

    /**
     * Save user data to localStorage
     */
    setCurrentUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    /**
     * Get user role
     */
    getUserRole() {
        const user = this.getCurrentUser();
        return user?.profile?.role || null;
    },

    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.getUserRole() === 'admin';
    },

    /**
     * Check if user is owner
     */
    isOwner() {
        return this.getUserRole() === 'owner';
    },

    /**
     * Get dashboard URL based on role
     */
    getDashboardURL() {
        const user = this.getCurrentUser();
        return user?.profile?.dashboard_url || '/login/';
    },

    /**
     * Logout user
     */
    async logout() {
        // Call logout API
        await API.post('/api/auth/logout/', {}, true);

        // Clear local storage
        API.removeToken();
        localStorage.removeItem('user');

        // Redirect to login
        window.location.href = '/login/';
    },

    /**
     * Redirect to appropriate dashboard
     */
    redirectToDashboard() {
        window.location.href = this.getDashboardURL();
    },

    /**
     * Redirect to login if not authenticated
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login/';
            return false;
        }
        return true;
    },

    /**
     * Redirect to dashboard if already authenticated
     */
    requireGuest() {
        if (this.isAuthenticated()) {
            this.redirectToDashboard();
            return false;
        }
        return true;
    },

    /**
     * Require specific role
     */
    requireRole(role) {
        if (!this.isAuthenticated()) {
            window.location.href = '/login/';
            return false;
        }

        if (this.getUserRole() !== role) {
            showToast('Access denied', 'error');
            this.redirectToDashboard();
            return false;
        }

        return true;
    }
};

// Make Auth available globally
window.Auth = Auth;
