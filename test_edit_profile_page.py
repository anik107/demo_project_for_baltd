#!/usr/bin/env python3
"""
Test script for the edit profile functionality
"""

import requests

BASE_URL = "http://localhost:8000"

def test_edit_profile_page():
    """Test that the edit profile page loads correctly"""

    # First, let's try to register a test user
    register_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "mobile_number": "+8801234567890",
        "password": "TestPass123!",
        "division_id": 1,
        "district_id": 1,
        "thana_id": 1
    }

    try:
        # Register user
        print("Testing user registration...")
        register_response = requests.post(f"{BASE_URL}/api/signup", data=register_data)
        print(f"Registration status: {register_response.status_code}")

        if register_response.status_code in [200, 201]:
            print("✓ User registration successful")
        elif register_response.status_code == 400:
            print("⚠ User might already exist, proceeding with login...")
        else:
            print(f"✗ Registration failed: {register_response.text}")
            return

        # Login
        print("\nTesting user login...")
        login_data = {
            "username": "testuser@example.com",
            "password": "TestPass123!"
        }

        login_response = requests.post(f"{BASE_URL}/api/login", data=login_data)
        print(f"Login status: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"✗ Login failed: {login_response.text}")
            return

        print("✓ Login successful")

        # Get cookies from login response
        cookies = login_response.cookies

        # Get user info to find user ID
        print("\nGetting user information...")
        dashboard_response = requests.get(f"{BASE_URL}/dashboard", cookies=cookies)
        print(f"Dashboard access status: {dashboard_response.status_code}")

        if dashboard_response.status_code != 200:
            print(f"✗ Dashboard access failed: {dashboard_response.text}")
            return

        print("✓ Dashboard access successful")

        # Try to access edit profile page (we'll use user ID 1 for testing)
        print("\nTesting edit profile page access...")
        edit_profile_response = requests.get(f"{BASE_URL}/api/users/1/edit", cookies=cookies)
        print(f"Edit profile page status: {edit_profile_response.status_code}")

        if edit_profile_response.status_code == 200:
            print("✓ Edit profile page loads successfully")

            # Check if the page contains expected elements
            content = edit_profile_response.text
            expected_elements = [
                "Edit Profile",
                "full_name",
                "email",
                "mobile_number",
                "division_id",
                "district_id",
                "thana_id",
                "profile_image",
                "Update Profile"
            ]

            missing_elements = []
            for element in expected_elements:
                if element not in content:
                    missing_elements.append(element)

            if not missing_elements:
                print("✓ All expected form elements are present")
            else:
                print(f"⚠ Missing elements: {missing_elements}")

        elif edit_profile_response.status_code == 401:
            print("✗ Authentication failed - check cookie handling")
        elif edit_profile_response.status_code == 403:
            print("✗ Access forbidden - check user permissions")
        elif edit_profile_response.status_code == 404:
            print("✗ User not found - check user ID")
        else:
            print(f"✗ Edit profile page failed: {edit_profile_response.status_code}")
            print(f"Response: {edit_profile_response.text}")

    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")

if __name__ == "__main__":
    print("=== Edit Profile Page Test ===")
    test_edit_profile_page()
    print("\n=== Test Complete ===")
