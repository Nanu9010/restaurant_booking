/**
 * Signup Form Handling
 */
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');

    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
});

/**
 * Handle signup form submission
 * @param {Event} e - Form submission event
 */
async function handleSignup(e) {
    e.preventDefault();

    // Get form elements
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    // Basic validation
    if (!username || !email || !password) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }

    if (password.length < 8) {
        showAlert('Password must be at least 8 characters long', 'error');
        return;
    }

    try {
        // Show loading state
        const submitBtn = document.querySelector('#signupForm button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Creating Account...';

        // Make API call to signup
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password,
                role: 'owner' // Default role is owner
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Signup failed');
        }

        // Store user data and token
        if (data.token && data.user) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Redirect to profile page
            window.location.href = '/profile/';
        }

    } catch (error) {
        console.error('Signup error:', error);
        showAlert(error.message || 'Failed to create account. Please try again.', 'error');
    } finally {
        // Reset button state
        const submitBtn = document.querySelector('#signupForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Sign Up';
        }
    }
}

/**
 * Show alert message
 * @param {string} message - Message to display
 * @param {string} type - Type of alert (success, error, warning, info)
 */
function showAlert(message, type = 'info') {
    // Remove any existing alerts
    const existingAlert = document.querySelector('.auth-alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `auth-alert alert-${type}`;
    alertDiv.textContent = message;

    // Insert after the auth header
    const authHeader = document.querySelector('.auth-header');
    if (authHeader) {
        authHeader.parentNode.insertBefore(alertDiv, authHeader.nextSibling);
    } else {
        // Fallback to prepend to form
        const form = document.getElementById('signupForm');
        if (form) {
            form.prepend(alertDiv);
        }
    }

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Add CSS for alerts
const style = document.createElement('style');
style.textContent = `
    .auth-alert {
        padding: 12px 16px;
        border-radius: 4px;
        margin: 16px 0;
        font-size: 14px;
        animation: slideDown 0.3s ease-out;
    }

    .alert-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }

    .alert-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    .alert-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }

    .alert-info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);