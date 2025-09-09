# Department Management API - Complete Endpoints Summary

## 🎯 All Available API Endpoints

### Base URL: `http://localhost:8000/api/v1/`

---

## 📋 Department Management (Main Endpoints)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/departments/` | List all departments | ✅ |
| POST | `/departments/` | Create new department | ✅ |
| GET | `/departments/{id}/` | Get department details | ✅ |
| PUT | `/departments/{id}/` | Update department | ✅ |
| PATCH | `/departments/{id}/` | Partial update department | ✅ |
| DELETE | `/departments/{id}/` | Delete department | ✅ |
| GET | `/departments/stats/` | Get department statistics | ✅ |
| POST | `/departments/search/` | Advanced search | ✅ |
| POST | `/departments/{id}/update_counts/` | Update faculty/student counts | ✅ |

### Department Related Data Endpoints
| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/departments/{id}/programs/` | Get department programs | ✅ |
| GET | `/departments/{id}/resources/` | Get department resources | ✅ |
| GET | `/departments/{id}/announcements/` | Get department announcements | ✅ |
| GET | `/departments/{id}/events/` | Get department events | ✅ |
| GET | `/departments/{id}/documents/` | Get department documents | ✅ |

---

## 🎓 Department Programs

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/programs/` | List all programs | ✅ |
| POST | `/programs/` | Create new program | ✅ |
| GET | `/programs/{id}/` | Get program details | ✅ |
| PUT | `/programs/{id}/` | Update program | ✅ |
| PATCH | `/programs/{id}/` | Partial update program | ✅ |
| DELETE | `/programs/{id}/` | Delete program | ✅ |

---

## 🏢 Department Resources

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/resources/` | List all resources | ✅ |
| POST | `/resources/` | Create new resource | ✅ |
| GET | `/resources/{id}/` | Get resource details | ✅ |
| PUT | `/resources/{id}/` | Update resource | ✅ |
| PATCH | `/resources/{id}/` | Partial update resource | ✅ |
| DELETE | `/resources/{id}/` | Delete resource | ✅ |

---

## 📢 Department Announcements

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/announcements/` | List all announcements | ✅ |
| POST | `/announcements/` | Create new announcement | ✅ |
| GET | `/announcements/{id}/` | Get announcement details | ✅ |
| PUT | `/announcements/{id}/` | Update announcement | ✅ |
| PATCH | `/announcements/{id}/` | Partial update announcement | ✅ |
| DELETE | `/announcements/{id}/` | Delete announcement | ✅ |

---

## 📅 Department Events

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/events/` | List all events | ✅ |
| POST | `/events/` | Create new event | ✅ |
| GET | `/events/{id}/` | Get event details | ✅ |
| PUT | `/events/{id}/` | Update event | ✅ |
| PATCH | `/events/{id}/` | Partial update event | ✅ |
| DELETE | `/events/{id}/` | Delete event | ✅ |

---

## 📄 Department Documents

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/documents/` | List all documents | ✅ |
| POST | `/documents/` | Create new document | ✅ |
| GET | `/documents/{id}/` | Get document details | ✅ |
| PUT | `/documents/{id}/` | Update document | ✅ |
| PATCH | `/documents/{id}/` | Partial update document | ✅ |
| DELETE | `/documents/{id}/` | Delete document | ✅ |

---

## 🔍 Query Parameters & Filtering

### Common Parameters (All Endpoints)
- `page` - Page number for pagination
- `page_size` - Items per page (max 100)
- `search` - Text search across relevant fields
- `ordering` - Sort by field (prefix `-` for descending)

### Department Filters
- `department_type` - ACADEMIC, ADMINISTRATIVE, RESEARCH, SERVICE, SUPPORT
- `status` - ACTIVE, INACTIVE, SUSPENDED, MERGED, DISSOLVED
- `is_active` - true/false
- `head_of_department` - Filter by head ID

### Program Filters
- `department` - Filter by department ID
- `level` - CERTIFICATE, DIPLOMA, UG, PG, PHD, POST_DOC
- `status` - ACTIVE, INACTIVE, SUSPENDED, DISCONTINUED
- `is_active` - true/false

### Resource Filters
- `department` - Filter by department ID
- `resource_type` - LABORATORY, LIBRARY, EQUIPMENT, SOFTWARE, FACILITY, VEHICLE, OTHER
- `status` - AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_ORDER, RETIRED
- `responsible_person` - Filter by responsible person ID

### Announcement Filters
- `department` - Filter by department ID
- `announcement_type` - GENERAL, ACADEMIC, EVENT, DEADLINE, EMERGENCY, MAINTENANCE
- `priority` - LOW, MEDIUM, HIGH, URGENT
- `is_published` - true/false
- `target_audience` - ALL, FACULTY, STUDENTS, etc.

### Event Filters
- `department` - Filter by department ID
- `event_type` - SEMINAR, WORKSHOP, CONFERENCE, MEETING, CELEBRATION, COMPETITION, EXHIBITION, OTHER
- `status` - PLANNED, CONFIRMED, ONGOING, COMPLETED, CANCELLED, POSTPONED
- `is_public` - true/false
- `organizer` - Filter by organizer ID

### Document Filters
- `department` - Filter by department ID
- `document_type` - POLICY, PROCEDURE, FORM, REPORT, MANUAL, GUIDELINE, CERTIFICATE, OTHER
- `is_public` - true/false
- `uploaded_by` - Filter by uploader ID

---

## 📝 Example API Calls

### 1. Get All Departments
```bash
GET http://localhost:8000/api/v1/departments/
```

### 2. Create a Department
```bash
POST http://localhost:8000/api/v1/departments/
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

### 3. Search Departments
```bash
POST http://localhost:8000/api/v1/departments/search/
Content-Type: application/json

{
    "query": "Computer",
    "department_type": "ACADEMIC",
    "status": "ACTIVE"
}
```

### 4. Get Department Statistics
```bash
GET http://localhost:8000/api/v1/departments/stats/
```

### 5. Get Department Programs
```bash
GET http://localhost:8000/api/v1/departments/{department_id}/programs/
```

### 6. Create a Program
```bash
POST http://localhost:8000/api/v1/programs/
Content-Type: application/json

{
    "department": "department-uuid",
    "name": "Bachelor of Computer Science",
    "short_name": "BCS",
    "code": "BCS001",
    "level": "UG",
    "duration_years": 4,
    "total_credits": 120,
    "description": "Undergraduate program in Computer Science",
    "eligibility_criteria": "High school diploma or equivalent",
    "established_date": "2020-01-01"
}
```

### 7. Filter Resources by Type
```bash
GET http://localhost:8000/api/v1/resources/?resource_type=LABORATORY&department={department_id}
```

### 8. Get Published Announcements
```bash
GET http://localhost:8000/api/v1/announcements/?is_published=true&department={department_id}
```

### 9. Get Upcoming Events
```bash
GET http://localhost:8000/api/v1/events/?status=PLANNED&is_public=true
```

### 10. Upload Document
```bash
POST http://localhost:8000/api/v1/documents/
Content-Type: multipart/form-data

{
    "department": "department-uuid",
    "title": "Department Policy",
    "document_type": "POLICY",
    "file": <file-data>
}
```

---

## 🔐 Authentication & Permissions

### Authentication Required
All endpoints require JWT authentication:
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

## 📊 Response Formats

### Success Response (200/201)
```json
{
    "id": "uuid",
    "name": "Department Name",
    "short_name": "DEPT",
    "code": "DEPT001",
    "department_type": "ACADEMIC",
    "status": "ACTIVE",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Paginated Response
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/v1/departments/?page=2",
    "previous": null,
    "results": [...]
}
```

### Error Response
```json
{
    "error": "Error message",
    "details": {
        "field_name": ["Specific error message"]
    }
}
```

---

## 🚀 Quick Start Guide

### 1. Start the Server
```bash
python manage.py runserver 8000
```

### 2. Test Basic Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/departments/
```

### 3. Create a Department
```bash
curl -X POST http://localhost:8000/api/v1/departments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Department", "short_name": "TEST", "code": "TEST001", ...}'
```

### 4. Get Statistics
```bash
curl -X GET http://localhost:8000/api/v1/departments/stats/
```

---

## ✅ All Endpoints Status: WORKING

The Department Management API is fully functional with:
- ✅ 35+ endpoints across 6 main resource types
- ✅ Complete CRUD operations
- ✅ Advanced filtering and search
- ✅ Pagination support
- ✅ File upload capabilities
- ✅ Role-based permissions
- ✅ Comprehensive validation
- ✅ Error handling
- ✅ Documentation

**Total Endpoints: 35+**
**Status: All Working ✅**
