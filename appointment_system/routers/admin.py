from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, extract, func, or_
from database import get_db
import models
from auth_utils import verify_password, create_access_token, get_current_user_from_token
from datetime import datetime
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_admin_user(request: Request, db: Session = Depends(get_db)):
    """Get admin user from cookie or redirect to login"""
    admin_token = request.cookies.get("admin_token")

    if not admin_token:
        return None

    try:
        user = get_current_user_from_token(admin_token, db)
        if user and user.user_type == models.UserType.ADMIN:
            return user
    except:
        pass

    return None

def require_admin_cookie(request: Request, db: Session = Depends(get_db)):
    """Require admin authentication via cookie"""
    user = get_admin_user(request, db)
    if not user:
        # Return a redirect response instead of raising exception
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/admin/login", status_code=303)
    return user

# Admin Login
@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    """Show admin login form"""
    return templates.TemplateResponse("admin_login.html", {
        "request": request
    })

@router.post("/admin/login")
async def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    # Find user by email
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Invalid email or password"
        })

    # Check if user is admin
    if user.user_type != models.UserType.ADMIN:
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Admin access required"
        })

    # Create access token and redirect to admin dashboard
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    # For now, we'll redirect to admin dashboard
    # In a real app, you'd set a secure cookie with the token
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="admin_token", value=access_token, httponly=True, secure=False)
    return response

@router.get("/admin/logout")
async def admin_logout():
    """Admin logout endpoint"""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="admin_token")
    return response

# Admin Dashboard
@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard with overview statistics"""
    user = get_admin_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user
    })

# Appointments Management
@router.get("/admin/appointments", response_class=HTMLResponse)
async def admin_appointments(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """View all appointments"""
    appointments = db.query(models.Appointment).options(
        joinedload(models.Appointment.patient),
        joinedload(models.Appointment.doctor).joinedload(models.DoctorProfile.user)
    ).order_by(models.Appointment.appointment_date.desc()).all()

    return templates.TemplateResponse("admin_appointments.html", {
        "request": request,
        "user": current_user,
        "appointments": appointments
    })

@router.post("/admin/appointments/{appointment_id}/update-status")
async def update_appointment_status(
    appointment_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Update appointment status"""
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Validate status
    try:
        appointment_status = models.AppointmentStatus(status)
        appointment.status = appointment_status
        appointment.updated_at = datetime.utcnow()
        db.commit()
        return RedirectResponse(url="/admin/appointments", status_code=303)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

@router.post("/admin/appointments/{appointment_id}/delete")
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Delete an appointment"""
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
    return RedirectResponse(url="/admin/appointments", status_code=303)

@router.get("/admin/appointments/create", response_class=HTMLResponse)
async def create_appointment_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Show create appointment form"""
    # Get all patients and doctors
    patients = db.query(models.User).filter(models.User.user_type == models.UserType.PATIENT).all()
    doctors = db.query(models.DoctorProfile).options(joinedload(models.DoctorProfile.user)).all()
    status = [{
        "name": appt_status.name,
        "value": appt_status.value
    } for appt_status in models.AppointmentStatus]
    return templates.TemplateResponse("admin_create_appointment.html", {
        "request": request,
        "user": current_user,
        "patients": patients,
        "doctors": doctors,
        "status": status
    })

@router.post("/admin/appointments/create")
async def create_appointment(
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Create a new appointment"""
    try:
        # Parse date and time
        appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        appt_time = datetime.strptime(appointment_time, "%H:%M").time()

        # Check if patient and doctor exist
        patient = db.query(models.User).filter(
            and_(models.User.id == patient_id, models.User.user_type == models.UserType.PATIENT)
        ).first()
        doctor = db.query(models.DoctorProfile).filter(models.DoctorProfile.id == doctor_id).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Create appointment
        appointment = models.Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appt_date,
            appointment_time=appt_time,
            notes=notes,
            status=models.AppointmentStatus.PENDING
        )

        db.add(appointment)
        db.commit()
        return RedirectResponse(url="/admin/appointments", status_code=303)

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date or time format")

# Doctors Management
@router.get("/admin/doctors", response_class=HTMLResponse)
async def admin_doctors(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """View all doctors"""
    doctors = db.query(models.DoctorProfile).options(
        joinedload(models.DoctorProfile.user),
        joinedload(models.DoctorProfile.available_timeslots)
    ).all()

    return templates.TemplateResponse("admin_doctors.html", {
        "request": request,
        "user": current_user,
        "doctors": doctors
    })

@router.get("/admin/doctors/create", response_class=HTMLResponse)
async def create_doctor_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Show create doctor form"""
    # Get location data
    divisions = db.query(models.Division).all()
    districts = db.query(models.District).all()
    thanas = db.query(models.Thana).all()

    return templates.TemplateResponse("admin_create_doctor.html", {
        "request": request,
        "user": current_user,
        "divisions": divisions,
        "districts": districts,
        "thanas": thanas
    })

@router.post("/admin/doctors/create")
async def create_doctor(
    full_name: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    password: str = Form(...),
    license_number: str = Form(...),
    experience_years: int = Form(...),
    consultation_fee: float = Form(...),
    division_id: int = Form(...),
    district_id: int = Form(...),
    thana_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Create a new doctor"""
    from auth_utils import hash_password

    # Check if user already exists
    existing_user = db.query(models.User).filter(
        or_(models.User.email == email, models.User.mobile_number == mobile_number)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or mobile number already exists")

    # Check if license number already exists
    existing_license = db.query(models.DoctorProfile).filter(
        models.DoctorProfile.license_number == license_number
    ).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already exists")

    try:
        # Create user
        hashed_password = hash_password(password)
        user = models.User(
            full_name=full_name,
            email=email,
            mobile_number=mobile_number,
            hashed_password=hashed_password,
            user_type=models.UserType.DOCTOR,
            division_id=division_id,
            district_id=district_id,
            thana_id=thana_id
        )
        db.add(user)
        db.flush()  # Get the user ID

        # Create doctor profile
        doctor_profile = models.DoctorProfile(
            user_id=user.id,
            license_number=license_number,
            experience_years=experience_years,
            consultation_fee=consultation_fee
        )
        db.add(doctor_profile)
        db.commit()

        return RedirectResponse(url="/admin/doctors", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create doctor")

@router.post("/admin/doctors/{doctor_id}/delete")
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Delete a doctor and their user account"""
    doctor = db.query(models.DoctorProfile).filter(models.DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check if doctor has active appointments
    active_appointments = db.query(models.Appointment).filter(
        and_(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.status.in_([models.AppointmentStatus.PENDING, models.AppointmentStatus.CONFIRMED])
        )
    ).count()

    if active_appointments > 0:
        raise HTTPException(status_code=400, detail="Cannot delete doctor with active appointments")

    # Delete doctor profile and user
    user = doctor.user
    db.delete(doctor)
    db.delete(user)
    db.commit()

    return RedirectResponse(url="/admin/doctors", status_code=303)

@router.get("/admin/doctors/{doctor_id}/edit", response_class=HTMLResponse)
async def edit_doctor_form(
    doctor_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Show edit doctor form"""
    doctor = db.query(models.DoctorProfile).options(
        joinedload(models.DoctorProfile.user)
    ).filter(models.DoctorProfile.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Get location data
    divisions = db.query(models.Division).all()
    districts = db.query(models.District).all()
    thanas = db.query(models.Thana).all()

    return templates.TemplateResponse("admin_edit_doctor.html", {
        "request": request,
        "user": current_user,
        "doctor": doctor,
        "divisions": divisions,
        "districts": districts,
        "thanas": thanas
    })

@router.post("/admin/doctors/{doctor_id}/edit")
async def edit_doctor(
    doctor_id: int,
    full_name: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    license_number: str = Form(...),
    experience_years: int = Form(...),
    consultation_fee: float = Form(...),
    division_id: int = Form(...),
    district_id: int = Form(...),
    thana_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Update doctor information"""
    doctor = db.query(models.DoctorProfile).options(
        joinedload(models.DoctorProfile.user)
    ).filter(models.DoctorProfile.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check for duplicate email/mobile (excluding current user)
    existing_user = db.query(models.User).filter(
        and_(
            models.User.id != doctor.user.id,
            or_(models.User.email == email, models.User.mobile_number == mobile_number)
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or mobile number already exists")

    # Check for duplicate license (excluding current doctor)
    existing_license = db.query(models.DoctorProfile).filter(
        and_(
            models.DoctorProfile.id != doctor_id,
            models.DoctorProfile.license_number == license_number
        )
    ).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already exists")

    try:
        # Update user
        doctor.user.full_name = full_name
        doctor.user.email = email
        doctor.user.mobile_number = mobile_number
        doctor.user.division_id = division_id
        doctor.user.district_id = district_id
        doctor.user.thana_id = thana_id
        doctor.user.updated_at = datetime.utcnow()

        # Update doctor profile
        doctor.license_number = license_number
        doctor.experience_years = experience_years
        doctor.consultation_fee = consultation_fee

        db.commit()
        return RedirectResponse(url="/admin/doctors", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update doctor")

# API endpoints for getting statistics
@router.get("/admin/api/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Get admin dashboard statistics"""
    total_appointments = db.query(models.Appointment).count()
    total_doctors = db.query(models.DoctorProfile).count()
    total_patients = db.query(models.User).filter(models.User.user_type == models.UserType.PATIENT).count()

    pending_appointments = db.query(models.Appointment).filter(
        models.Appointment.status == models.AppointmentStatus.PENDING
    ).count()

    return {
        "total_appointments": total_appointments,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "pending_appointments": pending_appointments
    }

@router.get("/admin/monthly-report", response_class=HTMLResponse)
async def admin_monthly_report(request: Request, db: Session = Depends(get_db)):
    """Generate a monthly report for all doctors (admin only)"""
    user = get_admin_user(request, db)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)

    # Get current month and year
    now = datetime.now()
    year = now.year
    month = now.month

    # Query: For each doctor, count unique patients, total appointments, and total money earned
    results = (
        db.query(
            models.DoctorProfile.id.label("doctor_id"),
            models.User.full_name.label("doctor_name"),
            func.count(models.Appointment.id).label("total_appointments"),
            func.count(func.distinct(models.Appointment.patient_id)).label("total_patient_visits"),
            (func.count(models.Appointment.id) * models.DoctorProfile.consultation_fee).label("total_money_earned")
        )
        .join(models.User, models.DoctorProfile.user_id == models.User.id)
        .outerjoin(models.Appointment, (
            (models.Appointment.doctor_id == models.DoctorProfile.id) &
            (extract('year', models.Appointment.appointment_date) == year) &
            (extract('month', models.Appointment.appointment_date) == month) &
            (models.Appointment.status == models.AppointmentStatus.COMPLETED)
        ))
        .group_by(models.DoctorProfile.id, models.User.full_name, models.DoctorProfile.consultation_fee)
        .order_by(models.User.full_name)
        .all()
    )

    # Prepare data for template
    report_data = [
        {
            "doctor_name": row.doctor_name,
            "total_patient_visits": row.total_patient_visits,
            "total_appointments": row.total_appointments,
            "total_money_earned": row.total_money_earned or 0.0
        }
        for row in results
    ]

    return templates.TemplateResponse("admin_monthly_report.html", {
        "request": request,
        "user": user,
        "report_data": report_data
    })