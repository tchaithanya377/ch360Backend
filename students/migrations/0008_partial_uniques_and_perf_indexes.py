from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('students', '0007_remove_student_grade_level_and_more'),
    ]

    operations = [
        # Partial unique on Student.email where not null
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS students_student_email_notnull_uniq "
                "ON students_student (LOWER(email)) WHERE email IS NOT NULL;"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_email_notnull_uniq;"
            ),
        ),
        # Partial unique on Student.aadhar_number where not null
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS students_student_aadhar_notnull_uniq "
                "ON students_student (aadhar_number) WHERE aadhar_number IS NOT NULL;"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_aadhar_notnull_uniq;"
            ),
        ),
        # Indexes to speed common filters
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_student_status_idx ON students_student (status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_status_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_student_department_status_idx "
                "ON students_student (department_id, status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_department_status_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_student_program_status_idx "
                "ON students_student (academic_program_id, status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_program_status_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_student_year_idx ON students_student (year_of_study);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_year_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_student_semester_idx ON students_student (semester);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_student_semester_idx;"
            ),
        ),
        # Ensure history dates are consistent
        migrations.RunSQL(
            sql=(
                "ALTER TABLE students_studentenrollmenthistory "
                "ADD CONSTRAINT studentenrollmenthistory_dates_chk "
                "CHECK (completion_date IS NULL OR completion_date >= enrollment_date);"
            ),
            reverse_sql=(
                "ALTER TABLE students_studentenrollmenthistory "
                "DROP CONSTRAINT IF EXISTS studentenrollmenthistory_dates_chk;"
            ),
        ),
    ]


