# Patient Appointment Booking System

## Overview

This comprehensive appointment booking system provides a robust solution for managing patient-doctor appointments with the following key features:

### Core Features

1. **Doctor Selection**: Patients can choose from available doctors with detailed profiles
2. **Date & Time Selection**: Smart scheduling with real-time availability checking
3. **Notes/Symptoms**: Optional field for patient notes and symptoms
4. **Status Management**: Complete appointment lifecycle management
5. **Validation**: Prevents double-booking and ensures data integrity
6. **Extensible Design**: Clean architecture following SOLID principles

## Database Schema

### Appointment Model
```python
class Appointment(Base):
    id: int (Primary Key)
    patient_id: int (Foreign Key to User)
    doctor_id: int (Foreign Key to DoctorProfile)
    appointment_date: date
    appointment_time: time
    notes: text (Optional)
    status: AppointmentStatus (PENDING, CONFIRMED, CANCELLED, COMPLETED)
    created_at: datetime
    updated_at: datetime
```

### Appointment Status Enum
- **PENDING**: Initial status when appointment is created
- **CONFIRMED**: Doctor has confirmed the appointment
- **CANCELLED**: Appointment has been cancelled by patient or doctor
- **COMPLETED**: Appointment has been completed

## API Endpoints

### 1. Create Appointment
**POST** `/api/appointments/`

**Request Body:**
```json
{
    "doctor_id": 1,
    "appointment_date": "2025-07-15",
    "appointment_time": "10:00:00",
    "notes": "Experiencing headaches for the past week"
}
```

**Response:**
```json
{
    "id": 1,
    "patient_id": 2,
    "doctor_id": 1,
    "appointment_date": "2025-07-15",
    "appointment_time": "10:00:00",
    "notes": "Experiencing headaches for the past week",
    "status": "PENDING",
    "created_at": "2025-07-12T10:30:00Z",
    "updated_at": "2025-07-12T10:30:00Z",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "patient_mobile": "+8801234567890",
    "doctor_name": "Dr. Jane Smith",
    "doctor_license": "MD12345",
    "consultation_fee": 100.0
}
```

### 2. Get Appointments
**GET** `/api/appointments/`

**Query Parameters:**
- `skip`: int (default: 0) - Pagination offset
- `limit`: int (default: 100) - Pagination limit
- `status`: AppointmentStatus (optional) - Filter by status
- `date_from`: date (optional) - Filter appointments from date
- `date_to`: date (optional) - Filter appointments to date

**Response:**
```json
[
    {
        "id": 1,
        "patient_id": 2,
        "doctor_id": 1,
        // ... appointment details
    }
]
```

### 3. Get Single Appointment
**GET** `/api/appointments/{appointment_id}`

### 4. Update Appointment
**PUT** `/api/appointments/{appointment_id}`

**Request Body:**
```json
{
    "appointment_date": "2025-07-16",
    "appointment_time": "11:00:00",
    "notes": "Updated symptoms description",
    "status": "CONFIRMED"
}
```

### 5. Cancel Appointment
**DELETE** `/api/appointments/{appointment_id}`

### 6. Get Doctor Availability
**GET** `/api/appointments/doctors/{doctor_id}/availability?appointment_date=2025-07-15`

**Response:**
```json
{
    "doctor_id": 1,
    "date": "2025-07-15",
    "available_slots": [
        {"time": "09:00", "available": true},
        {"time": "09:30", "available": true},
        {"time": "10:00", "available": false},
        {"time": "10:30", "available": true}
    ]
}
```

### 7. Confirm Appointment (Doctor Only)
**POST** `/api/appointments/{appointment_id}/confirm`

### 8. Complete Appointment (Doctor Only)
**POST** `/api/appointments/{appointment_id}/complete`

### 9. Get Appointment Statistics
**GET** `/api/appointments/stats/summary`

## Business Logic & Validation

### 1. Doctor Availability Validation
```python
def _is_doctor_available(db: Session, doctor_id: int, appointment_date: date, appointment_time: time) -> bool:
    """
    Validates that the requested time falls within doctor's available time slots
    """
    # Implementation checks DoctorTimeslot table for availability
```

### 2. Double Booking Prevention
```python
def _has_conflicting_appointment(db: Session, doctor_id: int, appointment_date: date, appointment_time: time) -> bool:
    """
    Prevents booking appointments at times that are already taken
    """
    # Implementation checks for existing appointments at the same time
```

### 3. Permission Management
- **Patients**: Can create, view their own appointments, update details, and cancel
- **Doctors**: Can view their appointments, update status (confirm/complete), and cancel
- **Admins**: Full access to all appointments

## Frontend Interface

### Appointment Booking Page (`/appointments`)

The system includes a modern, responsive web interface with:

1. **Doctor Selection Dropdown**: Lists all available doctors with their details
2. **Date Picker**: Prevents selection of past dates
3. **Dynamic Time Slot Grid**: Shows available times based on doctor and date selection
4. **Notes Field**: Optional textarea for symptoms/notes
5. **Real-time Validation**: Immediate feedback on availability

### Key JavaScript Features

1. **Real-time Availability**: Fetches and displays available time slots dynamically
2. **Form Validation**: Client-side validation before submission
3. **Error Handling**: User-friendly error messages
4. **Appointment Management**: View, cancel, and reschedule appointments

## Security Features

1. **JWT Authentication**: All endpoints require valid authentication tokens
2. **Role-based Access Control**: Different permissions for patients, doctors, and admins
3. **Data Validation**: Server-side validation for all inputs
4. **SQL Injection Prevention**: Using SQLAlchemy ORM with parameterized queries

## Extensibility Features

### 1. Service Layer Pattern
The `AppointmentService` class encapsulates all business logic, making it easy to:
- Add new appointment types
- Implement complex scheduling rules
- Add notification systems
- Integrate with external calendars

### 2. Schema Flexibility
The Pydantic schemas support:
- Easy addition of new fields
- Validation rule modifications
- API versioning

### 3. Database Design
The normalized database structure allows for:
- Adding appointment types
- Implementing recurring appointments
- Adding reminder systems
- Integrating with payment systems

## Error Handling

### Common Error Responses

1. **Doctor Not Found** (404):
```json
{"detail": "Doctor not found"}
```

2. **Time Slot Not Available** (400):
```json
{"detail": "Doctor is not available at the selected time slot"}
```

3. **Double Booking** (400):
```json
{"detail": "Time slot is already booked"}
```

4. **Unauthorized Access** (403):
```json
{"detail": "Not authorized to update this appointment"}
```

## Testing

The system includes comprehensive test coverage:

1. **Unit Tests**: Service layer validation
2. **Integration Tests**: API endpoint testing
3. **End-to-End Tests**: Complete workflow validation

### Running Tests
```bash
python test_appointment_system.py
```

## Performance Considerations

1. **Database Indexing**: Proper indexes on date, time, and foreign keys
2. **Query Optimization**: Efficient joins and filtering
3. **Caching**: Redis can be added for availability caching
4. **Pagination**: All list endpoints support pagination

## Future Enhancements

1. **Notification System**: Email/SMS reminders and confirmations
2. **Recurring Appointments**: Support for regular check-ups
3. **Telemedicine Integration**: Video call scheduling
4. **Payment Integration**: Online payment for consultations
5. **Calendar Sync**: Integration with Google Calendar, Outlook
6. **Mobile App**: React Native or Flutter mobile application
7. **Analytics Dashboard**: Appointment analytics and reporting

## Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run Database Migrations**:
```bash
# Database tables are created automatically on startup
```

3. **Start the Server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the Application**:
- API Documentation: http://localhost:8000/docs
- Appointment Booking: http://localhost:8000/appointments

## Architecture Principles

This implementation follows several key design principles:

1. **Single Responsibility**: Each class/module has a single, well-defined purpose
2. **Open/Closed**: Easy to extend functionality without modifying existing code
3. **Dependency Inversion**: High-level modules don't depend on low-level modules
4. **Clean Architecture**: Separation of concerns between layers
5. **RESTful Design**: Standard HTTP methods and status codes

The appointment booking system is production-ready and can scale to handle thousands of concurrent users with proper infrastructure setup.
