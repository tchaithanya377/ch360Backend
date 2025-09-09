from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transportation', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS transportpass_user_active_idx ON transportation_transportpass (user_id, is_active);\n"
                "CREATE INDEX IF NOT EXISTS transportpass_active_partial_idx ON transportation_transportpass (user_id) WHERE is_active;\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS transportpass_user_active_idx;\n"
                "DROP INDEX IF EXISTS transportpass_active_partial_idx;\n"
            ),
        ),
    ]


