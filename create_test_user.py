#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from appointment_system.models import User, DoctorProfile, DoctorTimeslot, UserType
from appointment_system.auth_utils import hash_password

def create_test_user():
    db = SessionLocal()
    try:        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "testpatient@example.com").first()
        if existing_user:
            print("Test user already exists")
        else:
            # Create a test patient with unique mobile number
            test_user = User(
                full_name="Test Patient",
                email="testpatient@example.com",
                mobile_number="+8801234567893",  # Using a new number
                hashed_password=hash_password("TestPass123!"),
                user_type=UserType.PATIENT,
                division_id=1,  # Assuming division 1 exists
                district_id=1,  # Assuming district 1 exists
                thana_id=1      # Assuming thana 1 exists
            )

            db.add(test_user)
            db.commit()
            print("Test patient created successfully: testpatient@example.com / TestPass123!")

        # Check if test doctor already exists
        existing_doctor = db.query(User).filter(User.email == "doctor@example.com").first()
        if not existing_doctor:
            # Create a test doctor
            test_doctor = User(
                full_name="Dr. Test Doctor",
                email="doctor@example.com",
                mobile_number="+8801234567891",
                hashed_password=hash_password("TestPass123!"),
                user_type=UserType.DOCTOR,
                division_id=1,
                district_id=1,
                thana_id=1
            )

            db.add(test_doctor)
            db.commit()
            db.refresh(test_doctor)

            # Create doctor profile
            doctor_profile = DoctorProfile(
                user_id=test_doctor.id,
                license_number="TEST12345",
                experience_years=5,
                consultation_fee=50.0
            )

            db.add(doctor_profile)
            db.commit()
            db.refresh(doctor_profile)

            # Create some test timeslots
            timeslot1 = DoctorTimeslot(
                doctor_id=doctor_profile.id,
                start_time="09:00",
                end_time="12:00",
                is_available=True
            )

            timeslot2 = DoctorTimeslot(
                doctor_id=doctor_profile.id,
                start_time="14:00",
                end_time="17:00",
                is_available=True
            )

            db.add(timeslot1)
            db.add(timeslot2)
            db.commit()

            print("Test doctor created successfully with timeslots")
        else:
            print("Test doctor already exists")

    except Exception as e:
        print(f"Error creating test user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
