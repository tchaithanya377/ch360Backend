from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='examschedule',
            index=models.Index(fields=['exam_session', 'course', 'exam_date'], name='idx_examschedule_session_course_date'),
        ),
        migrations.AddIndex(
            model_name='examschedule',
            index=models.Index(fields=['exam_date'], name='idx_examschedule_date'),
        ),
        migrations.AddIndex(
            model_name='examregistration',
            index=models.Index(fields=['exam_schedule', 'status'], name='idx_examreg_schedule_status'),
        ),
    ]


