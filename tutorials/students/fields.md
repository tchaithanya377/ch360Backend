# Students default fields

This page lists the core fields on the `students.Student` model and how they map to API serializers. Use this reference when creating forms or validating payloads on the frontend.

## Required on create
- `roll_number` (string, unique)
- `first_name` (string)
- `last_name` (string)
- `date_of_birth` (YYYY-MM-DD)
- `gender` (M/F/O)

## Common optional fields
- `email` (unique if provided)
- `student_mobile` (E.164 phone)
- `section` (A/B/C/D/E)
- `academic_year` (e.g., 2024-2025)
- `year_of_study` (1-5)
- `semester` (1-10)
- `quota` (GENERAL/SC/ST/OBC/EWS/PHYSICALLY_CHALLENGED/SPORTS/NRI)
- `department` (UUID)
- `academic_program` (UUID)

## Address fields
- `village`, `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`

## Identity and demographics
- `aadhar_number` (12 digits)
- `religion` (enum), `caste`, `subcaste`

## Parents/Guardian
- `father_name`, `mother_name`
- `father_mobile`, `mother_mobile`
- `guardian_name`, `guardian_phone`, `guardian_email`, `guardian_relationship`

## Emergency
- `emergency_contact_name`, `emergency_contact_phone`, `emergency_contact_relationship`

## Medical
- `medical_conditions`, `medications`

## Other
- `notes`
- `profile_picture` (image upload)
- `status` (ACTIVE/INACTIVE/GRADUATED/SUSPENDED/DROPPED)

---

Tip: Use the list/detail serializers in `students/api_serializers.py` when building API mocks and type definitions.
# Students Fields and Validation

This reference compiles important fields from `students.models.Student` and related serializers.

## Student model (key fields)
- id: UUID (read-only)
- roll_number: string, unique, required
- first_name, last_name: required
- middle_name: optional
- date_of_birth: date, required
- gender: enum `M|F|O`, required
- email: unique, optional
- student_mobile: `+`-prefixed, up to 15 digits
- address_line1/2, city, state, postal_code, country (default India)
- section: `A|B|C|D|E` (optional)
- academic_year: e.g., `2024-2025`
- year_of_study: `1..5` (default 1)
- semester: `1..10` (default 1)
- quota: enum (GENERAL, SC, ST, OBC, EWS, PHYSICALLY_CHALLENGED, SPORTS, NRI)
- rank: integer
- department: FK to `academics.Department` (optional)
- academic_program: FK to `academics.AcademicProgram` (optional)
- aadhar_number: exactly 12 digits (optional)
- religion, caste, subcaste: optional
- father_name, mother_name, father_mobile, mother_mobile: optional (mobiles validated)
- enrollment_date: defaults to now
- expected_graduation_date: optional
- status: enum `ACTIVE|INACTIVE|GRADUATED|SUSPENDED|DROPPED` (default ACTIVE)
- guardian_* and emergency_*: optional
- medical_conditions, medications, notes, profile_picture: optional
- user: OneToOne to auth user (auto)
- created_by, updated_by: FK to user (system)
- created_at, updated_at: timestamps

Computed (read-only): `full_name`, `age`, `full_address`.

## Serializer rules (API)
- `StudentSerializer`/`StudentDetailSerializer`: validate `roll_number` unique; `email` unique if provided.
- Bulk endpoints wrap `students`, `updates`, `roll_numbers` arrays.

## Default values
- `country`: "India"
- `year_of_study`: "1"
- `semester`: "1"
- `status`: "ACTIVE"
- `enrollment_date`: now

## Related models
- `StudentEnrollmentHistory`: tracks year/semester, academic_year, status.
- `StudentDocument`: types include BIRTH_CERT, TRANSCRIPT, MEDICAL, IMMUNIZATION, PHOTO_ID, OTHER.
- `CustomField`: dynamic fields for student profiles.
- `StudentCustomFieldValue`: values per student and custom field.
- `StudentImport`: import job history and stats.
