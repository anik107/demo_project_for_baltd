const API_BASE_URL = 'http://localhost:8000/api';
// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Check if user is authenticated
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    loadUserInfo();
}

function loadUserInfo() {
    const userData = getUserData();
    const userInfoContainer = document.getElementById('userInfo');

    if (userData) {
        userInfoContainer.innerHTML = `
            <div class="user-card">
                <h2>Hello, ${userData.full_name}!</h2>
                <p><strong>Email:</strong> ${userData.email}</p>
                <p><strong>User Type:</strong> ${userData.user_type}</p>
                <p><strong>Mobile:</strong> ${userData.mobile_number}</p>
            </div>
        `;

        // Show doctor-specific actions if user is a doctor
        if (userData.user_type === 'DOCTOR') {
            document.getElementById('doctorActions').style.display = 'block';
        }
    }
}

// Utility functions (reuse from login.js)
function getAuthToken() {
    return localStorage.getItem('access_token');
}

function getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
}

function isAuthenticated() {
    return !!getAuthToken();
}

async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            const token = getAuthToken();

            // Call the backend logout endpoint to blacklist the token
            if (token) {
                const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    console.log('Successfully logged out from server');
                } else {
                    console.warn('Server logout failed, but continuing with local logout');
                }
            }
        } catch (error) {
            console.warn('Error during server logout:', error);
            // Continue with local logout even if server logout fails
        } finally {
            // Always clear local storage and redirect
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
            window.location.href = '/login';
        }
    }
}
