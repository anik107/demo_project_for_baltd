#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from appointment_system.models import User, DoctorTimeslot, UserType

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user.id}, Name: {user.full_name}, Email: {user.email}, Type: {user.user_type}")
            if user.user_type == UserType.DOCTOR and user.doctor_profile:
                print(f"    Doctor Profile ID: {user.doctor_profile.id}")
                timeslots = db.query(DoctorTimeslot).filter(DoctorTimeslot.doctor_id == user.doctor_profile.id).all()
                print(f"    Timeslots: {len(timeslots)}")
                for slot in timeslots:
                    print(f"      {slot.start_time}-{slot.end_time} (Available: {slot.is_available})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
