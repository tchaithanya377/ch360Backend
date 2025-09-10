from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0004_alter_academicprogram_status'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='coursesection',
            index=models.Index(fields=['course', 'academic_year', 'semester'], name='idx_section_course_year_sem'),
        ),
        migrations.AddIndex(
            model_name='coursesection',
            index=models.Index(fields=['academic_year', 'semester', 'is_active'], name='idx_section_year_sem_active'),
        ),
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['course_section'], name='idx_enroll_section_active', condition=Q(status='ENROLLED')),
        ),
    ]


