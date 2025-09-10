from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['department', 'year_of_study', 'section'], name='idx_student_dept_year_section'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['academic_program', 'year_of_study'], name='idx_student_program_year'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(condition=models.Q(('status', 'ACTIVE')), fields=['status'], name='idx_student_status_active'),
        ),
    ]


