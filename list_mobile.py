#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

from appointment_system.database import SessionLocal
from appointment_system.models import User

def list_mobile_numbers():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("Mobile numbers in database:")
        for user in users:
            print(f"  {user.email}: {user.mobile_number}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_mobile_numbers()
