/**
 * Validation and UI Utility Functions
 */

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone format
 */
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

/**
 * Validate password strength
 */
function validatePassword(password) {
    const errors = [];

    if (password.length < 8) {
        errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
    }
    if (!/\d/.test(password)) {
        errors.push('Password must contain at least one number');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Show field error
 */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.add('error');

    // Remove existing error message
    const existingError = field.parentElement.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }

    // Add new error message
    if (message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }
}

/**
 * Clear field error
 */
function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.remove('error');

    const errorDiv = field.parentElement.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Clear all form errors
 */
function clearAllErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    form.querySelectorAll('.form-error').forEach(el => el.remove());
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format time for display
 */
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Handle API errors and show appropriate messages
 */
function handleAPIError(error, formId = null) {
    console.error('API Error:', error);

    if (error.status === 400 && error.data) {
        // Validation errors
        if (formId) {
            Object.keys(error.data).forEach(field => {
                const message = Array.isArray(error.data[field])
                    ? error.data[field][0]
                    : error.data[field];
                showFieldError(field, message);
            });
        } else {
            const firstError = Object.values(error.data)[0];
            const message = Array.isArray(firstError) ? firstError[0] : firstError;
            showToast(message, 'error');
        }
    } else if (error.status === 401) {
        showToast('Authentication required. Please login.', 'error');
        setTimeout(() => window.location.href = '/login/', 2000);
    } else if (error.status === 403) {
        showToast('Access denied', 'error');
    } else if (error.status === 404) {
        showToast('Resource not found', 'error');
    } else if (error.status >= 500) {
        showToast('Server error. Please try again later.', 'error');
    } else {
        showToast(error.error || 'An error occurred', 'error');
    }
}

/**
 * Confirm action
 */
function confirmAction(message) {
    return confirm(message);
}

// Make functions available globally
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.isValidEmail = isValidEmail;
window.isValidPhone = isValidPhone;
window.validatePassword = validatePassword;
window.showFieldError = showFieldError;
window.clearFieldError = clearFieldError;
window.clearAllErrors = clearAllErrors;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.debounce = debounce;
window.handleAPIError = handleAPIError;
window.confirmAction = confirmAction;
