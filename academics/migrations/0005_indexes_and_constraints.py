from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('academics', '0004_merge_20250909_1449'),
    ]

    operations = [
        # CourseSection helpful composite indexes
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS academics_coursesection_course_active_idx "
                "ON academics_coursesection (course_id, is_active);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS academics_coursesection_course_active_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS academics_coursesection_term_idx "
                "ON academics_coursesection (course_id, academic_year, semester);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS academics_coursesection_term_idx;"
            ),
        ),
        # CourseEnrollment partial index for active enrollments
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS academics_courseenrollment_student_status_idx "
                "ON academics_courseenrollment (student_id, status) WHERE status = 'ENROLLED';"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS academics_courseenrollment_student_status_idx;"
            ),
        ),
    ]


