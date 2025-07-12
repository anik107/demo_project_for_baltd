#!/usr/bin/env python3
"""
Test script for the logout functionality
"""

import requests
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def test_logout_functionality():
    """Test the complete login/logout flow"""

    print("🧪 Testing Logout Functionality")
    print("=" * 50)

    # Test data for login
    test_user = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

    print("1. Testing login...")
    try:
        # Login request
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=test_user
        )

        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data["access_token"]
            print(f"✅ Login successful! Token: {access_token[:30]}...")

            # Test logout
            print("\n2. Testing logout...")
            headers = {"Authorization": f"Bearer {access_token}"}

            logout_response = requests.post(
                f"{BASE_URL}/auth/logout",
                headers=headers
            )

            if logout_response.status_code == 200:
                logout_data = logout_response.json()
                print(f"✅ Logout successful! Message: {logout_data['message']}")

                # Test using the token after logout (should fail)
                print("\n3. Testing token after logout (should fail)...")
                test_response = requests.post(
                    f"{BASE_URL}/auth/logout",
                    headers=headers
                )

                if test_response.status_code == 401:
                    print("✅ Token correctly invalidated after logout!")
                else:
                    print(f"❌ Token still valid after logout: {test_response.status_code}")

            else:
                print(f"❌ Logout failed: {logout_response.status_code} - {logout_response.text}")

        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            print("Note: You may need to create a test user first")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_logout_functionality()
    sys.exit(0 if success else 1)
