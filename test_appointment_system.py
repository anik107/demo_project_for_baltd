#!/usr/bin/env python3
"""
Test script for the Appointment Booking System

This script tests all the appointment booking functionality including:
1. Creating appointments with validation
2. Checking doctor availability
3. Preventing double booking
4. Updating and cancelling appointments
5. Status management
"""

import asyncio
import httpx
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"
TEST_PATIENT_EMAIL = "patient@test.com"
TEST_PATIENT_PASSWORD = "TestPass123!"
TEST_DOCTOR_EMAIL = "doctor@test.com"
TEST_DOCTOR_PASSWORD = "TestPass123!"

class AppointmentSystemTester:
    def __init__(self):
        self.patient_token = None
        self.doctor_token = None
        self.patient_id = None
        self.doctor_id = None
        self.doctor_profile_id = None
        self.test_appointment_id = None

    async def run_tests(self):
        """Run comprehensive tests for the appointment system"""
        async with httpx.AsyncClient() as client:
            print("🚀 Starting Appointment System Tests")
            print("=" * 50)

            try:
                # Step 1: Setup test users
                await self.setup_test_users(client)

                # Step 2: Test doctor availability
                await self.test_doctor_availability(client)

                # Step 3: Test appointment creation
                await self.test_appointment_creation(client)

                # Step 4: Test double booking prevention
                await self.test_double_booking_prevention(client)

                # Step 5: Test appointment retrieval
                await self.test_appointment_retrieval(client)

                # Step 6: Test appointment updates
                await self.test_appointment_updates(client)

                # Step 7: Test appointment status management
                await self.test_appointment_status_management(client)

                # Step 8: Test appointment cancellation
                await self.test_appointment_cancellation(client)

                print("\n✅ All tests completed successfully!")

            except Exception as e:
                print(f"\n❌ Test failed: {e}")
                raise

    async def setup_test_users(self, client):
        """Setup test patient and doctor users"""
        print("\n1. Setting up test users...")

        # Login as patient
        try:
            response = await client.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_PATIENT_EMAIL,
                "password": TEST_PATIENT_PASSWORD
            })
            if response.status_code == 200:
                data = response.json()
                self.patient_token = data["access_token"]
                self.patient_id = data["user"]["id"]
                print(f"✓ Patient logged in successfully (ID: {self.patient_id})")
            else:
                print(f"✗ Patient login failed: {response.text}")
        except Exception as e:
            print(f"✗ Patient login error: {e}")

        # Login as doctor
        try:
            response = await client.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_DOCTOR_EMAIL,
                "password": TEST_DOCTOR_PASSWORD
            })
            if response.status_code == 200:
                data = response.json()
                self.doctor_token = data["access_token"]
                self.doctor_id = data["user"]["id"]
                if data["user"]["doctor_profile"]:
                    self.doctor_profile_id = data["user"]["doctor_profile"]["id"]
                print(f"✓ Doctor logged in successfully (ID: {self.doctor_id}, Profile: {self.doctor_profile_id})")
            else:
                print(f"✗ Doctor login failed: {response.text}")
        except Exception as e:
            print(f"✗ Doctor login error: {e}")

    async def test_doctor_availability(self, client):
        """Test doctor availability checking"""
        print("\n2. Testing doctor availability...")

        if not self.doctor_profile_id:
            print("✗ No doctor profile available for testing")
            return

        tomorrow = (datetime.now() + timedelta(days=1)).date()

        response = await client.get(
            f"{BASE_URL}/appointments/doctors/{self.doctor_profile_id}/availability",
            params={"appointment_date": tomorrow.isoformat()},
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved availability for {data['date']}")
            print(f"  Available slots: {len(data['available_slots'])}")
            if data['available_slots']:
                print(f"  First slot: {data['available_slots'][0]['time']}")
        else:
            print(f"✗ Failed to get availability: {response.text}")

    async def test_appointment_creation(self, client):
        """Test creating a new appointment"""
        print("\n3. Testing appointment creation...")

        if not self.doctor_profile_id:
            print("✗ No doctor profile available for testing")
            return

        tomorrow = (datetime.now() + timedelta(days=1)).date()

        appointment_data = {
            "doctor_id": self.doctor_profile_id,
            "appointment_date": tomorrow.isoformat(),
            "appointment_time": "10:00:00",
            "notes": "Test appointment for system validation"
        }

        response = await client.post(
            f"{BASE_URL}/appointments/",
            json=appointment_data,
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 201:
            data = response.json()
            self.test_appointment_id = data["id"]
            print(f"✓ Appointment created successfully (ID: {self.test_appointment_id})")
            print(f"  Date: {data['appointment_date']}")
            print(f"  Time: {data['appointment_time']}")
            print(f"  Status: {data['status']}")
        else:
            print(f"✗ Failed to create appointment: {response.text}")

    async def test_double_booking_prevention(self, client):
        """Test that double booking is prevented"""
        print("\n4. Testing double booking prevention...")

        if not self.doctor_profile_id:
            print("✗ No doctor profile available for testing")
            return

        tomorrow = (datetime.now() + timedelta(days=1)).date()

        # Try to book the same time slot again
        appointment_data = {
            "doctor_id": self.doctor_profile_id,
            "appointment_date": tomorrow.isoformat(),
            "appointment_time": "10:00:00",
            "notes": "This should fail due to double booking"
        }

        response = await client.post(
            f"{BASE_URL}/appointments/",
            json=appointment_data,
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 400:
            print("✓ Double booking prevention working correctly")
        else:
            print(f"✗ Double booking should have been prevented: {response.status_code}")

    async def test_appointment_retrieval(self, client):
        """Test retrieving appointments"""
        print("\n5. Testing appointment retrieval...")

        # Get all appointments for patient
        response = await client.get(
            f"{BASE_URL}/appointments/",
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 200:
            appointments = response.json()
            print(f"✓ Retrieved {len(appointments)} appointments for patient")
        else:
            print(f"✗ Failed to retrieve appointments: {response.text}")

        # Get specific appointment
        if self.test_appointment_id:
            response = await client.get(
                f"{BASE_URL}/appointments/{self.test_appointment_id}",
                headers={"Authorization": f"Bearer {self.patient_token}"}
            )

            if response.status_code == 200:
                appointment = response.json()
                print(f"✓ Retrieved specific appointment: {appointment['id']}")
            else:
                print(f"✗ Failed to retrieve specific appointment: {response.text}")

    async def test_appointment_updates(self, client):
        """Test updating appointments"""
        print("\n6. Testing appointment updates...")

        if not self.test_appointment_id:
            print("✗ No test appointment available for updating")
            return

        # Update appointment notes
        update_data = {
            "notes": "Updated notes for the appointment"
        }

        response = await client.put(
            f"{BASE_URL}/appointments/{self.test_appointment_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 200:
            appointment = response.json()
            print(f"✓ Appointment updated successfully")
            print(f"  New notes: {appointment['notes']}")
        else:
            print(f"✗ Failed to update appointment: {response.text}")

    async def test_appointment_status_management(self, client):
        """Test appointment status management by doctor"""
        print("\n7. Testing appointment status management...")

        if not self.test_appointment_id or not self.doctor_token:
            print("✗ No test appointment or doctor token available")
            return

        # Doctor confirms appointment
        response = await client.post(
            f"{BASE_URL}/appointments/{self.test_appointment_id}/confirm",
            headers={"Authorization": f"Bearer {self.doctor_token}"}
        )

        if response.status_code == 200:
            appointment = response.json()
            print(f"✓ Appointment confirmed by doctor")
            print(f"  Status: {appointment['status']}")
        else:
            print(f"✗ Failed to confirm appointment: {response.text}")

        # Doctor completes appointment
        response = await client.post(
            f"{BASE_URL}/appointments/{self.test_appointment_id}/complete",
            headers={"Authorization": f"Bearer {self.doctor_token}"}
        )

        if response.status_code == 200:
            appointment = response.json()
            print(f"✓ Appointment completed by doctor")
            print(f"  Status: {appointment['status']}")
        else:
            print(f"✗ Failed to complete appointment: {response.text}")

    async def test_appointment_cancellation(self, client):
        """Test appointment cancellation"""
        print("\n8. Testing appointment cancellation...")

        # Create a new appointment for cancellation test
        if not self.doctor_profile_id:
            print("✗ No doctor profile available for testing")
            return

        tomorrow = (datetime.now() + timedelta(days=2)).date()

        appointment_data = {
            "doctor_id": self.doctor_profile_id,
            "appointment_date": tomorrow.isoformat(),
            "appointment_time": "11:00:00",
            "notes": "Appointment to be cancelled"
        }

        response = await client.post(
            f"{BASE_URL}/appointments/",
            json=appointment_data,
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )

        if response.status_code == 201:
            appointment_id = response.json()["id"]

            # Cancel the appointment
            response = await client.delete(
                f"{BASE_URL}/appointments/{appointment_id}",
                headers={"Authorization": f"Bearer {self.patient_token}"}
            )

            if response.status_code == 200:
                print("✓ Appointment cancelled successfully")
            else:
                print(f"✗ Failed to cancel appointment: {response.text}")
        else:
            print(f"✗ Failed to create appointment for cancellation test: {response.text}")

async def main():
    """Main test runner"""
    tester = AppointmentSystemTester()
    await tester.run_tests()

if __name__ == "__main__":
    print("Appointment System Test Suite")
    print("============================")
    print("Make sure the server is running at http://localhost:8000")
    print("And that you have test users set up:")
    print(f"  Patient: {TEST_PATIENT_EMAIL}")
    print(f"  Doctor: {TEST_DOCTOR_EMAIL}")
    print()

    asyncio.run(main())
