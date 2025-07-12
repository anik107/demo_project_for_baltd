# Appointment System

A FastAPI-based appointment booking system with user authentication and location-based services.

## Features

- User registration and authentication
- Doctor appointment booking
- Location-based services
- Web-based dashboard
- RESTful API endpoints

## Project Structure

```
appointment_system/
├── main.py              # FastAPI application entry point
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── database.py         # Database configuration
├── config.py           # Application configuration
├── auth_utils.py       # Authentication utilities
├── user_service.py     # User service layer
├── location_utils.py   # Location utilities
├── requirements.txt    # Python dependencies
├── routers/           # API route handlers
│   ├── auth.py        # Authentication routes
│   ├── users.py       # User management routes
│   ├── doctors.py     # Doctor management routes
│   ├── locations.py   # Location routes
│   └── general.py     # General web pages
├── templates/         # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
└── static/           # Static assets
    ├── css/
    └── js/
```

## Installation

1. Clone the repository:
```bash
git clone git@github.com:anik107/demo_project_for_baltd.git
cd demo_project_for_baltd
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd appointment_system
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
cd appointment_system
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to:
- Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## API Endpoints

- `/` - Home page
- `/login` - Login page
- `/signup` - Registration page
- `/dashboard` - User dashboard
- `/api/auth/` - Authentication endpoints
- `/api/users/` - User management endpoints
- `/api/doctors/` - Doctor management endpoints
- `/api/locations/` - Location services endpoints

## Technologies Used

- **Backend**: FastAPI, Python
- **Authentication**: JWT tokens
- **Database**: SQLAlchemy (configurable database)
- **Frontend**: HTML, CSS, JavaScript
- **Templating**: Jinja2

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
