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

    // Always fetch fresh user data to ensure we have profile image info
    // This ensures we get the latest data including profile images
    fetchUserDataFromServer();

    // Load notifications
    loadNotifications();
}

function loadUserInfo() {
    const userData = getUserData();
    const userInfoContainer = document.getElementById('userInfo');

    console.log('Loading user info with data:', userData);

    if (userData) {
        // Debug profile image data
        console.log('Profile image filename:', userData.profile_image_filename);
        console.log('Profile image content type:', userData.profile_image_content_type);

        // Create profile image HTML
        let profileImageHtml = '';
        if (userData.profile_image_filename) {
            const imageUrl = `static/profiles/${userData.profile_image_filename}`;
            console.log('Profile image URL:', imageUrl);

            profileImageHtml = `
                <div class="profile-image">
                    <img src="${imageUrl}"
                         alt="Profile Picture"
                         onerror="console.error('Failed to load profile image:', '${imageUrl}'); this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="profile-placeholder" style="display: none;">
                        <span>${userData.full_name.charAt(0).toUpperCase()}</span>
                    </div>
                </div>
            `;
        } else {
            console.log('No profile image filename, showing placeholder');
            profileImageHtml = `
                <div class="profile-image">
                    <div class="profile-placeholder">
                        <span>${userData.full_name ? userData.full_name.charAt(0).toUpperCase() : 'U'}</span>
                    </div>
                </div>
            `;
        }

        userInfoContainer.innerHTML = `
            <div class="user-card">
                ${profileImageHtml}
                <div class="user-details">
                    <h2>Hello, ${userData.full_name || 'User'}!</h2>
                    <p><strong>Email:</strong> ${userData.email || 'Not available'}</p>
                    <p><strong>User Type:</strong> ${userData.user_type || 'Not specified'}</p>
                    <p><strong>Mobile:</strong> ${userData.mobile_number || 'Not provided'}</p>
                </div>
            </div>
        `;

        // Show doctor-specific actions if user is a doctor
        if (userData.user_type === 'DOCTOR') {
            const doctorActions = document.getElementById('doctorActions');
            if (doctorActions) {
                doctorActions.style.display = 'block';
            }
        }
    } else {
        console.log('No user data available, fetching from server...');
        // If no user data, try to fetch it from the server
        fetchUserDataFromServer();
    }
}

// Function to fetch user data from server if not in localStorage
async function fetchUserDataFromServer() {
    try {
        const token = getAuthToken();
        if (!token) {
            console.log('No auth token, redirecting to login');
            window.location.href = '/login';
            return;
        }

        console.log('Fetching user data from server...');
        const response = await fetch(`${API_BASE_URL}/auth/dashboard`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Server response not OK:', response.status, response.statusText);
            throw new Error(`Failed to fetch user data: ${response.status}`);
        }

        const userData = await response.json();
        console.log('Fetched user data from server:', userData);
        console.log('Profile image in fetched data:', userData.profile_image_filename);

        // Store the user data for future use
        localStorage.setItem('user_data', JSON.stringify(userData));

        // Update the UI
        loadUserInfo();

    } catch (error) {
        console.error('Error fetching user data:', error);

        // Try to load from localStorage as fallback
        const cachedUserData = getUserData();
        if (cachedUserData) {
            console.log('Using cached user data as fallback');
            loadUserInfo();
        } else {
            // If we can't fetch user data and no cache, redirect to login
            console.log('No user data available, redirecting to login');
            window.location.href = '/login';
        }
    }
}

// Utility functions (reuse from login.js)
function getAuthToken() {
    return localStorage.getItem('access_token');
}

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

// Debug function to help test profile image display
function debugUserData() {
    const userData = getUserData();
    console.log('Current user data:', userData);

    if (userData) {
        console.log('Profile image filename:', userData.profile_image_filename);
        console.log('Profile image URL:', userData.profile_image_filename ? `/static/profiles/${userData.profile_image_filename}` : 'No image');

        // Test if the image file exists
        if (userData.profile_image_filename) {
            const img = new Image();
            img.onload = function() {
                console.log('Profile image loaded successfully');
            };
            img.onerror = function() {
                console.error('Failed to load profile image:', `/static/profiles/${userData.profile_image_filename}`);
            };
            img.src = `/static/profiles/${userData.profile_image_filename}`;
        }
    }

    return userData;
}

// Make debug function available globally for testing
window.debugUserData = debugUserData;

// Notification Functions
async function loadNotifications() {
    try {
        const token = getAuthToken();
        if (!token) {
            console.log('No auth token available for notifications');
            return;
        }

        console.log('Loading notifications...');
        const response = await fetch(`${API_BASE_URL}/notifications?limit=5&read_only=true`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Failed to fetch notifications:', response.status);
            if (response.status === 401) {
                console.warn('Authentication failed for notifications. Token may be expired.');
                // Try to refresh user data which will redirect to login if token is invalid
                fetchUserDataFromServer();
            }
            return;
        }

        const notifications = await response.json();
        console.log('Loaded notifications:', notifications);

        // Also get unread count
        const countResponse = await fetch(`${API_BASE_URL}/notifications/unread-count`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        let unreadCount = 0;
        if (countResponse.ok) {
            const countData = await countResponse.json();
            unreadCount = countData.unread_count || 0;
        } else if (countResponse.status === 401) {
            console.warn('Authentication failed for notification count. Token may be expired.');
            // Don't try to refresh here to avoid infinite loops
        }

        displayNotifications(notifications, unreadCount);

    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function displayNotifications(notifications, unreadCount) {
    const notificationsSection = document.getElementById('notificationsSection');
    const notificationsContainer = document.getElementById('notificationsContainer');
    const notificationBadge = document.getElementById('notificationBadge');

    // Filter notifications to only show read ones
    const readNotifications = notifications.filter(notification => notification.is_read === true);

    // Show notifications section if there are read notifications
    if (readNotifications && readNotifications.length > 0) {
        notificationsSection.style.display = 'block';

        // Update badge (for unread count, but we're only showing read notifications)
        if (unreadCount > 0) {
            notificationBadge.textContent = unreadCount;
            notificationBadge.style.display = 'inline-flex';
        } else {
            notificationBadge.style.display = 'none';
        }

        // Display only read notifications with user-friendly messages
        notificationsContainer.innerHTML = readNotifications.map(notification => {
            const date = new Date(notification.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            // Create a user-friendly message with appointment link
            let friendlyMessage = '';
            let appointmentLink = '/appointments';
            let linkText = '📅 View All Appointments';

            if (notification.message) {
                // If notification has a message, use it
                if (notification.user_name && notification.user_email) {
                    friendlyMessage = `✅ Notification from ${notification.user_name} (${notification.user_email}) - ${notification.message}`;
                } else if (notification.user_name) {
                    friendlyMessage = `✅ Notification from ${notification.user_name} - ${notification.message}`;
                } else {
                    friendlyMessage = `✅ ${notification.message}`;
                }

                // Check if this is an appointment-related notification
                if (notification.message.toLowerCase().includes('appointment')) {
                    linkText = '📅 View Appointment Details';
                    // If we have an appointment ID in the notification, we could link to specific appointment
                    if (notification.appointment_id) {
                        appointmentLink = `/appointments/${notification.appointment_id}`;
                        linkText = '📅 View This Appointment';
                    }
                }
            } else {
                // Default notification message for appointment reminders
                if (notification.user_name) {
                    friendlyMessage = `✅ Appointment reminder from ${notification.user_name}`;
                } else {
                    friendlyMessage = `✅ You have an appointment reminder`;
                }
                linkText = '📅 View Your Appointments';
            }

            return `
                <div class="notification-item read-notification">
                    <div class="notification-message">
                        ${friendlyMessage}
                        <div class="notification-actions">
                            <a href="${appointmentLink}" class="appointment-link" onclick="return handleAppointmentLinkClick(event, '${notification.appointment_id}')">
                                ${linkText}
                            </a>
                        </div>
                    </div>
                    <div class="notification-date">${date}</div>
                </div>
            `;
        }).join('');

    } else {
        notificationsContainer.innerHTML = '<div class="notification-empty">No read notifications to display</div>';
        notificationBadge.style.display = 'none';
        notificationsSection.style.display = 'block';
    }
}

function viewAllNotifications() {
    // For now, just reload notifications to show more
    // In the future, this could navigate to a dedicated notifications page
    loadNotifications();
}

// Auto-refresh notifications every 5 minutes
setInterval(() => {
    console.log('Auto-refreshing notifications...');
    loadNotifications();
}, 5 * 60 * 1000); // 5 minutes

// Make notification functions available globally
window.markNotificationAsRead = markNotificationAsRead;
window.markAllAsRead = markAllAsRead;
window.viewAllNotifications = viewAllNotifications;

// Add a helper function to handle appointment link clicks
function handleAppointmentLinkClick(event, appointmentId = null) {
    // You can add analytics tracking here if needed
    console.log('Appointment link clicked', appointmentId ? `for appointment ${appointmentId}` : 'for all appointments');

    // Let the default link behavior happen (navigation)
    return true;
}

// Make the helper function available globally
window.handleAppointmentLinkClick = handleAppointmentLinkClick;
