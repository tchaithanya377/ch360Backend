from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='enrollmentrequest',
            index=models.Index(fields=['course_section', 'status'], name='idx_enrollreq_section_status'),
        ),
        migrations.AddIndex(
            model_name='waitlistentry',
            index=models.Index(fields=['course_section', 'position'], name='idx_waitlist_section_position'),
        ),
    ]


