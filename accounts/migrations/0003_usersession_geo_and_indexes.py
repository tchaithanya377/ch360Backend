from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20250905_1117'),
    ]

    operations = [
        # UserSession geo and login_at fields
        migrations.AddField(
            model_name='usersession',
            name='country',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='region',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='city',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='latitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='longitude',
            field=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='location_raw',
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='login_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),

        # Indexes and constraints to align with models.py
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['user', 'revoked', 'expires_at'], name='accounts_use_user_re_e2b3c6_idx'),
        ),
        migrations.AddIndex(
            model_name='authidentifier',
            index=models.Index(fields=['user', 'id_type', 'is_primary'], name='accounts_aut_user_id__7c8bd2_idx'),
        ),
        migrations.AddConstraint(
            model_name='authidentifier',
            constraint=models.UniqueConstraint(fields=['user', 'id_type'], condition=models.Q(('is_primary', True)), name='uniq_primary_identifier_per_type'),
        ),
        migrations.AddIndex(
            model_name='passwordreset',
            index=models.Index(fields=['user', 'used'], name='accounts_pas_user_id__27a6a1_idx'),
        ),
    ]


