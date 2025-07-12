#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from sqlalchemy import text

def fix_appointments_table():
    """Add missing timestamp columns to the appointments table"""
    db = SessionLocal()
    try:
        print("Adding missing timestamp columns to appointments table...")

        # Add created_at column
        try:
            db.execute(text("""
                ALTER TABLE appointments
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """))
            print("✓ Added created_at column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ created_at column already exists")
            else:
                print(f"Error adding created_at: {e}")

        # Add updated_at column
        try:
            db.execute(text("""
                ALTER TABLE appointments
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """))
            print("✓ Added updated_at column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ updated_at column already exists")
            else:
                print(f"Error adding updated_at: {e}")

        # Commit the changes
        db.commit()
        print("✓ Database schema updated successfully")

        # Verify the changes
        result = db.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'appointments'
            ORDER BY ordinal_position;
        """))

        columns = result.fetchall()
        print("\nUpdated appointments table structure:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")

    except Exception as e:
        print(f"Error fixing appointments table: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_appointments_table()
