from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('departments', '0004_drop_departmentprogram'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS departments_resource_cover_idx "
                "ON departments_departmentresource (department_id, resource_type, status);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS departments_resource_cover_idx;"
            ),
        ),
    ]


