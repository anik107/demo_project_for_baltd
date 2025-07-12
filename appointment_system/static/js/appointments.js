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
            slotsContainer.innerHTML = '<p>Loading available time slots...</p>';

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
                slotsContainer.innerHTML = '<p>Session expired. Please log in again.</p>';
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
            slotsContainer.innerHTML = '<p>Error loading time slots</p>';
            this.showMessage('Error loading time slots: ' + error.message, 'error');
        }
    }

    renderTimeSlots(slots) {
        const container = document.getElementById('timeSlots');

        if (slots.length === 0) {
            container.innerHTML = '<p>No available time slots for this date</p>';
            return;
        }

        container.innerHTML = '';

        slots.forEach(slot => {
            const slotElement = document.createElement('div');
            slotElement.className = 'time-slot available';
            slotElement.textContent = slot.time;
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
            container.innerHTML = '<div class="loading">Loading appointments...</div>';

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
            container.innerHTML = '<p>Error loading appointments</p>';
            this.showMessage('Error loading appointments: ' + error.message, 'error');
        }
    }

    renderAppointments(appointments) {
        const container = document.getElementById('appointmentsList');

        if (appointments.length === 0) {
            container.innerHTML = '<p>No appointments found</p>';
            return;
        }

        container.innerHTML = '';

        appointments.forEach(appointment => {
            const card = document.createElement('div');
            card.className = 'appointment-card';

            const statusClass = `status-${appointment.status.toLowerCase()}`;
            const formattedDate = new Date(appointment.appointment_date).toLocaleDateString();
            const formattedTime = appointment.appointment_time;

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <h3>Dr. ${appointment.doctor_name || 'Unknown'}</h3>
                    <span class="appointment-status ${statusClass}">${appointment.status}</span>
                </div>
                <p><strong>Date:</strong> ${formattedDate}</p>
                <p><strong>Time:</strong> ${formattedTime}</p>
                <p><strong>License:</strong> ${appointment.doctor_license || 'N/A'}</p>
                <p><strong>Fee:</strong> $${appointment.consultation_fee || 'N/A'}</p>
                ${appointment.notes ? `<p><strong>Notes:</strong> ${appointment.notes}</p>` : ''}
                <div style="margin-top: 1rem;">
                    ${this.renderAppointmentActions(appointment)}
                </div>
            `;

            container.appendChild(card);
        });
    }

    renderAppointmentActions(appointment) {
        const canCancel = appointment.status === 'PENDING' || appointment.status === 'CONFIRMED';
        const canReschedule = appointment.status === 'PENDING';

        let actions = '';

        if (canCancel) {
            actions += `<button onclick="appointmentManager.cancelAppointment(${appointment.id})"
                        style="background-color: #dc3545; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; margin-right: 0.5rem; cursor: pointer;">
                        Cancel
                      </button>`;
        }

        if (canReschedule) {
            actions += `<button onclick="appointmentManager.rescheduleAppointment(${appointment.id})"
                        style="background-color: #ffc107; color: black; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                        Reschedule
                      </button>`;
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
        messageArea.innerHTML = `<div class="${type}">${message}</div>`;

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

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).style.display = 'block';

    // Add active class to clicked button
    event.target.classList.add('active');

    // Load appointments when switching to appointments tab
    if (tabName === 'appointments') {
        appointmentManager.loadAppointments();
    }
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

// Add CSS for tabs
const style = document.createElement('style');
style.textContent = `
    .tabs {
        display: flex;
        margin-bottom: 2rem;
        border-bottom: 1px solid #ddd;
    }

    .tab-button {
        background: none;
        border: none;
        padding: 1rem 2rem;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.3s;
    }

    .tab-button:hover {
        background-color: #f8f9fa;
    }

    .tab-button.active {
        border-bottom-color: #007bff;
        color: #007bff;
        font-weight: bold;
    }

    .tab-content {
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);
