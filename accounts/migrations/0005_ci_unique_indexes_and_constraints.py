from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('accounts', '0004_rename_accounts_aut_user_id__7c8bd2_idx_accounts_au_user_id_93c765_idx_and_more'),
    ]

    operations = [
        # Case-insensitive unique for User.email
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS accounts_user_email_ci_uniq "
                "ON accounts_user (LOWER(email));"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS accounts_user_email_ci_uniq;"
            ),
        ),
        # Case-insensitive unique for AuthIdentifier (id_type, identifier)
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS accounts_authidentifier_idtype_identifier_ci_uniq "
                "ON accounts_authidentifier (id_type, LOWER(identifier));"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS accounts_authidentifier_idtype_identifier_ci_uniq;"
            ),
        ),
        # Partial index for active sessions to speed lookups
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS accounts_usersession_active_idx "
                "ON accounts_usersession (user_id, expires_at) "
                "WHERE revoked = false;"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS accounts_usersession_active_idx;"
            ),
        ),
        # Partial index for unused password resets
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS accounts_passwordreset_unused_idx "
                "ON accounts_passwordreset (user_id, expires_at) "
                "WHERE used = false;"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS accounts_passwordreset_unused_idx;"
            ),
        ),
        # Check constraint for UserRole validity dates
        migrations.RunSQL(
            sql=(
                "ALTER TABLE accounts_userrole "
                "ADD CONSTRAINT accounts_userrole_valid_range_chk "
                "CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from);"
            ),
            reverse_sql=(
                "ALTER TABLE accounts_userrole "
                "DROP CONSTRAINT IF EXISTS accounts_userrole_valid_range_chk;"
            ),
        ),
        # Helpful index for AuditLog queries by user and time
        migrations.RunSQL(
            sql=(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS accounts_auditlog_user_created_at_idx "
                "ON accounts_auditlog (user_id, created_at DESC);"
            ),
            reverse_sql=(
                "DROP INDEX CONCURRENTLY IF EXISTS accounts_auditlog_user_created_at_idx;"
            ),
        ),
    ]


