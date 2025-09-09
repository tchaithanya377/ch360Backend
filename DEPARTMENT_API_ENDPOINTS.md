# Department Management API Endpoints

## Complete List of Available Endpoints

### Base URL: `http://localhost:8000/api/v1/`

---

## 1. Department Management Endpoints

### Core Department Operations
- **GET** `/departments/` - List all departments
- **POST** `/departments/` - Create new department
- **GET** `/departments/{id}/` - Get department details
- **PUT** `/departments/{id}/` - Update department
- **PATCH** `/departments/{id}/` - Partial update department
- **DELETE** `/departments/{id}/` - Delete department

### Department Statistics & Search
- **GET** `/departments/stats/` - Get department statistics
- **POST** `/departments/search/` - Advanced search for departments

### Department Related Data
- **GET** `/departments/{id}/programs/` - Get all programs for a department
- **GET** `/departments/{id}/resources/` - Get all resources for a department
- **GET** `/departments/{id}/announcements/` - Get all announcements for a department
- **GET** `/departments/{id}/events/` - Get all events for a department
- **GET** `/departments/{id}/documents/` - Get all documents for a department
- **POST** `/departments/{id}/update_counts/` - Update faculty and student counts

---

## 2. Department Program Endpoints

### Core Program Operations
- **GET** `/programs/` - List all programs
- **POST** `/programs/` - Create new program
- **GET** `/programs/{id}/` - Get program details
- **PUT** `/programs/{id}/` - Update program
- **PATCH** `/programs/{id}/` - Partial update program
- **DELETE** `/programs/{id}/` - Delete program

### Program Filtering & Search
- **GET** `/programs/?department={id}` - Filter programs by department
- **GET** `/programs/?level={level}` - Filter programs by level
- **GET** `/programs/?status={status}` - Filter programs by status
- **GET** `/programs/?search={query}` - Search programs

---

## 3. Department Resource Endpoints

### Core Resource Operations
- **GET** `/resources/` - List all resources
- **POST** `/resources/` - Create new resource
- **GET** `/resources/{id}/` - Get resource details
- **PUT** `/resources/{id}/` - Update resource
- **PATCH** `/resources/{id}/` - Partial update resource
- **DELETE** `/resources/{id}/` - Delete resource

### Resource Filtering & Search
- **GET** `/resources/?department={id}` - Filter resources by department
- **GET** `/resources/?resource_type={type}` - Filter resources by type
- **GET** `/resources/?status={status}` - Filter resources by status
- **GET** `/resources/?responsible_person={id}` - Filter resources by responsible person
- **GET** `/resources/?search={query}` - Search resources

---

## 4. Department Announcement Endpoints

### Core Announcement Operations
- **GET** `/announcements/` - List all announcements
- **POST** `/announcements/` - Create new announcement
- **GET** `/announcements/{id}/` - Get announcement details
- **PUT** `/announcements/{id}/` - Update announcement
- **PATCH** `/announcements/{id}/` - Partial update announcement
- **DELETE** `/announcements/{id}/` - Delete announcement

### Announcement Filtering & Search
- **GET** `/announcements/?department={id}` - Filter announcements by department
- **GET** `/announcements/?announcement_type={type}` - Filter announcements by type
- **GET** `/announcements/?priority={priority}` - Filter announcements by priority
- **GET** `/announcements/?is_published={true/false}` - Filter published/unpublished announcements
- **GET** `/announcements/?target_audience={audience}` - Filter announcements by target audience
- **GET** `/announcements/?search={query}` - Search announcements

---

## 5. Department Event Endpoints

### Core Event Operations
- **GET** `/events/` - List all events
- **POST** `/events/` - Create new event
- **GET** `/events/{id}/` - Get event details
- **PUT** `/events/{id}/` - Update event
- **PATCH** `/events/{id}/` - Partial update event
- **DELETE** `/events/{id}/` - Delete event

### Event Filtering & Search
- **GET** `/events/?department={id}` - Filter events by department
- **GET** `/events/?event_type={type}` - Filter events by type
- **GET** `/events/?status={status}` - Filter events by status
- **GET** `/events/?is_public={true/false}` - Filter public/private events
- **GET** `/events/?organizer={id}` - Filter events by organizer
- **GET** `/events/?search={query}` - Search events

---

## 6. Department Document Endpoints

### Core Document Operations
- **GET** `/documents/` - List all documents
- **POST** `/documents/` - Create new document
- **GET** `/documents/{id}/` - Get document details
- **PUT** `/documents/{id}/` - Update document
- **PATCH** `/documents/{id}/` - Partial update document
- **DELETE** `/documents/{id}/` - Delete document

### Document Filtering & Search
- **GET** `/documents/?department={id}` - Filter documents by department
- **GET** `/documents/?document_type={type}` - Filter documents by type
- **GET** `/documents/?is_public={true/false}` - Filter public/private documents
- **GET** `/documents/?uploaded_by={id}` - Filter documents by uploader
- **GET** `/documents/?search={query}` - Search documents

---

## 7. Query Parameters & Filtering

### Common Query Parameters
- `page` - Page number for pagination
- `page_size` - Number of items per page (max 100)
- `search` - Search query for text fields
- `ordering` - Order results by field (prefix with `-` for descending)

### Department-Specific Filters
- `department_type` - Filter by department type (ACADEMIC, ADMINISTRATIVE, RESEARCH, SERVICE, SUPPORT)
- `status` - Filter by status (ACTIVE, INACTIVE, SUSPENDED, MERGED, DISSOLVED)
- `is_active` - Filter by active status (true/false)
- `head_of_department` - Filter by head of department ID

### Program-Specific Filters
- `level` - Filter by program level (CERTIFICATE, DIPLOMA, UG, PG, PHD, POST_DOC)
- `status` - Filter by program status (ACTIVE, INACTIVE, SUSPENDED, DISCONTINUED)

### Resource-Specific Filters
- `resource_type` - Filter by resource type (LABORATORY, LIBRARY, EQUIPMENT, SOFTWARE, FACILITY, VEHICLE, OTHER)
- `status` - Filter by resource status (AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_ORDER, RETIRED)

### Announcement-Specific Filters
- `announcement_type` - Filter by type (GENERAL, ACADEMIC, EVENT, DEADLINE, EMERGENCY, MAINTENANCE)
- `priority` - Filter by priority (LOW, MEDIUM, HIGH, URGENT)
- `is_published` - Filter by publication status (true/false)
- `target_audience` - Filter by target audience

### Event-Specific Filters
- `event_type` - Filter by event type (SEMINAR, WORKSHOP, CONFERENCE, MEETING, CELEBRATION, COMPETITION, EXHIBITION, OTHER)
- `status` - Filter by event status (PLANNED, CONFIRMED, ONGOING, COMPLETED, CANCELLED, POSTPONED)
- `is_public` - Filter by public/private status (true/false)

### Document-Specific Filters
- `document_type` - Filter by document type (POLICY, PROCEDURE, FORM, REPORT, MANUAL, GUIDELINE, CERTIFICATE, OTHER)
- `is_public` - Filter by public/private status (true/false)

---

## 8. Request/Response Examples

### Create Department
```bash
POST /api/v1/departments/
Content-Type: application/json

{
    "name": "Computer Science",
    "short_name": "CS",
    "code": "CS001",
    "department_type": "ACADEMIC",
    "email": "cs@university.edu",
    "phone": "+1234567890",
    "building": "Engineering Building",
    "address_line1": "123 University Ave",
    "city": "University City",
    "state": "State",
    "postal_code": "12345",
    "country": "Country",
    "established_date": "2020-01-01",
    "description": "Department of Computer Science"
}
```

### Search Departments
```bash
POST /api/v1/departments/search/
Content-Type: application/json

{
    "query": "Computer",
    "department_type": "ACADEMIC",
    "status": "ACTIVE",
    "is_active": true
}
```

### Get Department Statistics
```bash
GET /api/v1/departments/stats/
```

Response:
```json
{
    "total_departments": 10,
    "active_departments": 8,
    "academic_departments": 6,
    "administrative_departments": 2,
    "research_departments": 2,
    "total_faculty": 150,
    "total_students": 1200,
    "total_programs": 25,
    "total_resources": 50,
    "upcoming_events": 5,
    "active_announcements": 12
}
```

---

## 9. Authentication & Permissions

### Authentication
All endpoints require authentication. Use JWT tokens:
```bash
Authorization: Bearer <your-jwt-token>
```

### Permission Levels
- **Superuser/Staff**: Full access to all operations
- **Department Head**: Can manage their own department
- **Faculty**: Can view their department and sub-departments
- **Students**: Can view their own department
- **Regular Users**: Can view active departments only

---

## 10. Error Responses

### Common HTTP Status Codes
- `200` - OK (successful GET, PUT, PATCH)
- `201` - Created (successful POST)
- `204` - No Content (successful DELETE)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

### Error Response Format
```json
{
    "error": "Error message",
    "details": {
        "field_name": ["Specific error message"]
    }
}
```

---

## 11. Pagination

All list endpoints support pagination:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/v1/departments/?page=2",
    "previous": null,
    "results": [...]
}
```

---

## 12. File Uploads

For document uploads, use multipart/form-data:
```bash
POST /api/v1/documents/
Content-Type: multipart/form-data

{
    "department": "department-uuid",
    "title": "Document Title",
    "document_type": "POLICY",
    "file": <file-data>
}
```

---

## 13. Testing the API

### Using curl
```bash
# Get all departments
curl -X GET http://localhost:8000/api/v1/departments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"

# Create a department
curl -X POST http://localhost:8000/api/v1/departments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Department", "short_name": "TEST", ...}'
```

### Using Python requests
```python
import requests

headers = {
    'Authorization': 'Bearer <your-token>',
    'Content-Type': 'application/json'
}

# Get departments
response = requests.get('http://localhost:8000/api/v1/departments/', headers=headers)
departments = response.json()

# Create department
data = {
    "name": "Test Department",
    "short_name": "TEST",
    # ... other fields
}
response = requests.post('http://localhost:8000/api/v1/departments/', 
                        headers=headers, json=data)
```

---

## 14. Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 1000 requests per hour per user
- 100 requests per minute per user

---

## 15. API Versioning

Current API version: v1
- Base URL: `/api/v1/`
- Future versions will be available at `/api/v2/`, etc.

---

This comprehensive list covers all available endpoints in the Department Management API. Each endpoint supports various HTTP methods and query parameters for flexible data access and manipulation.
