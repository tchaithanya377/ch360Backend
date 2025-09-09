from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_studentimport'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX IF NOT EXISTS student_rollnumber_uniq ON students_student (roll_number);\n"
                "CREATE UNIQUE INDEX IF NOT EXISTS student_email_uniq ON students_student (email) WHERE email IS NOT NULL;\n"
                "CREATE INDEX IF NOT EXISTS student_academic_grade_section_idx ON students_student (academic_year, grade_level, section);\n"
                "CREATE INDEX IF NOT EXISTS student_status_idx ON students_student (status);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS student_rollnumber_uniq;\n"
                "DROP INDEX IF EXISTS student_email_uniq;\n"
                "DROP INDEX IF EXISTS student_academic_grade_section_idx;\n"
                "DROP INDEX IF EXISTS student_status_idx;\n"
            ),
        ),
    ]


