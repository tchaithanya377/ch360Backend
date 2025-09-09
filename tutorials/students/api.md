# Students API Guide

This guide explains how to use the Students APIs: endpoints, request/response formats, and examples.

> Base path: `/api/students/`
> All endpoints require Authorization header (Bearer token or session auth).

## List students
GET `/api/students/`

Query params: `search`, `ordering`, `page`, filter fields from `StudentFilter`.

Example:
```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/students/?search=john&ordering=-created_at"
```

Response: paginated list of students using `StudentSerializer`.

## Retrieve a student
GET `/api/students/{id}/`

Returns detailed student using `StudentDetailSerializer`.

## Create a student
POST `/api/students/`

Body (JSON): minimal example
```json
{
  "roll_number": "22CSE001",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "2004-05-12",
  "gender": "M",
  "section": "A",
  "academic_year": "2024-2025"
}
```
Notes:
- `roll_number` unique
- `email` unique if provided

## Update/Partial update
PUT/PATCH `/api/students/{id}/`

## Delete
DELETE `/api/students/{id}/`

## Search
GET `/api/students/search/?q=...`

Returns up to 20 items with basic student fields.

## Stats
GET `/api/students/stats/`

Aggregated statistics of students.

## Documents of a student
GET `/api/students/{id}/documents/`

## Enrollment history of a student
GET `/api/students/{id}/enrollment-history/`

## Custom fields of a student
GET `/api/students/{id}/custom-fields/`

## Create login for a student
POST `/api/students/{id}/create-login/`

Creates auth user for the student if missing.

## Custom Fields
- List/Create/Update/Delete: `/api/custom-fields/`
- Types: GET `/api/custom-fields/types/`
- Stats: GET `/api/custom-fields/stats/`

## Custom Field Values
- CRUD: `/api/custom-field-values/`
- By student: GET `/api/custom-field-values/by-student/?student_id=...`
- By field: GET `/api/custom-field-values/by-field/?field_id=...`

## Bulk Operations
### Bulk create
POST `/api/students/bulk-create/`
```json
{
  "students": [
    {"roll_number": "22CSE002", "first_name": "Alice", "last_name": "W", "date_of_birth": "2004-01-01", "gender": "F"}
  ]
}
```

### Bulk update
POST `/api/students/bulk-update/`
```json
{
  "updates": [
    {"roll_number": "22CSE002", "section": "B"}
  ]
}
```

### Bulk delete
DELETE `/api/students/bulk-delete/`
```json
{
  "roll_numbers": ["22CSE002", "22CSE003"]
}
```

## Imports
GET `/api/imports/` and GET `/api/imports/stats/`

---
See `fields.md` for field-level reference and `frontend.md` for integration.
