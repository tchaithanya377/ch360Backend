from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_alter_student_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentContact',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contact_type', models.CharField(max_length=20, choices=[('SELF', 'Self'), ('FATHER', 'Father'), ('MOTHER', 'Mother'), ('GUARDIAN', 'Guardian'), ('EMERGENCY', 'Emergency')])),
                ('name', models.CharField(max_length=200, blank=True, null=True)),
                ('phone', models.CharField(max_length=17, blank=True, null=True)),
                ('email', models.EmailField(max_length=254, blank=True, null=True)),
                ('relationship', models.CharField(max_length=50, blank=True, null=True)),
                ('is_primary', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='students.student')),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='StudentAddress',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address_type', models.CharField(max_length=20, choices=[('CURRENT', 'Current'), ('PERMANENT', 'Permanent'), ('MAILING', 'Mailing')])),
                ('address_line1', models.CharField(max_length=255)),
                ('address_line2', models.CharField(max_length=255, blank=True, null=True)),
                ('city', models.CharField(max_length=100, blank=True, null=True)),
                ('state', models.CharField(max_length=100, blank=True, null=True)),
                ('postal_code', models.CharField(max_length=20, blank=True, null=True)),
                ('country', models.CharField(max_length=100, default='India')),
                ('is_primary', models.BooleanField(default=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='students.student')),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='StudentIdentifier',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id_type', models.CharField(max_length=20)),
                ('identifier', models.CharField(max_length=255)),
                ('is_primary', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identifiers', to='students.student')),
            ],
            options={'abstract': False},
        ),
        migrations.AddIndex(
            model_name='studentcontact',
            index=models.Index(fields=['student', 'contact_type'], name='students_st_student_0b43c3_idx'),
        ),
        migrations.AddIndex(
            model_name='studentaddress',
            index=models.Index(fields=['student', 'address_type'], name='students_st_student_3b34b9_idx'),
        ),
        migrations.AddIndex(
            model_name='studentidentifier',
            index=models.Index(fields=['student', 'id_type', 'is_primary'], name='students_st_student_76fbb1_idx'),
        ),
        migrations.AddConstraint(
            model_name='studentcontact',
            constraint=models.UniqueConstraint(fields=('student', 'contact_type', 'is_primary'), name='uniq_student_contact_primary'),
        ),
        migrations.AddConstraint(
            model_name='studentaddress',
            constraint=models.UniqueConstraint(fields=('student', 'address_type', 'is_primary'), name='uniq_student_address_primary'),
        ),
        migrations.AddConstraint(
            model_name='studentidentifier',
            constraint=models.UniqueConstraint(fields=('id_type', 'identifier'), name='uniq_student_identifier_value'),
        ),
    ]


