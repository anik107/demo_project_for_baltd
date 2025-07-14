// API Configuration
const API_BASE_URL = 'http://localhost:8000/api'; // Adjust this to your backend URL

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeLoginForm();
    checkRegistrationSuccess();
});

// Check if coming from successful registration
function checkRegistrationSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('registered') === 'true') {
        const successMessage = document.getElementById('registrationSuccess');
        if (successMessage) {
            successMessage.style.display = 'block';
            // Remove the parameter from URL without page reload
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }
}

// Initialize login form
function initializeLoginForm() {
    const form = document.getElementById('loginForm');

    // Form submission
    form.addEventListener('submit', handleLoginSubmit);

    // Real-time validation
    setupRealTimeValidation();
}

// Real-time validation setup
function setupRealTimeValidation() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearError(input));
    });
}

// Field validation
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;

    clearError(field);

    switch(fieldName) {
        case 'email':
            return validateEmail(value, field);
        case 'password':
            return validatePassword(value, field);
        default:
            return true;
    }
}

// Email validation
function validateEmail(value, field) {
    if (!value) {
        showError(field, 'Email is required');
        return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
        showError(field, 'Please enter a valid email address');
        return false;
    }

    return true;
}

// Password validation
function validatePassword(value, field) {
    if (!value) {
        showError(field, 'Password is required');
        return false;
    }

    return true;
}

// Show error message
function showError(field, message) {
    const errorElement = document.getElementById(field.id + 'Error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    field.classList.add('error');
}

// Clear error message
function clearError(field) {
    const errorElement = document.getElementById(field.id + 'Error');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
    field.classList.remove('error');
}

// Clear all errors
function clearAllErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.textContent = '';
        element.style.display = 'none';
    });

    const errorFields = document.querySelectorAll('.error');
    errorFields.forEach(field => {
        field.classList.remove('error');
    });
}

// Show message
function showMessage(message, type = 'info') {
    const messageContainer = document.getElementById('messageContainer');
    const messageContent = document.getElementById('messageContent');

    messageContent.innerHTML = `
        <div class="message ${type}">
            <p>${message}</p>
        </div>
    `;

    messageContainer.style.display = 'block';

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 3000);
    }
}

// Toggle password visibility
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.nextElementSibling;

    if (field.type === 'password') {
        field.type = 'text';
        button.textContent = '🙈';
    } else {
        field.type = 'password';
        button.textContent = '👁️';
    }
}

// Handle login form submission
async function handleLoginSubmit(event) {
    event.preventDefault();

    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoader = loginBtn.querySelector('.btn-loader');

    // Clear previous errors
    clearAllErrors();

    // Validate form
    const form = event.target;
    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');

    let isValid = true;

    if (!validateEmail(emailField.value.trim(), emailField)) {
        isValid = false;
    }

    if (!validatePassword(passwordField.value.trim(), passwordField)) {
        isValid = false;
    }

    if (!isValid) {
        showMessage('Please correct the errors above', 'error');
        return;
    }

    // Show loading state
    loginBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    try {
        // Prepare login data
        const loginData = {
            email: emailField.value.trim(),
            password: passwordField.value.trim(),
            remember_me: document.getElementById('rememberMe').checked
        };

        // Submit to API
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }

        const result = await response.json();

        // Store authentication token if provided
        if (result.access_token) {
            localStorage.setItem('access_token', result.access_token);

            // Store user data if provided
            if (result.user) {
                console.log('Storing user data:', result.user);
                localStorage.setItem('user_data', JSON.stringify(result.user));
            } else {
                console.warn('No user data in login response');
            }
        }

        showMessage('Login successful! Redirecting...', 'success');

        // Redirect to dashboard or home page after successful login
        setTimeout(() => {
            window.location.href = '/dashboard'; // You can change this to your desired redirect URL
        }, 1500);

    } catch (error) {
        console.error('Login error:', error);
        showMessage(error.message || 'Login failed. Please check your credentials.', 'error');
    } finally {
        // Reset button state
        loginBtn.disabled = false;
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
    }
}

// Utility function to get stored auth token
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Utility function to get stored user data
function getUserData() {
    try {
        const userData = localStorage.getItem('user_data');
        if (!userData) {
            console.warn('No user data found in localStorage');
            return null;
        }
        const parsedData = JSON.parse(userData);
        console.log('Retrieved user data:', parsedData);
        return parsedData;
    } catch (error) {
        console.error('Error parsing user data from localStorage:', error);
        // Clear corrupted data
        localStorage.removeItem('user_data');
        return null;
    }
}

// Utility function to check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Utility function to logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login';
}
