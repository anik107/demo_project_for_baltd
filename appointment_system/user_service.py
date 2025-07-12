"""
User service layer for handling registration and user management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import logging
from models import User, DoctorProfile, DoctorTimeslot, Division, District, Thana
from schemas import UserCreate, User as UserSchema, DoctorProfileCreate
from auth_utils import hash_password, process_profile_image, validate_mobile_number, validate_password_strength

_logger = logging.getLogger(__name__)

class UserService:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserSchema:
        """
        Create a new user with all validations and requirements
        """
        try:
            # Validate password strength
            is_valid, error_msg = validate_password_strength(user_data.password)
            if not is_valid:
                raise ValueError(error_msg)

            # Validate mobile number format
            if not validate_mobile_number(user_data.mobile_number):
                raise ValueError("Invalid mobile number format. Must start with +88 and be exactly 14 digits.")

            # Validate location hierarchy
            UserService._validate_location_hierarchy(db, user_data.division_id, user_data.district_id, user_data.thana_id)

            # Check if email or mobile already exists
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (User.mobile_number == user_data.mobile_number)
            ).first()
            if existing_user:
                if existing_user.email == user_data.email:
                    raise ValueError("Email already registered")
                else:
                    raise ValueError("Mobile number already registered")

            # Process profile image if provided
            profile_image_data = None
            profile_image_content_type = None
            if user_data.profile_image_base64 and user_data.profile_image_filename:
                profile_image_data, profile_image_content_type = process_profile_image(
                    user_data.profile_image_base64, user_data.profile_image_filename
                )

            # Hash password
            hashed_password = hash_password(user_data.password)

            # Create user
            db_user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                mobile_number=user_data.mobile_number,
                hashed_password=hashed_password,
                user_type=user_data.user_type,
                division_id=user_data.division_id,
                district_id=user_data.district_id,
                thana_id=user_data.thana_id,
                profile_image=profile_image_data,
                profile_image_filename=user_data.profile_image_filename,
                profile_image_content_type=profile_image_content_type
            )

            db.add(db_user)
            db.flush()  # Get the user ID

            # If user is a doctor, create doctor profile
            if user_data.user_type.value == "DOCTOR":
                if not user_data.doctor_profile:
                    raise ValueError("Doctor profile is required for doctor user type")

                doctor_profile = UserService._create_doctor_profile(
                    db, db_user.id, user_data.doctor_profile
                )

            db.commit()

            # Return user with relationships
            db.refresh(db_user)
            return UserSchema.from_orm(db_user)

        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                raise ValueError("Email already registered")
            elif "mobile_number" in str(e):
                raise ValueError("Mobile number already registered")
            elif "license_number" in str(e):
                raise ValueError("License number already exists")
            else:
                raise ValueError("Registration failed due to data constraint violation")

        except Exception as e:
            _logger.info(f"Registration failed: {str(e)}")
            db.rollback()
            raise ValueError(f"Registration failed: {str(e)}")

    @staticmethod
    def _validate_location_hierarchy(db: Session, division_id: int, district_id: int, thana_id: int):
        """
        Validate that district belongs to division and thana belongs to district
        """
        # Check if division exists
        division = db.query(Division).filter(Division.id == division_id).first()
        if not division:
            raise ValueError("Invalid division selected")

        # Check if district belongs to the division
        district = db.query(District).filter(
            District.id == district_id, District.division_id == division_id
        ).first()
        if not district:
            raise ValueError("Selected district does not belong to the selected division")

        # Check if thana belongs to the district
        thana = db.query(Thana).filter(
            Thana.id == thana_id, Thana.district_id == district_id
        ).first()
        if not thana:
            raise ValueError("Selected thana does not belong to the selected district")

    @staticmethod
    def _create_doctor_profile(db: Session, user_id: int, doctor_data: DoctorProfileCreate) -> DoctorProfile:
        """
        Create doctor profile with validation
        """
        # Validate experience years
        if doctor_data.experience_years < 0:
            raise ValueError("Experience years cannot be negative")

        # Validate consultation fee
        if doctor_data.consultation_fee < 0:
            raise ValueError("Consultation fee cannot be negative")

        # Check if license number already exists
        existing_license = db.query(DoctorProfile).filter(
            DoctorProfile.license_number == doctor_data.license_number
        ).first()
        if existing_license:
            raise ValueError("License number already exists")

        # Create doctor profile
        doctor_profile = DoctorProfile(
            user_id=user_id,
            license_number=doctor_data.license_number,
            experience_years=doctor_data.experience_years,
            consultation_fee=doctor_data.consultation_fee
        )

        db.add(doctor_profile)
        db.flush()  # Get the doctor profile ID

        # Create timeslots if provided
        for timeslot_data in doctor_data.available_timeslots:
            UserService._validate_timeslot(timeslot_data.start_time, timeslot_data.end_time)

            timeslot = DoctorTimeslot(
                doctor_id=doctor_profile.id,
                start_time=timeslot_data.start_time,
                end_time=timeslot_data.end_time,
                is_available=timeslot_data.is_available
            )
            db.add(timeslot)

        return doctor_profile

    @staticmethod
    def _validate_timeslot(start_time: str, end_time: str):
        """
        Validate timeslot format and logic
        """
        import re
        from datetime import datetime

        # Validate time format
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
            raise ValueError("Time must be in HH:MM format")

        # Validate that start time is before end time
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")

        if start_dt >= end_dt:
            raise ValueError("Start time must be before end time")

        # Validate minimum consultation time (e.g., at least 30 minutes)
        time_diff = (end_dt - start_dt).total_seconds() / 60
        if time_diff < 30:
            raise ValueError("Minimum consultation time is 30 minutes")

    @staticmethod
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_mobile(db: Session, mobile: str) -> Optional[User]:
        """Get user by mobile number"""
        return db.query(User).filter(User.mobile_number == mobile).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID with all relationships"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_doctors(db: Session, skip: int = 0, limit: int = 100):
        """Get all doctors with their profiles"""
        return db.query(User).filter(User.user_type == "DOCTOR").offset(skip).limit(limit).all()

    @staticmethod
    def update_doctor_timeslots(db: Session, doctor_id: int, timeslots: list) -> bool:
        """Update doctor's available timeslots"""
        try:
            # Get doctor profile
            doctor_profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_id).first()
            if not doctor_profile:
                raise ValueError("Doctor profile not found")

            # Delete existing timeslots
            db.query(DoctorTimeslot).filter(DoctorTimeslot.doctor_id == doctor_profile.id).delete()

            # Add new timeslots
            for slot in timeslots:
                UserService._validate_timeslot(slot.start_time, slot.end_time)
                new_slot = DoctorTimeslot(
                    doctor_id=doctor_profile.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    is_available=slot.is_available
                )
                db.add(new_slot)

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update timeslots: {str(e)}")
