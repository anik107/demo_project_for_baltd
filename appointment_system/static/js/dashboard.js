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

        // Check if token is expired before making request
        if (isTokenExpired(token)) {
            console.log('Token is expired, clearing storage and redirecting to login');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
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

            // Handle 401 Unauthorized - token expired or invalid
            if (response.status === 401) {
                console.log('Token expired or invalid, clearing storage and redirecting to login');
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_data');
                window.location.href = '/login';
                return;
            }

            throw new Error(`Failed to fetch user data: ${response.status}`);
        }

        const userData = await response.json();
        console.log('Fetched user data from server:', userData);
        console.log('Profile image in fetched data:', userData.profile_image_filename);
        const userAppointments = await fetch(`${API_BASE_URL}/auth/appointments_count`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (!userAppointments.ok) {
            console.error('Failed to fetch user appointments:', userAppointments.status, userAppointments.statusText);

            // Handle 401 for appointments endpoint too
            if (userAppointments.status === 401) {
                console.log('Token expired during appointments fetch, clearing storage and redirecting to login');
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_data');
                window.location.href = '/login';
                return;
            }

            throw new Error(`Failed to fetch user appointments: ${userAppointments.status}`);
        }
        const appointmentsData = await userAppointments.json();
        console.log('Fetched user appointments:', appointmentsData);
        document.getElementById('user-appointments').textContent = appointmentsData.appointments_count || '0';
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

// Utility function to check if token is expired
function isTokenExpired(token) {
    if (!token) return true;

    try {
        // JWT tokens have 3 parts separated by dots
        const parts = token.split('.');
        if (parts.length !== 3) return true;

        // Decode the payload (second part)
        const payload = JSON.parse(atob(parts[1]));

        // Check if token has expired (exp is in seconds, Date.now() is in milliseconds)
        const now = Math.floor(Date.now() / 1000);
        return payload.exp < now;
    } catch (error) {
        console.error('Error checking token expiration:', error);
        return true; // Assume expired if we can't parse it
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
    const token = getAuthToken();
    if (!token) return false;

    // Check if token is expired
    if (isTokenExpired(token)) {
        console.log('Token is expired, clearing storage');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        return false;
    }

    return true;
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
        const response = await fetch(`${API_BASE_URL}/notifications?limit=5&read_only=false`, {
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
        const notificationCount = notifications.length || 0;
        document.getElementById('notification-count').textContent = notificationCount || '0';
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
    const notificationsContainer = document.getElementById('notificationsContainer');
    const notificationBadge = document.getElementById('notificationBadge');

    // Update badge for unread count
    if (unreadCount > 0) {
        notificationBadge.textContent = unreadCount;
        notificationBadge.style.display = 'inline-flex';
    } else {
        notificationBadge.style.display = 'none';
    }

    // Display all notifications in the panel
    if (notifications && notifications.length > 0) {
        notificationsContainer.innerHTML = notifications.map(notification => {
            const date = new Date(notification.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            // Create a user-friendly message with appointment link
            let friendlyMessage = '';
            let appointmentLink = '/appointments';
            let linkText = '📅 View Appointments';

            if (notification.message) {
                // Parse the notification message to create user-friendly content
                if (notification.message.includes('appointment')) {
                    if (notification.message.includes('confirmed')) {
                        friendlyMessage = '✅ Your appointment has been confirmed';
                    } else if (notification.message.includes('cancelled')) {
                        friendlyMessage = '❌ An appointment has been cancelled';
                    } else if (notification.message.includes('reminder')) {
                        friendlyMessage = '⏰ Appointment reminder';
                    } else if (notification.message.includes('scheduled')) {
                        friendlyMessage = '📅 New appointment scheduled';
                    } else {
                        friendlyMessage = notification.message;
                    }
                } else {
                    friendlyMessage = notification.message;
                }
            } else {
                friendlyMessage = 'You have a new notification';
            }

            return `
                <div class="notification-item ${!notification.is_read ? 'unread' : ''}" data-id="${notification.id}">
                    <div class="notification-message">${friendlyMessage}</div>
                    <div class="notification-actions-item">
                        <span class="notification-date">${date}</span>
                        <div>
                            <a href="${appointmentLink}" class="notification-link" onclick="handleAppointmentLinkClick(event, ${notification.appointment_id || 'null'})">${linkText}</a>
                            ${!notification.is_read ? `<button class="btn btn-sm btn-outline-primary ms-2" onclick="markNotificationAsRead(${notification.id})">Mark Read</button>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        notificationsContainer.innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-bell-slash"></i>
                <div>No notifications to display</div>
            </div>
        `;
    }

    // Update the notification count display
    const totalCount = notifications ? notifications.length : 0;
    document.getElementById('notification-count').textContent = totalCount || '0';
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

// Notification Panel Functions
function toggleNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    if (panel.style.display === 'none' || !panel.style.display) {
        openNotificationPanel();
    } else {
        closeNotificationPanel();
    }
}

function openNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    panel.style.display = 'block';

    // Load all notifications (both read and unread) for the panel
    loadAllNotificationsForPanel();
}

function closeNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    panel.style.display = 'none';
}

async function loadAllNotificationsForPanel() {
    try {
        const token = getAuthToken();
        if (!token) {
            console.log('No auth token available for notifications panel');
            return;
        }

        console.log('Loading all notifications for panel...');

        // Load all notifications (not just read ones)
        const response = await fetch(`${API_BASE_URL}/notifications?limit=20&read_only=false`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Failed to fetch notifications for panel:', response.status);
            document.getElementById('notificationsContainer').innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>Failed to load notifications</div>
                </div>
            `;
            return;
        }

        const notifications = await response.json();

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
        }

        displayNotifications(notifications, unreadCount);

    } catch (error) {
        console.error('Error loading notifications for panel:', error);
        document.getElementById('notificationsContainer').innerHTML = `
            <div class="notification-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <div>Error loading notifications</div>
            </div>
        `;
    }
}

async function markNotificationAsRead(notificationId) {
    try {
        const token = getAuthToken();
        if (!token) {
            console.log('No auth token available');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            console.log('Notification marked as read');
            // Refresh the notifications in the panel
            loadAllNotificationsForPanel();
            // Also refresh the dashboard notifications
            loadNotifications();
        } else {
            console.error('Failed to mark notification as read:', response.status);
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function markAllAsRead() {
    try {
        const token = getAuthToken();
        if (!token) {
            console.log('No auth token available');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/notifications/mark-all-read`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            console.log('All notifications marked as read');
            // Refresh the notifications in the panel
            loadAllNotificationsForPanel();
            // Also refresh the dashboard notifications
            loadNotifications();
        } else {
            console.error('Failed to mark all notifications as read:', response.status);
        }
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
    }
}

function refreshNotifications() {
    loadAllNotificationsForPanel();
    loadNotifications();
}

// Make notification panel functions available globally
window.toggleNotificationPanel = toggleNotificationPanel;
window.openNotificationPanel = openNotificationPanel;
window.closeNotificationPanel = closeNotificationPanel;
window.markNotificationAsRead = markNotificationAsRead;
window.markAllAsRead = markAllAsRead;
window.refreshNotifications = refreshNotifications;
