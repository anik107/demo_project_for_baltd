// Appointment Management JavaScript

class AppointmentManager {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.selectedTimeSlot = null;

        // Debug token
        console.log('AppointmentManager initialized');
        console.log('Token from localStorage:', this.token ? 'Present' : 'Missing');

        if (!this.token) {
            console.warn('No authentication token found');
            this.showMessage('Please log in to book appointments', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }

        this.init();
    }

    init() {
        this.loadDoctors();
        this.setupEventListeners();
        this.setMinDate();
    }

    setupEventListeners() {
        const form = document.getElementById('appointmentForm');
        const doctorSelect = document.getElementById('doctorSelect');
        const dateInput = document.getElementById('appointmentDate');

        form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        doctorSelect.addEventListener('change', () => this.loadTimeSlots());
        dateInput.addEventListener('change', () => this.loadTimeSlots());
    }

    setMinDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('appointmentDate').min = today;
    }

    async loadDoctors() {
        if (!this.token) {
            this.showMessage('Authentication required to load doctors', 'error');
            return;
        }

        try {
            console.log('Loading doctors...');
            const response = await fetch('/api/doctors/', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            console.log('Doctors response status:', response.status);

            if (response.status === 401) {
                // Token is invalid or expired
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_data');
                this.showMessage('Session expired. Please log in again.', 'error');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                return;
            }

            if (!response.ok) {
                throw new Error('Failed to load doctors');
            }

            const doctors = await response.json();
            console.log('Loaded doctors:', doctors.length);
            const select = document.getElementById('doctorSelect');

            select.innerHTML = '<option value="">Choose a doctor...</option>';

            doctors.forEach(doctor => {
                if (doctor.doctor_profile) {
                    const option = document.createElement('option');
                    option.value = doctor.doctor_profile.id;
                    option.textContent = `Dr. ${doctor.full_name} - ${doctor.doctor_profile.license_number} ($${doctor.doctor_profile.consultation_fee})`;
                    select.appendChild(option);
                }
            });
        } catch (error) {
            console.error('Error loading doctors:', error);
            this.showMessage('Error loading doctors: ' + error.message, 'error');
        }
    }

    async loadTimeSlots() {
        const doctorId = document.getElementById('doctorSelect').value;
        const date = document.getElementById('appointmentDate').value;
        const slotsContainer = document.getElementById('timeSlots');

        if (!doctorId || !date) {
            slotsContainer.innerHTML = '<p>Please select a doctor and date first</p>';
            return;
        }

        // Check if token exists
        if (!this.token) {
            slotsContainer.innerHTML = '<p>Authentication required. Please log in again.</p>';
            this.showMessage('Please log in to view available time slots', 'error');
            return;
        }

        try {
            slotsContainer.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <p>Loading available time slots...</p>
                </div>
            `;

            console.log('Making request with token:', this.token ? 'Token present' : 'No token');
            console.log('Request URL:', `/api/appointments/doctors/${doctorId}/availability?appointment_date=${date}`);

            const response = await fetch(`/api/appointments/doctors/${doctorId}/availability?appointment_date=${date}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));

            if (response.status === 401) {
                // Token is invalid or expired
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_data');
                slotsContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-lock"></i>
                        <h3>Session Expired</h3>
                        <p>Please log in again to view available time slots.</p>
                    </div>
                `;
                this.showMessage('Session expired. Please log in again.', 'error');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                return;
            }

            if (!response.ok) {
                const errorText = await response.text();
                console.log('Error response:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Availability data:', data);
            this.renderTimeSlots(data.available_slots);

        } catch (error) {
            console.error('Error loading time slots:', error);
            slotsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error Loading Slots</h3>
                    <p>Unable to load time slots. Please try again.</p>
                </div>
            `;
            this.showMessage('Error loading time slots: ' + error.message, 'error');
        }
    }

    renderTimeSlots(slots) {
        const container = document.getElementById('timeSlots');

        if (slots.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Available Slots</h3>
                    <p>No available time slots for this date. Please try another date.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        slots.forEach(slot => {
            const slotElement = document.createElement('div');
            slotElement.className = 'time-slot available';
            slotElement.innerHTML = `
                <i class="fas fa-clock"></i>
                <span>${slot.time}</span>
            `;
            slotElement.addEventListener('click', () => this.selectTimeSlot(slotElement, slot.time));
            container.appendChild(slotElement);
        });
    }

    selectTimeSlot(element, time) {
        // Remove previous selection
        document.querySelectorAll('.time-slot.selected').forEach(slot => {
            slot.classList.remove('selected');
        });

        // Select new slot
        element.classList.add('selected');
        this.selectedTimeSlot = time;
        document.getElementById('selectedTime').value = time;
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        if (!this.selectedTimeSlot) {
            this.showMessage('Please select a time slot', 'error');
            return;
        }

        const formData = {
            doctor_id: parseInt(document.getElementById('doctorSelect').value),
            appointment_date: document.getElementById('appointmentDate').value,
            appointment_time: this.selectedTimeSlot,
            notes: document.getElementById('notes').value || null
        };

        try {
            const response = await fetch('/api/appointments/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                let errorMessage = 'Failed to book appointment';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || errorMessage;
                } catch (jsonError) {
                    // If response is not JSON, use status text or default message
                    errorMessage = response.statusText || `Server error (${response.status})`;
                }
                throw new Error(errorMessage);
            }

            const appointment = await response.json();
            this.showMessage('Appointment booked successfully!', 'success');

            // Reset form
            document.getElementById('appointmentForm').reset();
            this.selectedTimeSlot = null;
            document.getElementById('timeSlots').innerHTML = '<p>Please select a doctor and date first</p>';

            // Refresh appointments list if visible
            if (document.getElementById('appointments').style.display !== 'none') {
                this.loadAppointments();
            }

        } catch (error) {
            this.showMessage('Error booking appointment: ' + error.message, 'error');
        }
    }

    async loadAppointments() {
        const container = document.getElementById('appointmentsList');

        try {
            container.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <p>Loading your appointments...</p>
                </div>
            `;

            const response = await fetch('/api/appointments/', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load appointments');
            }

            const appointments = await response.json();
            this.renderAppointments(appointments);

        } catch (error) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error Loading Appointments</h3>
                    <p>Unable to load your appointments. Please try again.</p>
                </div>
            `;
            this.showMessage('Error loading appointments: ' + error.message, 'error');
        }
    }

    renderAppointments(appointments) {
        const container = document.getElementById('appointmentsList');

        if (appointments.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Appointments Found</h3>
                    <p>You haven't booked any appointments yet. Book your first appointment now!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        appointments.forEach(appointment => {
            const card = document.createElement('div');
            card.className = 'appointment-card';

            const statusClass = `status-${appointment.status.toLowerCase()}`;
            const formattedDate = new Date(appointment.appointment_date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            const formattedTime = appointment.appointment_time;

            card.innerHTML = `
                <div class="appointment-header">
                    <div class="doctor-info">
                        <h3><i class="fas fa-user-md"></i> Dr. ${appointment.doctor_name || 'Unknown'}</h3>
                    </div>
                    <span class="appointment-status ${statusClass}">
                        ${this.getStatusIcon(appointment.status)} ${appointment.status}
                    </span>
                </div>

                <div class="appointment-details">
                    <div class="detail-item">
                        <i class="fas fa-calendar-alt"></i>
                        <span><strong>Date:</strong> ${formattedDate}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-clock"></i>
                        <span><strong>Time:</strong> ${formattedTime}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-id-badge"></i>
                        <span><strong>License:</strong> ${appointment.doctor_license || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-dollar-sign"></i>
                        <span><strong>Fee:</strong> $${appointment.consultation_fee || 'N/A'}</span>
                    </div>
                </div>

                ${appointment.notes ? `
                    <div class="appointment-notes">
                        <div class="detail-item">
                            <i class="fas fa-notes-medical"></i>
                            <span><strong>Notes:</strong> ${appointment.notes}</span>
                        </div>
                    </div>
                ` : ''}

                <div class="appointment-actions">
                    ${this.renderAppointmentActions(appointment)}
                </div>
            `;

            container.appendChild(card);
        });
    }

    getStatusIcon(status) {
        const icons = {
            'PENDING': '<i class="fas fa-hourglass-half"></i>',
            'CONFIRMED': '<i class="fas fa-check-circle"></i>',
            'CANCELLED': '<i class="fas fa-times-circle"></i>',
            'COMPLETED': '<i class="fas fa-check-double"></i>'
        };
        return icons[status] || '<i class="fas fa-question-circle"></i>';
    }

    renderAppointmentActions(appointment) {
        const canCancel = appointment.status === 'PENDING' || appointment.status === 'CONFIRMED';
        const canReschedule = appointment.status === 'PENDING';

        let actions = '';

        if (canCancel) {
            actions += `
                <button onclick="appointmentManager.cancelAppointment(${appointment.id})" class="btn-action btn-cancel">
                    <i class="fas fa-times"></i> Cancel
                </button>
            `;
        }

        if (canReschedule) {
            actions += `
                <button onclick="appointmentManager.rescheduleAppointment(${appointment.id})" class="btn-action btn-reschedule">
                    <i class="fas fa-calendar-alt"></i> Reschedule
                </button>
            `;
        }

        return actions;
    }

    async cancelAppointment(appointmentId) {
        if (!confirm('Are you sure you want to cancel this appointment?')) {
            return;
        }

        try {
            const response = await fetch(`/api/appointments/${appointmentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to cancel appointment');
            }

            this.showMessage('Appointment cancelled successfully', 'success');
            this.loadAppointments();

        } catch (error) {
            this.showMessage('Error cancelling appointment: ' + error.message, 'error');
        }
    }

    rescheduleAppointment(appointmentId) {
        // Switch to booking tab and pre-fill for rescheduling
        showTab('booking');
        this.showMessage('Please select new date and time for rescheduling', 'info');
        // Store the appointment ID for rescheduling
        this.reschedulingAppointmentId = appointmentId;
    }

    showMessage(message, type) {
        const messageArea = document.getElementById('messageArea');
        const iconMap = {
            'error': 'fas fa-exclamation-triangle',
            'success': 'fas fa-check-circle',
            'info': 'fas fa-info-circle'
        };

        messageArea.innerHTML = `
            <div class="message ${type}">
                <i class="${iconMap[type] || 'fas fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageArea.innerHTML = '';
        }, 5000);
    }
}

// Tab functionality
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });

    // Remove active class from all sidebar items
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).style.display = 'block';

    // Update page title and activate sidebar item
    if (tabName === 'booking') {
        document.getElementById('page-title').textContent = 'Book New Appointment';
        document.getElementById('book-sidebar').classList.add('active');
    } else if (tabName === 'appointments') {
        document.getElementById('page-title').textContent = 'My Appointments';
        document.getElementById('appointments-sidebar').classList.add('active');
        // Load appointments when switching to appointments tab
        if (typeof appointmentManager !== 'undefined') {
            appointmentManager.loadAppointments();
        }
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}

// Initialize when page loads
let appointmentManager;

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    appointmentManager = new AppointmentManager();
});
