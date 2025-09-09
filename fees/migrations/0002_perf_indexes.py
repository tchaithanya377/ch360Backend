from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS studentfee_student_status_idx ON fees_studentfee (student_id, status);\n"
                "CREATE INDEX IF NOT EXISTS studentfee_detail_duedate_idx ON fees_studentfee (fee_structure_detail_id, due_date);\n"
                "CREATE INDEX IF NOT EXISTS studentfee_due_overdue_partial_idx ON fees_studentfee (due_date) WHERE status IN ('PENDING','OVERDUE');\n"
                "CREATE INDEX IF NOT EXISTS payment_fee_date_desc_idx ON fees_payment (student_fee_id, payment_date DESC);\n"
                "CREATE UNIQUE INDEX IF NOT EXISTS payment_transaction_id_uniq ON fees_payment (transaction_id) WHERE transaction_id IS NOT NULL;\n"
                "CREATE INDEX IF NOT EXISTS payment_status_date_idx ON fees_payment (status, payment_date DESC);\n"
                "CREATE UNIQUE INDEX IF NOT EXISTS feereceipt_receipt_number_uniq ON fees_feereceipt (receipt_number);\n"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS studentfee_student_status_idx;\n"
                "DROP INDEX IF EXISTS studentfee_detail_duedate_idx;\n"
                "DROP INDEX IF EXISTS studentfee_due_overdue_partial_idx;\n"
                "DROP INDEX IF EXISTS payment_fee_date_desc_idx;\n"
                "DROP INDEX IF EXISTS payment_transaction_id_uniq;\n"
                "DROP INDEX IF EXISTS payment_status_date_idx;\n"
                "DROP INDEX IF EXISTS feereceipt_receipt_number_uniq;\n"
            ),
        ),
    ]


