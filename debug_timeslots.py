#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from appointment_system.models import DoctorProfile, DoctorTimeslot, User
from datetime import date

def debug_timeslots():
    db = SessionLocal()
    try:
        print("=== Checking Database State ===")

        # Check doctors
        doctors = db.query(DoctorProfile).all()
        print(f"Number of doctors in database: {len(doctors)}")

        for doctor in doctors:
            user = db.query(User).filter(User.id == doctor.user_id).first()
            print(f"Doctor ID: {doctor.id}, User: {user.full_name if user else 'Unknown'}")

        # Check timeslots
        timeslots = db.query(DoctorTimeslot).all()
        print(f"\nNumber of timeslots in database: {len(timeslots)}")

        for slot in timeslots:
            print(f"Timeslot ID: {slot.id}, Doctor ID: {slot.doctor_id}, "
                  f"Time: {slot.start_time}-{slot.end_time}, Available: {slot.is_available}")

        # Test the get_available_slots function
        if doctors and len(doctors) > 0:
            doctor_id = doctors[0].id
            test_date = date.today()

            print(f"\n=== Testing get_available_slots for Doctor {doctor_id} on {test_date} ===")

            from appointment_system.appointment_service import AppointmentService

            try:
                available_slots = AppointmentService.get_available_slots(db, doctor_id, test_date)
                print(f"Available slots: {available_slots}")
            except Exception as e:
                print(f"Error getting available slots: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_timeslots()
