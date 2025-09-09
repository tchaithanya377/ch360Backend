from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('students', '0010_contacts_addresses_identifiers_and_refs'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_enrollmenthistory_student_date_idx "
                "ON students_studentenrollmenthistory (student_id, enrollment_date DESC);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_enrollmenthistory_student_date_idx;"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS students_document_student_type_idx "
                "ON students_studentdocument (student_id, document_type);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS students_document_student_type_idx;"
            ),
        ),
    ]


