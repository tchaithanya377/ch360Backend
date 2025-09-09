from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX IF NOT EXISTS examregistration_student_schedule_uniq "
                "ON exams_examregistration (student_id, exam_schedule_id);\n"
                "CREATE INDEX IF NOT EXISTS examregistration_schedule_status_idx "
                "ON exams_examregistration (exam_schedule_id, status);\n"
                "CREATE INDEX IF NOT EXISTS examregistration_approved_partial_idx ON exams_examregistration (exam_schedule_id) "
                "WHERE status='APPROVED';\n"
                "CREATE UNIQUE INDEX IF NOT EXISTS hallticket_ticket_number_uniq ON exams_hallticket (ticket_number);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS examregistration_student_schedule_uniq;\n"
                "DROP INDEX IF EXISTS examregistration_schedule_status_idx;\n"
                "DROP INDEX IF EXISTS examregistration_approved_partial_idx;\n"
                "DROP INDEX IF EXISTS hallticket_ticket_number_uniq;\n"
            ),
        ),
    ]


