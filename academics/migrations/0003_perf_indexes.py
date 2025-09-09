from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_academicprogram_alter_courseenrollment_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX IF NOT EXISTS courseenrollment_student_section_uniq "
                "ON academics_courseenrollment (student_id, course_section_id);\n"
                "CREATE INDEX IF NOT EXISTS courseenrollment_section_status_idx "
                "ON academics_courseenrollment (course_section_id, status);\n"
                "CREATE INDEX IF NOT EXISTS courseenrollment_student_status_idx "
                "ON academics_courseenrollment (student_id, status);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS courseenrollment_student_section_uniq;\n"
                "DROP INDEX IF EXISTS courseenrollment_section_status_idx;\n"
                "DROP INDEX IF EXISTS courseenrollment_student_status_idx;\n"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX IF NOT EXISTS coursesection_unique_natural "
                "ON academics_coursesection (course_id, section_number, academic_year, semester);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS coursesection_unique_natural;\n"
            ),
        ),
    ]


