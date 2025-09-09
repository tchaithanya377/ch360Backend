### All API Endpoints

Below is a consolidated list of API endpoints, grouped by app and prefixed by their root from `campshub360/urls.py`.

Note: DRF viewsets expose standard actions (list, retrieve, create, update, partial_update, destroy) under the listed prefixes unless otherwise specified.

---

## Auth (JWT)
- POST /api/auth/token/
- POST /api/auth/token/refresh/

## Accounts (`/api/accounts/`)
- POST /api/accounts/register/
- GET /api/accounts/me/
- POST /api/accounts/logout/
- POST /api/accounts/token/
- POST /api/accounts/token/refresh/
- GET /api/accounts/me/roles-permissions/

## Students API (`/api/v1/students/` → includes `students/api_urls.py`)
- [ViewSet] /api/v1/students/students/
- [ViewSet] /api/v1/students/enrollment-history/
- [ViewSet] /api/v1/students/documents/
- [ViewSet] /api/v1/students/custom-fields/
- [ViewSet] /api/v1/students/custom-field-values/
- [ViewSet] /api/v1/students/imports/
- GET /api/v1/students/students/<uuid:pk>/documents/
- GET /api/v1/students/students/<uuid:pk>/enrollment-history/
- GET /api/v1/students/students/<uuid:pk>/custom-fields/
- POST /api/v1/students/students/<uuid:pk>/create-login/
- POST /api/v1/students/students/bulk-create/
- POST /api/v1/students/students/bulk-update/
- DELETE /api/v1/students/students/bulk-delete/
- GET /api/v1/students/students/stats/
- GET /api/v1/students/custom-fields/stats/
- GET /api/v1/students/imports/stats/
- GET /api/v1/students/students/search/
- GET /api/v1/students/custom-fields/types/
- GET /api/v1/students/custom-field-values/by-student/
- GET /api/v1/students/custom-field-values/by-field/

## Faculty (`/api/v1/faculty/`)
- [ViewSet] /api/v1/faculty/api/faculty/
- [ViewSet] /api/v1/faculty/api/subjects/
- [ViewSet] /api/v1/faculty/api/schedules/
- [ViewSet] /api/v1/faculty/api/leaves/
- [ViewSet] /api/v1/faculty/api/performance/
- [ViewSet] /api/v1/faculty/api/documents/
- [ViewSet] /api/v1/faculty/api/custom-fields/
- [ViewSet] /api/v1/faculty/api/custom-field-values/

## Academics (`/api/v1/academics/`)
- [ViewSet] /api/v1/academics/api/courses/
- [ViewSet] /api/v1/academics/api/syllabi/
- [ViewSet] /api/v1/academics/api/syllabus-topics/
- [ViewSet] /api/v1/academics/api/timetables/
- [ViewSet] /api/v1/academics/api/enrollments/
- [ViewSet] /api/v1/academics/api/academic-calendar/

## Departments (`/api/v1/departments/`)
- [ViewSet] /api/v1/departments/
- [ViewSet] /api/v1/departments/resources/
- [ViewSet] /api/v1/departments/announcements/
- [ViewSet] /api/v1/departments/events/
- [ViewSet] /api/v1/departments/documents/

## Attendance (`/api/v1/attendance/`)
- [ViewSet] /api/v1/attendance/attendance/sessions/
- [ViewSet] /api/v1/attendance/attendance/records/

## Placements (`/api/v1/placements/`)
- [ViewSet] /api/v1/placements/api/companies/
- [ViewSet] /api/v1/placements/api/jobs/
- [ViewSet] /api/v1/placements/api/applications/
- [ViewSet] /api/v1/placements/api/drives/
- [ViewSet] /api/v1/placements/api/rounds/
- [ViewSet] /api/v1/placements/api/offers/

## Grads (`/api/v1/grads/`)
- GET /api/v1/grads/health/
- [ViewSet] /api/v1/grads/
- [ViewSet] /api/v1/grads/grade-scales/
- [ViewSet] /api/v1/grads/terms/
- [ViewSet] /api/v1/grads/course-results/
- [ViewSet] /api/v1/grads/term-gpa/
- [ViewSet] /api/v1/grads/graduates/

## RnD (`/api/v1/rnd/`)
- [ViewSet] /api/v1/rnd/researchers/
- [ViewSet] /api/v1/rnd/grants/
- [ViewSet] /api/v1/rnd/projects/
- [ViewSet] /api/v1/rnd/publications/
- [ViewSet] /api/v1/rnd/patents/
- [ViewSet] /api/v1/rnd/datasets/
- [ViewSet] /api/v1/rnd/collaborations/

## Facilities (`/api/v1/facilities/`)
- (No DRF routes registered in `facilities/urls.py` for API prefix; facility dashboard pages are mounted elsewhere)

## Exams (`/api/v1/exams/`)
- [ViewSet] /api/v1/exams/api/exam-sessions/
- [ViewSet] /api/v1/exams/api/exam-schedules/
- [ViewSet] /api/v1/exams/api/exam-rooms/
- [ViewSet] /api/v1/exams/api/room-allocations/
- [ViewSet] /api/v1/exams/api/staff-assignments/
- [ViewSet] /api/v1/exams/api/student-dues/
- [ViewSet] /api/v1/exams/api/exam-registrations/
- [ViewSet] /api/v1/exams/api/hall-tickets/
- [ViewSet] /api/v1/exams/api/exam-attendance/
- [ViewSet] /api/v1/exams/api/exam-violations/
- [ViewSet] /api/v1/exams/api/exam-results/
- GET /api/v1/exams/api/dashboard/stats/
- GET /api/v1/exams/api/reports/exam-summary/
- GET /api/v1/exams/api/reports/student-performance/
- POST /api/v1/exams/api/bulk-operations/generate-hall-tickets/
- POST /api/v1/exams/api/bulk-operations/assign-rooms/
- POST /api/v1/exams/api/bulk-operations/assign-staff/

## Fees (`/api/v1/fees/`)
- [ViewSet] /api/v1/fees/api/categories/
- [ViewSet] /api/v1/fees/api/structures/
- [ViewSet] /api/v1/fees/api/structure-details/
- [ViewSet] /api/v1/fees/api/student-fees/
- [ViewSet] /api/v1/fees/api/payments/
- [ViewSet] /api/v1/fees/api/waivers/
- [ViewSet] /api/v1/fees/api/discounts/
- [ViewSet] /api/v1/fees/api/receipts/

## Transportation (`/api/v1/transport/`)
- [ViewSet] /api/v1/transport/vehicles/
- [ViewSet] /api/v1/transport/drivers/
- [ViewSet] /api/v1/transport/stops/
- [ViewSet] /api/v1/transport/routes/
- [ViewSet] /api/v1/transport/route-stops/
- [ViewSet] /api/v1/transport/assignments/
- [ViewSet] /api/v1/transport/schedules/
- [ViewSet] /api/v1/transport/passes/

## Mentoring (`/api/v1/mentoring/`)
- [ViewSet] /api/v1/mentoring/mentorships/
- [ViewSet] /api/v1/mentoring/projects/
- [ViewSet] /api/v1/mentoring/meetings/
- [ViewSet] /api/v1/mentoring/feedback/

## Feedback (`/api/v1/feedback/`)
- [ViewSet] /api/v1/feedback/categories/
- [ViewSet] /api/v1/feedback/tags/
- [ViewSet] /api/v1/feedback/items/
- [ViewSet] /api/v1/feedback/comments/
- [ViewSet] /api/v1/feedback/attachments/
- [ViewSet] /api/v1/feedback/votes/

## Open Requests (`/api/v1/open-requests/`)
- GET /api/v1/open-requests/health/
- GET, POST /api/v1/open-requests/requests/
- GET, PUT, PATCH, DELETE /api/v1/open-requests/requests/<int:pk>/
- GET, POST /api/v1/open-requests/requests/<int:request_id>/comments/

## Assignments (`/api/v1/assignments/`)
- GET, POST /api/v1/assignments/categories/
- GET, PUT, PATCH, DELETE /api/v1/assignments/categories/<uuid:pk>/
- GET, POST /api/v1/assignments/templates/
- GET, PUT, PATCH, DELETE /api/v1/assignments/templates/<uuid:pk>/
- GET, POST /api/v1/assignments/
- GET, PUT, PATCH, DELETE /api/v1/assignments/<uuid:pk>/
- GET /api/v1/assignments/my-assignments/
- POST /api/v1/assignments/<uuid:assignment_id>/publish/
- POST /api/v1/assignments/<uuid:assignment_id>/close/
- GET, POST /api/v1/assignments/<uuid:assignment_id>/submissions/
- POST /api/v1/assignments/<uuid:assignment_id>/submit/
- GET, PUT, PATCH, DELETE /api/v1/assignments/submissions/<uuid:pk>/
- POST /api/v1/assignments/submissions/<uuid:submission_id>/grade/
- GET /api/v1/assignments/comments/<uuid:assignment_id>/comments/
- POST /api/v1/assignments/files/upload/
- GET /api/v1/assignments/stats/

---

## Health and Docs
- GET /health/
- GET /health/detailed/
- GET /health/ready/
- GET /health/alive/
- GET /docs/ (documentation web UI)
- GET /docs/api/json/

## Admin
- GET /admin/


