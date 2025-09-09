from django.db import migrations


def noop_forward(apps, schema_editor):
    # No data migration needed if codes match; FK points to new app label via migration
    pass


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0001_initial'),
        ('academics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(noop_forward, noop_reverse),
    ]


