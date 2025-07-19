# 🏥 Appointment System

A comprehensive **FastAPI-based appointment booking system** designed for healthcare management. The system supports three user types: **Patients**, **Doctors**, and **Admins**, with location-based services for Bangladesh.

## ✨ Features

### 👥 User Management
- **Multi-role authentication** (Patient, Doctor, Admin)
- **User registration and login** with JWT token authentication
- **Profile management** with image upload support
- **Location-based registration** (Division → District → Thana)

### 🩺 Doctor Features
- **Doctor profiles** with license numbers and experience
- **Consultation fee management**
- **Available time slots** configuration
- **Appointment management**

### 📅 Appointment System
- **Book appointments** with doctors
- **Multiple appointment statuses** (Pending, Confirmed, Cancelled, Completed)
- **Date and time scheduling**
- **Notes and symptoms** tracking

### 👨‍💼 Admin Panel
- **Complete doctor management** (create, edit, delete)
- **Appointment oversight** and status updates
- **Monthly reports** with earnings and statistics
- **User management** across all roles

### 🔔 Notifications
- **System notifications** for users
- **Real-time updates** on appointment status

### 🌍 Location Services
- **Bangladesh location hierarchy** (Divisions, Districts, Thanas)
- **Location-based doctor search**

## 🏗️ Project Structure

```
appointment_system/
├── main.py                    # FastAPI application entry point
├── models.py                  # SQLAlchemy database models
├── schemas.py                 # Pydantic validation schemas
├── database.py                # Database configuration and connection
├── auth_utils.py              # JWT authentication utilities
├── user_service.py            # User business logic
├── appointment_service.py     # Appointment business logic
├── notification_service.py    # Notification system
├── location_utils.py          # Bangladesh location data seeding
├── requirements.txt           # Python dependencies
├── routers/                   # API route handlers
│   ├── auth.py               # Authentication endpoints
│   ├── users.py              # User management
│   ├── doctors.py            # Doctor-specific endpoints
│   ├── appointments.py       # Appointment booking
│   ├── admin.py              # Admin panel routes
│   ├── locations.py          # Location services
│   ├── notifications.py      # Notification endpoints
│   └── general.py            # Web page routes
├── templates/                 # HTML templates (Jinja2)
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── appointments.html
│   ├── admin_*.html          # Admin panel templates
│   └── ...
└── static/                   # Static assets
    ├── css/style.css
    ├── js/                   # JavaScript files
    └── profiles/             # User profile images
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone git@github.com:anik107/demo_project_for_baltd.git
   cd demo_project_for_baltd
   ```

2. **Start with Docker:**
   ```bash
   docker compose up --build
   ```

3. **Access the application:**
   - **Main App**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Admin Panel**: http://localhost:8000/admin/login
   - **Database**: localhost:5433 (postgres/postgres)

### Option 2: Local Development

1. **Clone and setup:**
   ```bash
   git clone git@github.com:anik107/demo_project_for_baltd.git
   cd demo_project_for_baltd
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd appointment_system
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🌐 Application Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Main Application** | http://localhost:8000 | Patient/Doctor interface |
| **Admin Panel** | http://localhost:8000/admin | Admin dashboard |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Alternative API Docs** | http://localhost:8000/redoc | ReDoc API documentation |

## 👨‍⚕️ User Roles & Capabilities

### 🧑‍🤝‍🧑 Patients
- Register and manage profile
- Search and book appointments with doctors
- View appointment history
- Receive notifications
- Upload profile pictures

### 👩‍⚕️ Doctors
- Manage professional profile (license, experience, fees)
- Set available time slots
- View and manage appointments
- Update appointment status
- Profile management

### 👨‍💼 Admins
- **Complete system oversight**
- Create, edit, and delete doctor profiles
- Manage all appointments
- Generate monthly reports
- View system statistics
- User management across all roles

## 📊 Database Schema

The system uses **PostgreSQL** with the following main entities:

- **Users** (patients, doctors, admins)
- **DoctorProfiles** (professional information)
- **Appointments** (booking system)
- **DoctorTimeslots** (availability)
- **Locations** (Bangladesh hierarchy)
- **Notifications** (system alerts)
- **TokenBlacklist** (security)

## 🔐 Authentication & Security

- **JWT-based authentication** with secure token handling
- **Password hashing** using secure algorithms
- **Role-based access control** (RBAC)
- **Token blacklisting** for logout security
- **CORS protection** and middleware

## 🛠️ Technologies Used

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI |
| **Database** | PostgreSQL with SQLAlchemy ORM |
| **Authentication** | JWT (JSON Web Tokens) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Templating** | Jinja2 |
| **Image Processing** | Pillow (PIL) |
| **Containerization** | Docker & Docker Compose |
| **API Documentation** | OpenAPI (Swagger) |

## 📋 API Endpoints

### 🔑 Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### 👤 User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/upload-image` - Upload profile image

### 🩺 Doctor Services
- `GET /api/doctors/` - List all doctors
- `GET /api/doctors/{id}` - Get doctor details
- `GET /api/doctors/timeslots/{id}` - Get doctor availability

### 📅 Appointments
- `POST /api/appointments/book` - Book appointment
- `GET /api/appointments/my` - Get user's appointments
- `PUT /api/appointments/{id}/status` - Update appointment

### 🌍 Location Services
- `GET /api/locations/divisions` - Get all divisions
- `GET /api/locations/districts/{division_id}` - Get districts
- `GET /api/locations/thanas/{district_id}` - Get thanas

### 👨‍💼 Admin Panel
- `GET /admin/` - Admin dashboard
- `GET /admin/doctors` - Manage doctors
- `GET /admin/appointments` - Manage appointments
- `GET /admin/monthly-report` - Generate reports

## 🚦 Getting Started Guide

### For Patients:
1. Visit http://localhost:8000
2. Click "Sign Up" to create an account
3. Fill in your details with location
4. Login and search for doctors
5. Book appointments

### For Doctors:
- Contact admin to create your doctor profile
- Login with provided credentials
- Set your available time slots
- Manage your appointments

### For Admins:
1. Access admin panel at http://localhost:8000/admin/login
2. Use admin credentials to login
3. Manage doctors, appointments, and generate reports

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (if not using Docker)
- Docker & Docker Compose (for containerized setup)

### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 📈 Features in Detail

### 🔍 Search & Filter
- Search doctors by name, specialization
- Filter by location (division, district, thana)
- Check doctor availability

### 📊 Reporting
- Monthly appointment reports
- Doctor earnings calculation
- Patient visit statistics
- System usage analytics

### 🔔 Notification System
- Real-time appointment updates
- Status change notifications
- System announcements

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes**
4. **Commit changes**: `git commit -am 'Add new feature'`
5. **Push to branch**: `git push origin feature/new-feature`
6. **Submit a pull request**

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For questions, issues, or support:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the Docker setup guide in `DOCKER.md`

---

**Made with ❤️ for healthcare management**
