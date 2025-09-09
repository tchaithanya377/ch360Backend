from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('accounts', '0005_ci_unique_indexes_and_constraints'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                """
                DO $$
                BEGIN
                  IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'userrole_no_overlap'
                  ) THEN
                    CREATE EXTENSION IF NOT EXISTS btree_gist;
                    ALTER TABLE accounts_userrole
                    ADD CONSTRAINT userrole_no_overlap
                    EXCLUDE USING GIST (
                      user_id WITH =,
                      role_id WITH =,
                      tstzrange(COALESCE(valid_from, '-infinity'), COALESCE(valid_to, 'infinity')) WITH &&
                    ) WHERE (valid_from IS NOT NULL OR valid_to IS NOT NULL);
                  END IF;
                END$$;
                """
            ),
            reverse_sql=(
                "ALTER TABLE accounts_userrole DROP CONSTRAINT IF EXISTS userrole_no_overlap;"
            ),
        ),
    ]


