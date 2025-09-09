from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        # EnrollmentRequest status indexes
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS enrollment_request_student_status_idx "
                "ON enrollment_enrollmentrequest (student_id, status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS enrollment_request_student_status_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS enrollment_request_section_status_idx "
                "ON enrollment_enrollmentrequest (course_section_id, status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS enrollment_request_section_status_idx;"
            ),
        ),
    ]


