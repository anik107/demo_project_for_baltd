#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

import requests

def test_appointment_booking():
    """Test appointment booking via API"""

    # First, login to get a token
    login_data = {
        "email": "testpatient@example.com",
        "password": "TestPass123!"
    }

    try:
        # Login
        print("Logging in...")
        login_response = requests.post(
            "http://localhost:8000/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return

        login_result = login_response.json()
        token = login_result["access_token"]
        print("✓ Login successful")

        # Get available time slots for doctor ID 1
        print("\nChecking doctor availability...")
        availability_response = requests.get(
            "http://localhost:8000/api/appointments/doctors/1/availability?appointment_date=2025-07-15",
            headers={"Authorization": f"Bearer {token}"}
        )

        if availability_response.status_code == 200:
            availability = availability_response.json()
            print(f"Available slots: {availability}")
        else:
            print(f"Failed to get availability: {availability_response.status_code}")
            print(f"Response: {availability_response.text}")

        # Try to book an appointment
        print("\nAttempting to book appointment...")
        appointment_data = {
            "doctor_id": 1,
            "appointment_date": "2025-07-15",
            "appointment_time": "16:00",
            "notes": "Test appointment booking"
        }

        booking_response = requests.post(
            "http://localhost:8000/api/appointments/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=appointment_data
        )

        print(f"Booking response status: {booking_response.status_code}")
        print(f"Response headers: {dict(booking_response.headers)}")
        print(f"Response text: {booking_response.text}")

        if booking_response.status_code == 201:
            appointment = booking_response.json()
            print("✓ Appointment booked successfully!")
            print(f"Appointment ID: {appointment['id']}")
            print(f"Date: {appointment['appointment_date']}")
            print(f"Time: {appointment['appointment_time']}")
            print(f"Status: {appointment['status']}")
        else:
            print(f"✗ Booking failed with status {booking_response.status_code}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_appointment_booking()
