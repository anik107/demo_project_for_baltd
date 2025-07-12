#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from sqlalchemy import text

def fix_appointments_table():
    db = SessionLocal()
    try:
        print("Adding appointment_date column to appointments table...")

        # Add the missing appointment_date column
        db.execute(text("""
            ALTER TABLE appointments
            ADD COLUMN appointment_date DATE;
        """))

        # Since appointment_time is currently a timestamp, we need to convert it
        # For now, let's just make it nullable so the app can work
        db.execute(text("""
            ALTER TABLE appointments
            ALTER COLUMN appointment_time TYPE TIME;
        """))

        db.commit()
        print("Successfully added appointment_date column and fixed appointment_time type")

        # Check the updated schema
        result = db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'appointments'
            ORDER BY ordinal_position;
        """))

        columns = result.fetchall()
        print("\nUpdated columns in appointments table:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_appointments_table()
