from django.db import migrations


def migrate_departmentprogram_to_academicprogram(apps, schema_editor):
    # If DepartmentProgram existed historically, migrate basic fields to AcademicProgram
    AcademicProgram = apps.get_model('academics', 'AcademicProgram')
    Department = apps.get_model('departments', 'Department')
    try:
        DepartmentProgram = apps.get_model('departments', 'DepartmentProgram')
    except LookupError:
        return
    for dp in DepartmentProgram.objects.all().iterator():
        AcademicProgram.objects.update_or_create(
            code=dp.code,
            defaults={
                'name': dp.name,
                'level': 'UG' if dp.level in ['UG', 'PG', 'PHD', 'DIPLOMA', 'CERTIFICATE'] else 'UG',
                'department': dp.department,
                'duration_years': dp.duration_years,
                'total_credits': dp.total_credits,
                'description': dp.description,
                'is_active': dp.status == 'ACTIVE',
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0003_alter_departmentprogram_department'),
        ('academics', '0006_remove_department_head_of_department_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_departmentprogram_to_academicprogram, migrations.RunPython.noop),
        migrations.DeleteModel(name='DepartmentProgram'),
    ]


