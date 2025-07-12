#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from sqlalchemy import text

def check_appointments_table():
    db = SessionLocal()
    try:
        # Check what columns exist in the appointments table
        result = db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'appointments'
            ORDER BY ordinal_position;
        """))

        columns = result.fetchall()
        print("Columns in appointments table:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")

        # Check if any appointments exist
        result = db.execute(text("SELECT COUNT(*) FROM appointments"))
        count = result.scalar()
        print(f"\nNumber of appointments in table: {count}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_appointments_table()
