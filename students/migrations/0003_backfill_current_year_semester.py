from django.db import migrations


def backfill_current_year_semester(apps, schema_editor):
    AcademicYear = apps.get_model('students', 'AcademicYear')
    Semester = apps.get_model('students', 'Semester')
    Student = apps.get_model('students', 'Student')

    # Map year string -> AcademicYear id
    year_map = {ay.year: ay.id for ay in AcademicYear.objects.all()}

    # Attempt to infer Semester by name match (best-effort)
    # Student.semester stores numeric/short strings; we keep it as is, only backfill if a current_semester exists already per FK
    semester_lookup = {}
    for sem in Semester.objects.all():
        key = f"{sem.academic_year_id}:{sem.semester_type}"
        semester_lookup.setdefault(key, sem.id)

    # Bulk update current_academic_year from academic_year string
    updates = []
    for s in Student.objects.only('id', 'academic_year', 'current_academic_year_id', 'current_semester_id', 'semester'):
        target_year_id = year_map.get(s.academic_year)
        if target_year_id and s.current_academic_year_id is None:
            updates.append((s.id, target_year_id))
    if updates:
        # Use raw SQL for efficiency
        student_table = Student._meta.db_table
        with schema_editor.connection.cursor() as cursor:
            for sid, ayid in updates:
                cursor.execute(
                    f"UPDATE {student_table} SET current_academic_year_id=%s WHERE id=%s AND current_academic_year_id IS NULL",
                    [ayid, sid],
                )


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_student_indexes'),
    ]

    operations = [
        migrations.RunPython(backfill_current_year_semester, migrations.RunPython.noop),
    ]


