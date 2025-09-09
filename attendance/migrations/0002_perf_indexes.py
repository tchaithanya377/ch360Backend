from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS attendancerecord_session_student_idx "
                "ON attendance_attendancerecord (session_id, student_id);\n"
                "CREATE INDEX IF NOT EXISTS attendancerecord_student_session_idx "
                "ON attendance_attendancerecord (student_id, session_id);\n"
                "CREATE INDEX IF NOT EXISTS attendancerecord_session_status_idx "
                "ON attendance_attendancerecord (session_id, status);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS attendancerecord_session_student_idx;\n"
                "DROP INDEX IF EXISTS attendancerecord_student_session_idx;\n"
                "DROP INDEX IF EXISTS attendancerecord_session_status_idx;\n"
            ),
        ),
    ]


