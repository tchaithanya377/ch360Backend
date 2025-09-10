#!/usr/bin/env python3
"""
Quick server connection test for Postman setup
"""
import requests
import json

def test_server_connection():
    """Test if Django server is running and accessible"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing CampusHub360 Server Connection")
    print("=" * 50)
    
    # Test 1: Basic health check
    try:
        response = requests.get(f"{base_url}/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health Check: FAILED (Error: {e})")
        return False
    
    # Test 2: API health check
    try:
        response = requests.get(f"{base_url}/api/health/", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
    
    # Test 3: Admin login
    try:
        response = requests.post(
            f"{base_url}/api/auth/token/",
            json={
                "username": "admin@gmail.com",
                "password": "123456"
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin Login: PASSED")
            print(f"   Access Token: {data.get('access', 'N/A')[:50]}...")
            print(f"   User: {data.get('user', {})}")
            print(f"   Session: {data.get('session', {})}")
        else:
            print(f"❌ Admin Login: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Admin Login: FAILED (Error: {e})")
    
    # Test 4: User registration
    try:
        response = requests.post(
            f"{base_url}/api/accounts/register/",
            json={
                "username": "postman_test_user",
                "email": "postman_test_user@example.com",
                "password": "TestPass123!",
                "is_verified": True
            },
            timeout=5
        )
        if response.status_code == 201:
            print("✅ User Registration: PASSED")
            print(f"   User ID: {response.json().get('id', 'N/A')}")
        else:
            print(f"❌ User Registration: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User Registration: FAILED (Error: {e})")
    
    print("\n🎯 Postman Setup Instructions:")
    print("1. Import CampusHub360_Postman_Collection.json")
    print("2. Set base_url to http://localhost:8000")
    print("3. Start testing with Authentication → Login (Email)")
    print("4. Follow the POSTMAN_TESTING_GUIDE.md")
    
    return True

if __name__ == "__main__":
    test_server_connection()
