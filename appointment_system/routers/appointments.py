from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import SessionLocal
from schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from models import AppointmentStatus
from appointment_service import AppointmentService
from auth_utils import get_current_user
from models import User

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new appointment (patients only)
    """
    if current_user.user_type != "PATIENT":
        raise HTTPException(
            status_code=403,
            detail="Only patients can create appointments"
        )

    created_appointment = AppointmentService.create_appointment(
        db, appointment, current_user.id
    )

    # Return the appointment with full details
    return AppointmentService.get_appointment_by_id(db, created_appointment.id)

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointments based on user role:
    - Patients see their own appointments
    - Doctors see appointments with them
    - Admins see all appointments
    """
    patient_id = None
    doctor_user_id = None

    if current_user.user_type == "PATIENT":
        patient_id = current_user.id
    elif current_user.user_type == "DOCTOR":
        doctor_user_id = current_user.id
    # Admins can see all appointments (no filtering)

    return AppointmentService.get_appointments(
        db=db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        doctor_user_id=doctor_user_id,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific appointment by ID
    """
    # For non-admins, check if they have access to this appointment
    user_id = None if current_user.user_type == "ADMIN" else current_user.id

    return AppointmentService.get_appointment_by_id(db, appointment_id, user_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an appointment:
    - Patients can update date, time, and notes
    - Doctors can update status and notes
    - Admins can update everything
    """
    updated_appointment = AppointmentService.update_appointment(
        db, appointment_id, appointment_update, current_user.id
    )

    return AppointmentService.get_appointment_by_id(db, updated_appointment.id)

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an appointment
    """
    AppointmentService.cancel_appointment(db, appointment_id, current_user.id)
    return {"message": "Appointment cancelled successfully"}

@router.get("/doctors/{doctor_id}/availability")
async def get_doctor_availability(
    doctor_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available time slots for a doctor on a specific date
    """
    available_slots = AppointmentService.get_available_slots(db, doctor_id, appointment_date)
    return {
        "doctor_id": doctor_id,
        "date": appointment_date,
        "available_slots": available_slots
    }

@router.post("/{appointment_id}/confirm")
async def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm an appointment (doctors only)
    """
    if current_user.user_type not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Only doctors can confirm appointments"
        )

    appointment_update = AppointmentUpdate(status=AppointmentStatus.CONFIRMED)
    updated_appointment = AppointmentService.update_appointment(
        db, appointment_id, appointment_update, current_user.id
    )

    return AppointmentService.get_appointment_by_id(db, updated_appointment.id)

@router.post("/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an appointment as completed (doctors only)
    """
    if current_user.user_type not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Only doctors can complete appointments"
        )

    appointment_update = AppointmentUpdate(status=AppointmentStatus.COMPLETED)
    updated_appointment = AppointmentService.update_appointment(
        db, appointment_id, appointment_update, current_user.id
    )

    return AppointmentService.get_appointment_by_id(db, updated_appointment.id)

# Statistics endpoints
@router.get("/stats/summary")
async def get_appointment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appointment statistics based on user role
    """
    from sqlalchemy import func
    from models import Appointment

    if current_user.user_type == "PATIENT":
        # Patient stats
        stats = db.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.patient_id == current_user.id
        ).group_by(Appointment.status).all()

    elif current_user.user_type == "DOCTOR":
        # Doctor stats
        from models import DoctorProfile
        doctor_profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == current_user.id
        ).first()

        if not doctor_profile:
            raise HTTPException(status_code=404, detail="Doctor profile not found")

        stats = db.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.doctor_id == doctor_profile.id
        ).group_by(Appointment.status).all()

    else:  # Admin
        # System-wide stats
        stats = db.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).group_by(Appointment.status).all()

    return {
        "statistics": [{"status": stat.status, "count": stat.count} for stat in stats]
    }
