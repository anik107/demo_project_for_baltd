#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from appointment_system.models import DoctorTimeslot
from datetime import datetime, date, time, timedelta

def test_timeslot_generation():
    db = SessionLocal()
    try:
        # Get a timeslot
        slot = db.query(DoctorTimeslot).first()
        if not slot:
            print("No timeslots found")
            return

        print(f"Testing timeslot: {slot.start_time} - {slot.end_time}")

        # Try to parse the time strings
        try:
            start_hour, start_minute = map(int, slot.start_time.split(':'))
            end_hour, end_minute = map(int, slot.end_time.split(':'))
            print(f"Parsed start: {start_hour}:{start_minute}")
            print(f"Parsed end: {end_hour}:{end_minute}")

            appointment_date = date.today()
            current_time = datetime.combine(appointment_date, time(start_hour, start_minute))
            end_time = datetime.combine(appointment_date, time(end_hour, end_minute))

            print(f"Generated datetime objects:")
            print(f"  Start: {current_time}")
            print(f"  End: {end_time}")

            # Generate slots
            available_slots = []
            while current_time < end_time:
                time_str = current_time.strftime("%H:%M")
                available_slots.append({
                    "time": time_str,
                    "available": True
                })
                current_time += timedelta(minutes=30)

            print(f"Generated {len(available_slots)} slots:")
            for slot_data in available_slots:
                print(f"  {slot_data['time']}")

        except Exception as e:
            print(f"Error parsing timeslot: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_timeslot_generation()
