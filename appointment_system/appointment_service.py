from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time, datetime, timedelta
from typing import List
from models import Appointment, DoctorProfile, User, DoctorTimeslot, AppointmentStatus
from schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from fastapi import HTTPException

class AppointmentService:
    @staticmethod
    def create_appointment(db: Session, appointment_data: AppointmentCreate, patient_id: int) -> Appointment:
        """
        Create a new appointment with validation for doctor availability
        """
        # Check if doctor exists
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == appointment_data.doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Check if patient exists and is actually a patient
        patient = db.query(User).filter(
            and_(User.id == patient_id, User.user_type == "PATIENT")
        ).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Validate appointment time against doctor's availability
        if not AppointmentService._is_doctor_available(
            db, appointment_data.doctor_id, appointment_data.appointment_date, appointment_data.appointment_time
        ):
            raise HTTPException(
                status_code=400,
                detail="Doctor is not available at the selected time slot"
            )

        # Check for conflicting appointments
        if AppointmentService._has_conflicting_appointment(
            db, appointment_data.doctor_id, appointment_data.appointment_date, appointment_data.appointment_time
        ):
            raise HTTPException(
                status_code=400,
                detail="Time slot is already booked"
            )

        # Create the appointment
        db_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            notes=appointment_data.notes,
            status=AppointmentStatus.PENDING
        )

        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)

        return db_appointment

    @staticmethod
    def _is_doctor_available(db: Session, doctor_id: int, appointment_date: date, appointment_time: time) -> bool:
        """
        Check if doctor has available time slots for the requested time
        """
        # Get doctor's available time slots
        timeslots = db.query(DoctorTimeslot).filter(
            and_(
                DoctorTimeslot.doctor_id == doctor_id,
                DoctorTimeslot.is_available == True
            )
        ).all()

        # Convert appointment time to string for comparison
        appointment_time_str = appointment_time.strftime("%H:%M")

        # Check if appointment time falls within any available slot
        for slot in timeslots:
            if slot.start_time <= appointment_time_str < slot.end_time:
                return True

        return False

    @staticmethod
    def _has_conflicting_appointment(db: Session, doctor_id: int, appointment_date: date, appointment_time: time) -> bool:
        """
        Check if there's already an appointment at the same time
        """
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.appointment_time == appointment_time,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        ).first()

        return existing_appointment is not None

    @staticmethod
    def get_appointment_by_id(db: Session, appointment_id: int, user_id: int = None) -> AppointmentResponse:
        """
        Get appointment by ID with related information
        """
        from sqlalchemy.orm import aliased

        PatientUser = aliased(User)
        DoctorUser = aliased(User)

        query = db.query(
            Appointment,
            PatientUser.full_name.label('patient_name'),
            PatientUser.email.label('patient_email'),
            PatientUser.mobile_number.label('patient_mobile'),
            DoctorUser.full_name.label('doctor_name'),
            DoctorProfile.license_number.label('doctor_license'),
            DoctorProfile.consultation_fee.label('consultation_fee')
        ).join(
            PatientUser, Appointment.patient_id == PatientUser.id
        ).join(
            DoctorProfile, Appointment.doctor_id == DoctorProfile.id
        ).join(
            DoctorUser, DoctorProfile.user_id == DoctorUser.id
        ).filter(
            Appointment.id == appointment_id
        )

        # If user_id is provided, filter by patient or doctor
        if user_id:
            query = query.filter(
                (Appointment.patient_id == user_id) |
                (DoctorProfile.user_id == user_id)
            )

        result = query.first()
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")

        appointment, patient_name, patient_email, patient_mobile, doctor_name, doctor_license, consultation_fee = result

        return AppointmentResponse(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            notes=appointment.notes,
            status=appointment.status,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            patient_name=patient_name,
            patient_email=patient_email,
            patient_mobile=patient_mobile,
            doctor_name=doctor_name,
            doctor_license=doctor_license,
            consultation_fee=consultation_fee
        )

    @staticmethod
    def get_appointments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        patient_id: int = None,
        doctor_user_id: int = None,
        status: AppointmentStatus = None,
        date_from: date = None,
        date_to: date = None
    ) -> List[AppointmentResponse]:
        """
        Get appointments with filtering options
        """
        from sqlalchemy.orm import aliased

        PatientUser = aliased(User)
        DoctorUser = aliased(User)

        query = db.query(
            Appointment,
            PatientUser.full_name.label('patient_name'),
            PatientUser.email.label('patient_email'),
            PatientUser.mobile_number.label('patient_mobile'),
            DoctorUser.full_name.label('doctor_name'),
            DoctorProfile.license_number.label('doctor_license'),
            DoctorProfile.consultation_fee.label('consultation_fee')
        ).join(
            PatientUser, Appointment.patient_id == PatientUser.id
        ).join(
            DoctorProfile, Appointment.doctor_id == DoctorProfile.id
        ).join(
            DoctorUser, DoctorProfile.user_id == DoctorUser.id
        )

        # Apply filters
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)

        if doctor_user_id:
            query = query.filter(DoctorProfile.user_id == doctor_user_id)

        if status:
            query = query.filter(Appointment.status == status)

        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)

        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)

        # Order by appointment date and time
        query = query.order_by(Appointment.appointment_date, Appointment.appointment_time)

        results = query.offset(skip).limit(limit).all()

        appointments = []
        for result in results:
            appointment, patient_name, patient_email, patient_mobile, doctor_name, doctor_license, consultation_fee = result
            appointments.append(AppointmentResponse(
                id=appointment.id,
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                notes=appointment.notes,
                status=appointment.status,
                created_at=appointment.created_at,
                updated_at=appointment.updated_at,
                patient_name=patient_name,
                patient_email=patient_email,
                patient_mobile=patient_mobile,
                doctor_name=doctor_name,
                doctor_license=doctor_license,
                consultation_fee=consultation_fee
            ))

        return appointments

    @staticmethod
    def update_appointment(
        db: Session,
        appointment_id: int,
        appointment_data: AppointmentUpdate,
        user_id: int
    ) -> Appointment:
        """
        Update an appointment (patients can update details, doctors can update status)
        """
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Check permissions
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == appointment.doctor_id).first()
        is_patient = appointment.patient_id == user_id
        is_doctor = doctor and doctor.user_id == user_id

        if not (is_patient or is_doctor):
            raise HTTPException(status_code=403, detail="Not authorized to update this appointment")

        # If rescheduling, validate new time slot
        if appointment_data.appointment_date or appointment_data.appointment_time:
            new_date = appointment_data.appointment_date or appointment.appointment_date
            new_time = appointment_data.appointment_time or appointment.appointment_time

            # Only check availability if time is actually changing
            if (new_date != appointment.appointment_date or new_time != appointment.appointment_time):
                if not AppointmentService._is_doctor_available(db, appointment.doctor_id, new_date, new_time):
                    raise HTTPException(status_code=400, detail="Doctor is not available at the selected time slot")

                if AppointmentService._has_conflicting_appointment(db, appointment.doctor_id, new_date, new_time):
                    raise HTTPException(status_code=400, detail="Time slot is already booked")

        # Update fields
        if appointment_data.appointment_date is not None:
            appointment.appointment_date = appointment_data.appointment_date
        if appointment_data.appointment_time is not None:
            appointment.appointment_time = appointment_data.appointment_time
        if appointment_data.notes is not None:
            appointment.notes = appointment_data.notes
        if appointment_data.status is not None:
            # Only doctors can change status to CONFIRMED/COMPLETED, patients can only CANCEL
            if is_doctor or (is_patient and appointment_data.status == AppointmentStatus.CANCELLED):
                appointment.status = appointment_data.status
            else:
                raise HTTPException(status_code=403, detail="Not authorized to change appointment status")

        appointment.updated_at = datetime.now()
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int, user_id: int) -> Appointment:
        """
        Cancel an appointment
        """
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Check permissions
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == appointment.doctor_id).first()
        is_patient = appointment.patient_id == user_id
        is_doctor = doctor and doctor.user_id == user_id

        if not (is_patient or is_doctor):
            raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

        if appointment.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
            raise HTTPException(status_code=400, detail="Cannot cancel appointment in current status")

        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.now()
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def get_available_slots(db: Session, doctor_id: int, appointment_date: date) -> List[dict]:
        """
        Get available time slots for a doctor on a specific date
        """
        # Get doctor's available time slots
        timeslots = db.query(DoctorTimeslot).filter(
            and_(
                DoctorTimeslot.doctor_id == doctor_id,
                DoctorTimeslot.is_available == True
            )
        ).all()

        # Get existing appointments for that date
        booked_times = db.query(Appointment.appointment_time).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        ).all()

        booked_time_strings = {time.strftime("%H:%M") for time, in booked_times}

        available_slots = []
        for slot in timeslots:
            # Generate 30-minute slots within each time range
            start_hour, start_minute = map(int, slot.start_time.split(':'))
            end_hour, end_minute = map(int, slot.end_time.split(':'))

            current_time = datetime.combine(appointment_date, time(start_hour, start_minute))
            end_time = datetime.combine(appointment_date, time(end_hour, end_minute))

            while current_time < end_time:
                time_str = current_time.strftime("%H:%M")
                if time_str not in booked_time_strings:
                    available_slots.append({
                        "time": time_str,
                        "available": True
                    })
                current_time += timedelta(minutes=30)

        return available_slots
