#!/usr/bin/env python
"""
Test script for Department Management API endpoints
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campshub360.settings')
os.environ.setdefault('SECRET_KEY', 'your-secret-key-here-for-development-only-change-in-production-this-is-a-very-long-secret-key-for-development')
os.environ.setdefault('DEBUG', 'True')

django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from departments.models import Department, DepartmentResource, DepartmentAnnouncement, DepartmentEvent, DepartmentDocument
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class DepartmentAPITest:
    def __init__(self):
        self.client = APIClient()
        self.base_url = "http://localhost:8000/api/v1"
        self.test_data = self.create_test_data()
        
    def create_test_data(self):
        """Create test data for API testing"""
        return {
            'department': {
                'name': 'Computer Science',
                'short_name': 'CS',
                'code': 'CS001',
                'department_type': 'ACADEMIC',
                'email': 'cs@university.edu',
                'phone': '+1234567890',
                'building': 'Engineering Building',
                'address_line1': '123 University Ave',
                'city': 'University City',
                'state': 'State',
                'postal_code': '12345',
                'country': 'Country',
                'established_date': '2020-01-01',
                'description': 'Department of Computer Science'
            },
            'resource': {
                'name': 'Computer Lab 1',
                'resource_type': 'LABORATORY',
                'description': 'Main computer laboratory',
                'location': 'Engineering Building Room 101',
                'status': 'AVAILABLE'
            },
            'announcement': {
                'title': 'Welcome to New Semester',
                'content': 'Welcome all students to the new semester',
                'announcement_type': 'GENERAL',
                'priority': 'MEDIUM',
                'target_audience': 'ALL'
            },
            'event': {
                'title': 'Department Meeting',
                'description': 'Monthly department meeting',
                'event_type': 'MEETING',
                'start_date': '2024-02-01T10:00:00Z',
                'end_date': '2024-02-01T11:00:00Z',
                'location': 'Conference Room A',
                'status': 'PLANNED'
            }
        }
    
    def test_department_endpoints(self):
        """Test all department-related endpoints"""
        print("🔍 Testing Department Endpoints...")
        
        # Test 1: List departments (GET)
        print("\n1. Testing GET /api/v1/departments/")
        try:
            response = self.client.get(f"{self.base_url}/departments/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {len(response.data.get('results', []))} departments found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 2: Create department (POST)
        print("\n2. Testing POST /api/v1/departments/")
        try:
            response = self.client.post(f"{self.base_url}/departments/", 
                                      data=json.dumps(self.test_data['department']),
                                      content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   Department created: {response.data.get('name')}")
                self.department_id = response.data.get('id')
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 3: Get department details (GET)
        if hasattr(self, 'department_id'):
            print(f"\n3. Testing GET /api/v1/departments/{self.department_id}/")
            try:
                response = self.client.get(f"{self.base_url}/departments/{self.department_id}/")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Department: {response.data.get('name')}")
                else:
                    print(f"   Error: {response.data}")
            except Exception as e:
                print(f"   Error: {str(e)}")
        
        # Test 4: Update department (PUT)
        if hasattr(self, 'department_id'):
            print(f"\n4. Testing PUT /api/v1/departments/{self.department_id}/")
            try:
                update_data = self.test_data['department'].copy()
                update_data['description'] = 'Updated Department of Computer Science'
                response = self.client.put(f"{self.base_url}/departments/{self.department_id}/",
                                         data=json.dumps(update_data),
                                         content_type='application/json')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Department updated: {response.data.get('description')}")
                else:
                    print(f"   Error: {response.data}")
            except Exception as e:
                print(f"   Error: {str(e)}")
        
        # Test 5: Department statistics
        print("\n5. Testing GET /api/v1/departments/stats/")
        try:
            response = self.client.get(f"{self.base_url}/departments/stats/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Stats: {response.data}")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 6: Department search
        print("\n6. Testing POST /api/v1/departments/search/")
        try:
            search_data = {'query': 'Computer', 'department_type': 'ACADEMIC'}
            response = self.client.post(f"{self.base_url}/departments/search/",
                                      data=json.dumps(search_data),
                                      content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Search results: {len(response.data.get('results', []))} found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    def test_resource_endpoints(self):
        """Test department resource endpoints"""
        print("\n🔍 Testing Department Resource Endpoints...")
        
        if not hasattr(self, 'department_id'):
            print("   Skipping - No department ID available")
            return
        
        # Test 1: List resources
        print("\n1. Testing GET /api/v1/resources/")
        try:
            response = self.client.get(f"{self.base_url}/resources/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {len(response.data.get('results', []))} resources found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 2: Create resource
        print("\n2. Testing POST /api/v1/resources/")
        try:
            resource_data = self.test_data['resource'].copy()
            resource_data['department'] = self.department_id
            response = self.client.post(f"{self.base_url}/resources/",
                                      data=json.dumps(resource_data),
                                      content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   Resource created: {response.data.get('name')}")
                self.resource_id = response.data.get('id')
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 3: Get department resources
        print(f"\n3. Testing GET /api/v1/departments/{self.department_id}/resources/")
        try:
            response = self.client.get(f"{self.base_url}/departments/{self.department_id}/resources/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Resources: {len(response.data)} found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    def test_announcement_endpoints(self):
        """Test department announcement endpoints"""
        print("\n🔍 Testing Department Announcement Endpoints...")
        
        if not hasattr(self, 'department_id'):
            print("   Skipping - No department ID available")
            return
        
        # Test 1: List announcements
        print("\n1. Testing GET /api/v1/announcements/")
        try:
            response = self.client.get(f"{self.base_url}/announcements/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {len(response.data.get('results', []))} announcements found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 2: Create announcement
        print("\n2. Testing POST /api/v1/announcements/")
        try:
            announcement_data = self.test_data['announcement'].copy()
            announcement_data['department'] = self.department_id
            response = self.client.post(f"{self.base_url}/announcements/",
                                      data=json.dumps(announcement_data),
                                      content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   Announcement created: {response.data.get('title')}")
                self.announcement_id = response.data.get('id')
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 3: Get department announcements
        print(f"\n3. Testing GET /api/v1/departments/{self.department_id}/announcements/")
        try:
            response = self.client.get(f"{self.base_url}/departments/{self.department_id}/announcements/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Announcements: {len(response.data)} found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    def test_event_endpoints(self):
        """Test department event endpoints"""
        print("\n🔍 Testing Department Event Endpoints...")
        
        if not hasattr(self, 'department_id'):
            print("   Skipping - No department ID available")
            return
        
        # Test 1: List events
        print("\n1. Testing GET /api/v1/events/")
        try:
            response = self.client.get(f"{self.base_url}/events/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {len(response.data.get('results', []))} events found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 2: Create event
        print("\n2. Testing POST /api/v1/events/")
        try:
            event_data = self.test_data['event'].copy()
            event_data['department'] = self.department_id
            response = self.client.post(f"{self.base_url}/events/",
                                      data=json.dumps(event_data),
                                      content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   Event created: {response.data.get('title')}")
                self.event_id = response.data.get('id')
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 3: Get department events
        print(f"\n3. Testing GET /api/v1/departments/{self.department_id}/events/")
        try:
            response = self.client.get(f"{self.base_url}/departments/{self.department_id}/events/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Events: {len(response.data)} found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    def test_document_endpoints(self):
        """Test department document endpoints"""
        print("\n🔍 Testing Department Document Endpoints...")
        
        if not hasattr(self, 'department_id'):
            print("   Skipping - No department ID available")
            return
        
        # Test 1: List documents
        print("\n1. Testing GET /api/v1/documents/")
        try:
            response = self.client.get(f"{self.base_url}/documents/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {len(response.data.get('results', []))} documents found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 2: Get department documents
        print(f"\n2. Testing GET /api/v1/departments/{self.department_id}/documents/")
        try:
            response = self.client.get(f"{self.base_url}/departments/{self.department_id}/documents/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Documents: {len(response.data)} found")
            else:
                print(f"   Error: {response.data}")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Department Management API Tests")
        print("=" * 60)
        
        self.test_department_endpoints()
        self.test_resource_endpoints()
        self.test_announcement_endpoints()
        self.test_event_endpoints()
        self.test_document_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ API Testing Complete!")

if __name__ == "__main__":
    tester = DepartmentAPITest()
    tester.run_all_tests()
