#!/usr/bin/env python
"""
Simple API test script for Department Management endpoints
"""
import requests
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000/api/v1/departments"
    
    print("🚀 Testing Department Management API Endpoints")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("GET", "/", "List all departments"),
        ("GET", "/stats/", "Get department statistics"),
        ("GET", "/programs/", "List all programs"),
        ("GET", "/resources/", "List all resources"),
        ("GET", "/announcements/", "List all announcements"),
        ("GET", "/events/", "List all events"),
        ("GET", "/documents/", "List all documents"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing {method} {endpoint}")
            print(f"   Description: {description}")
            
            response = requests.get(url, timeout=5)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print(f"   ✅ Success: {len(data['results'])} items found")
                elif isinstance(data, dict):
                    print(f"   ✅ Success: {len(data)} fields in response")
                else:
                    print(f"   ✅ Success: Response received")
            elif response.status_code == 401:
                print(f"   🔒 Authentication required (expected)")
            elif response.status_code == 404:
                print(f"   ❌ Not Found: Endpoint may not be configured")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Server may not be running")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout: Server took too long to respond")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ API Testing Complete!")

if __name__ == "__main__":
    test_endpoints()
