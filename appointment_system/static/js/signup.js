// API Configuration
const API_BASE_URL = 'http://localhost:8000/api'; // Adjust this to your backend URL

// Global variables
let timeslotCount = 0;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    loadDivisions();
});

// Initialize form event listeners
function initializeForm() {
    const form = document.getElementById('signupForm');
    const userTypeSelect = document.getElementById('userType');
    const divisionSelect = document.getElementById('division');
    const districtSelect = document.getElementById('district');
    const profileImageInput = document.getElementById('profileImage');

    // Form submission
    form.addEventListener('submit', handleFormSubmit);

    // User type change
    userTypeSelect.addEventListener('change', handleUserTypeChange);

    // Location cascading dropdowns
    divisionSelect.addEventListener('change', handleDivisionChange);
    districtSelect.addEventListener('change', handleDistrictChange);

    // Profile image validation
    profileImageInput.addEventListener('change', validateProfileImage);

    // Real-time validation
    setupRealTimeValidation();
}

// Real-time validation setup
function setupRealTimeValidation() {
    const inputs = document.querySelectorAll('input, select');
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
        case 'full_name':
            return validateFullName(value, field);
        case 'email':
            return validateEmail(value, field);
        case 'mobile_number':
            return validateMobileNumber(value, field);
        case 'password':
            return validatePassword(value, field);
        case 'confirm_password':
            return validateConfirmPassword(value, field);
        case 'user_type':
            return validateRequired(value, field, 'Please select a user type');
        case 'division_id':
            return validateRequired(value, field, 'Please select a division');
        case 'district_id':
            return validateRequired(value, field, 'Please select a district');
        case 'thana_id':
            return validateRequired(value, field, 'Please select a thana');
        case 'license_number':
            return validateLicenseNumber(value, field);
        case 'experience_years':
            return validateExperienceYears(value, field);
        case 'consultation_fee':
            return validateConsultationFee(value, field);
        default:
            return true;
    }
}

// Validation functions
function validateFullName(value, field) {
    if (!value) {
        showError(field, 'Full name is required');
        return false;
    }
    if (value.length < 2) {
        showError(field, 'Full name must be at least 2 characters');
        return false;
    }
    if (value.length > 100) {
        showError(field, 'Full name must be less than 100 characters');
        return false;
    }
    return true;
}

function validateEmail(value, field) {
    if (!value) {
        showError(field, 'Email is required');
        return false;
    }
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(value)) {
        showError(field, 'Please enter a valid email address');
        return false;
    }
    return true;
}

function validateMobileNumber(value, field) {
    if (!value) {
        showError(field, 'Mobile number is required');
        return false;
    }
    if (!value.startsWith('+88')) {
        showError(field, 'Mobile number must start with +88');
        return false;
    }
    if (value.length !== 14) {
        showError(field, 'Mobile number must be exactly 14 digits including +88');
        return false;
    }
    if (!/^\+88\d{11}$/.test(value)) {
        showError(field, 'Invalid mobile number format');
        return false;
    }
    return true;
}

function validatePassword(value, field) {
    if (!value) {
        showError(field, 'Password is required');
        return false;
    }

    const errors = [];
    if (value.length < 8) {
        errors.push('at least 8 characters');
    }
    if (!/[A-Z]/.test(value)) {
        errors.push('one uppercase letter');
    }
    if (!/[0-9]/.test(value)) {
        errors.push('one digit');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
        errors.push('one special character');
    }

    if (errors.length > 0) {
        showError(field, `Password must contain: ${errors.join(', ')}`);
        return false;
    }
    return true;
}

function validateConfirmPassword(value, field) {
    const password = document.getElementById('password').value;
    if (!value) {
        showError(field, 'Please confirm your password');
        return false;
    }
    if (value !== password) {
        showError(field, 'Passwords do not match');
        return false;
    }
    return true;
}

function validateLicenseNumber(value, field) {
    const userType = document.getElementById('userType').value;
    if (userType === 'DOCTOR') {
        if (!value) {
            showError(field, 'License number is required for doctors');
            return false;
        }
        if (value.length < 3) {
            showError(field, 'License number must be at least 3 characters');
            return false;
        }
    }
    return true;
}

function validateExperienceYears(value, field) {
    const userType = document.getElementById('userType').value;
    if (userType === 'DOCTOR') {
        if (value === '') {
            showError(field, 'Experience years is required for doctors');
            return false;
        }
        if (parseInt(value) < 0) {
            showError(field, 'Experience years cannot be negative');
            return false;
        }
        if (parseInt(value) > 60) {
            showError(field, 'Experience years seems too high');
            return false;
        }
    }
    return true;
}

function validateConsultationFee(value, field) {
    const userType = document.getElementById('userType').value;
    if (userType === 'DOCTOR') {
        if (value === '') {
            showError(field, 'Consultation fee is required for doctors');
            return false;
        }
        if (parseFloat(value) < 0) {
            showError(field, 'Consultation fee cannot be negative');
            return false;
        }
        if (parseFloat(value) > 10000) {
            showError(field, 'Consultation fee seems too high');
            return false;
        }
    }
    return true;
}

function validateRequired(value, field, message) {
    if (!value) {
        showError(field, message);
        return false;
    }
    return true;
}

function validateProfileImage() {
    const fileInput = document.getElementById('profileImage');
    const file = fileInput.files[0];

    clearError(fileInput);

    if (!file) return true; // Optional field

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
        showError(fileInput, 'Only JPEG and PNG images are allowed');
        fileInput.value = '';
        return false;
    }

    // Check file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        showError(fileInput, 'Image size must be less than 5MB');
        fileInput.value = '';
        return false;
    }

    // Update file upload label
    const label = document.querySelector('.file-upload-text');
    label.textContent = file.name;

    return true;
}

// Error handling functions
function showError(field, message) {
    field.classList.add('error');
    const errorElement = document.getElementById(field.id + 'Error') ||
                        document.getElementById(field.name + 'Error');
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function clearError(field) {
    field.classList.remove('error');
    const errorElement = document.getElementById(field.id + 'Error') ||
                        document.getElementById(field.name + 'Error');
    if (errorElement) {
        errorElement.textContent = '';
    }
}

function clearAllErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.textContent = '';
    });

    const errorFields = document.querySelectorAll('.error');
    errorFields.forEach(field => {
        field.classList.remove('error');
    });
}

// User type change handler
function handleUserTypeChange(event) {
    const userType = event.target.value;
    const doctorSection = document.getElementById('doctorSection');
    const doctorFields = doctorSection.querySelectorAll('input, select');

    if (userType === 'DOCTOR') {
        doctorSection.style.display = 'block';
        doctorFields.forEach(field => {
            if (field.name !== 'profile_image') {
                field.setAttribute('required', 'required');
            }
        });

        // Add initial timeslot if none exist
        if (timeslotCount === 0) {
            addTimeslot();
        }
    } else {
        doctorSection.style.display = 'none';
        doctorFields.forEach(field => {
            field.removeAttribute('required');
            clearError(field);
        });

        // Clear timeslots
        document.getElementById('timeslotsContainer').innerHTML = '';
        timeslotCount = 0;
    }
}

// Location API functions
async function loadDivisions() {
    try {
        const response = await fetch(`${API_BASE_URL}/locations/divisions`);
        if (!response.ok) throw new Error('Failed to load divisions');

        const divisions = await response.json();
        const divisionSelect = document.getElementById('division');

        divisionSelect.innerHTML = '<option value="">Select Division</option>';
        divisions.forEach(division => {
            const option = document.createElement('option');
            option.value = division.id;
            option.textContent = division.name;
            divisionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading divisions:', error);
        showMessage('Failed to load divisions. Please refresh the page.', 'error');
    }
}

async function handleDivisionChange(event) {
    const divisionId = event.target.value;
    const districtSelect = document.getElementById('district');
    const thanaSelect = document.getElementById('thana');

    // Reset dependent dropdowns
    districtSelect.innerHTML = '<option value="">Select District</option>';
    thanaSelect.innerHTML = '<option value="">Select Thana</option>';
    thanaSelect.disabled = true;

    if (!divisionId) {
        districtSelect.disabled = true;
        return;
    }

    try {
        districtSelect.disabled = false;
        districtSelect.innerHTML = '<option value="">Loading districts...</option>';

        const response = await fetch(`${API_BASE_URL}/locations/divisions/${divisionId}/districts`);
        if (!response.ok) throw new Error('Failed to load districts');

        const districts = await response.json();
        districtSelect.innerHTML = '<option value="">Select District</option>';

        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district.id;
            option.textContent = district.name;
            districtSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading districts:', error);
        districtSelect.innerHTML = '<option value="">Error loading districts</option>';
        showMessage('Failed to load districts', 'error');
    }
}

async function handleDistrictChange(event) {
    const districtId = event.target.value;
    const thanaSelect = document.getElementById('thana');

    thanaSelect.innerHTML = '<option value="">Select Thana</option>';

    if (!districtId) {
        thanaSelect.disabled = true;
        return;
    }

    try {
        thanaSelect.disabled = false;
        thanaSelect.innerHTML = '<option value="">Loading thanas...</option>';

        const response = await fetch(`${API_BASE_URL}/locations/districts/${districtId}/thanas`);
        if (!response.ok) throw new Error('Failed to load thanas');

        const thanas = await response.json();
        thanaSelect.innerHTML = '<option value="">Select Thana</option>';

        thanas.forEach(thana => {
            const option = document.createElement('option');
            option.value = thana.id;
            option.textContent = thana.name;
            thanaSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading thanas:', error);
        thanaSelect.innerHTML = '<option value="">Error loading thanas</option>';
        showMessage('Failed to load thanas', 'error');
    }
}

// Timeslot management
function addTimeslot() {
    timeslotCount++;
    const container = document.getElementById('timeslotsContainer');
    const timeslotRow = document.createElement('div');
    timeslotRow.className = 'timeslot-row';
    timeslotRow.id = `timeslot-${timeslotCount}`;

    timeslotRow.innerHTML = `
        <div class="form-group">
            <label for="startTime-${timeslotCount}">Start Time</label>
            <input type="time" id="startTime-${timeslotCount}" name="start_time_${timeslotCount}" required>
        </div>
        <div class="form-group">
            <label for="endTime-${timeslotCount}">End Time</label>
            <input type="time" id="endTime-${timeslotCount}" name="end_time_${timeslotCount}" required>
        </div>
        <button type="button" class="remove-timeslot" onclick="removeTimeslot(${timeslotCount})">Remove</button>
    `;

    container.appendChild(timeslotRow);

    // Add validation for time inputs
    const startTimeInput = timeslotRow.querySelector(`#startTime-${timeslotCount}`);
    const endTimeInput = timeslotRow.querySelector(`#endTime-${timeslotCount}`);

    startTimeInput.addEventListener('change', () => validateTimeslot(timeslotCount));
    endTimeInput.addEventListener('change', () => validateTimeslot(timeslotCount));
}

function removeTimeslot(id) {
    const timeslotRow = document.getElementById(`timeslot-${id}`);
    if (timeslotRow) {
        timeslotRow.remove();
    }

    // Check if any timeslots remain
    const remainingTimeslots = document.querySelectorAll('.timeslot-row');
    if (remainingTimeslots.length === 0 && document.getElementById('userType').value === 'DOCTOR') {
        addTimeslot(); // Ensure at least one timeslot for doctors
    }
}

function validateTimeslot(id) {
    const startTime = document.getElementById(`startTime-${id}`).value;
    const endTime = document.getElementById(`endTime-${id}`).value;

    if (startTime && endTime) {
        if (startTime >= endTime) {
            showMessage('End time must be after start time', 'error');
            return false;
        }
    }
    return true;
}

// Form submission
async function handleFormSubmit(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    // Clear previous errors
    clearAllErrors();

    // Validate all fields
    const form = event.target;
    const formData = new FormData(form);
    let isValid = true;

    // Validate basic fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Validate terms acceptance
    const termsAccepted = document.getElementById('termsAccepted').checked;
    if (!termsAccepted) {
        showError(document.getElementById('termsAccepted'), 'You must accept the terms and conditions');
        isValid = false;
    }

    // Validate doctor-specific fields and timeslots
    const userType = document.getElementById('userType').value;
    if (userType === 'DOCTOR') {
        isValid = validateDoctorFields() && isValid;
    }

    if (!isValid) {
        showMessage('Please correct the errors above', 'error');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    try {
        // Prepare data for submission
        const userData = await prepareUserData(formData);

        // Submit to API
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }

        const result = await response.json();
        showMessage('Account created successfully! Redirecting to login page...', 'success');

        // Redirect to login page after successful submission
        setTimeout(() => {
            window.location.href = '/login?registered=true';
        }, 2000);

    } catch (error) {
        console.error('Registration error:', error);
        showMessage(error.message || 'Registration failed. Please try again.', 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
    }
}

function validateDoctorFields() {
    let isValid = true;

    // Validate timeslots
    const timeslotRows = document.querySelectorAll('.timeslot-row');
    if (timeslotRows.length === 0) {
        showError(document.getElementById('timeslotsContainer'), 'At least one timeslot is required for doctors');
        isValid = false;
    } else {
        timeslotRows.forEach(row => {
            const id = row.id.split('-')[1];
            if (!validateTimeslot(id)) {
                isValid = false;
            }
        });
    }

    return isValid;
}

async function prepareUserData(formData) {
    const userData = {
        full_name: formData.get('full_name'),
        email: formData.get('email'),
        mobile_number: formData.get('mobile_number'),
        password: formData.get('password'),
        user_type: formData.get('user_type'),
        division_id: parseInt(formData.get('division_id')),
        district_id: parseInt(formData.get('district_id')),
        thana_id: parseInt(formData.get('thana_id'))
    };

    // Handle profile image
    const profileImageFile = formData.get('profile_image');
    if (profileImageFile && profileImageFile.size > 0) {
        userData.profile_image_base64 = await fileToBase64(profileImageFile);
        userData.profile_image_filename = profileImageFile.name;
    }

    // Handle doctor profile
    if (userData.user_type === 'DOCTOR') {
        const timeslots = [];
        const timeslotRows = document.querySelectorAll('.timeslot-row');

        timeslotRows.forEach(row => {
            const id = row.id.split('-')[1];
            const startTime = document.getElementById(`startTime-${id}`).value;
            const endTime = document.getElementById(`endTime-${id}`).value;

            if (startTime && endTime) {
                timeslots.push({
                    start_time: startTime,
                    end_time: endTime,
                    is_available: true
                });
            }
        });

        userData.doctor_profile = {
            license_number: formData.get('license_number'),
            experience_years: parseInt(formData.get('experience_years')),
            consultation_fee: parseFloat(formData.get('consultation_fee')),
            available_timeslots: timeslots
        };
    }

    return userData;
}

// Utility functions
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            // Remove the data:image/...;base64, prefix
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = error => reject(error);
    });
}

function togglePassword() {
    const passwordField = document.getElementById('password');
    const toggleBtn = document.querySelector('.toggle-password');

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleBtn.textContent = '🙈';
    } else {
        passwordField.type = 'password';
        toggleBtn.textContent = '👁️';
    }
}

function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('messageContainer');
    const messageContent = document.getElementById('messageContent');
    const messageText = document.getElementById('messageText');

    messageText.textContent = message;
    messageContent.className = `message-content ${type}`;
    messageContainer.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeMessage();
    }, 5000);
}

function closeMessage() {
    const messageContainer = document.getElementById('messageContainer');
    messageContainer.style.display = 'none';
}
