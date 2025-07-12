#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appointment_system'))

import requests

def test_availability():
    """Test the availability endpoint"""

    # Login first
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

        # Test availability endpoint with different dates
        test_dates = ["2025-07-13", "2025-07-14", "2025-07-15", "2025-07-16"]

        for test_date in test_dates:
            print(f"\nTesting availability for {test_date}...")

            availability_response = requests.get(
                f"http://localhost:8000/api/appointments/doctors/1/availability?appointment_date={test_date}",
                headers={"Authorization": f"Bearer {token}"}
            )

            print(f"Status: {availability_response.status_code}")
            print(f"Response: {availability_response.text}")

            if availability_response.status_code == 200:
                data = availability_response.json()
                print(f"Available slots: {len(data.get('available_slots', []))}")
            else:
                print("Failed to get availability")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_availability()
