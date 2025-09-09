import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator

User = get_user_model()


class TimeStampedUUIDModel(models.Model):
    """Abstract base model with UUID primary key and timestamps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Student(TimeStampedUUIDModel):
    """Student model for managing student information"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('GRADUATED', 'Graduated'),
        ('SUSPENDED', 'Suspended'),
        ('DROPPED', 'Dropped Out'),
    ]
    
    YEAR_OF_STUDY_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('5', '5th Year'),
    ]
    
    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
        ('9', 'Semester 9'),
        ('10', 'Semester 10'),
    ]
    
    SECTION_CHOICES = [
        ('A', 'Section A'),
        ('B', 'Section B'),
        ('C', 'Section C'),
        ('D', 'Section D'),
        ('E', 'Section E'),
    ]
    
    QUOTA_CHOICES = [
        ('GENERAL', 'General'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('OBC', 'Other Backward Class'),
        ('EWS', 'Economically Weaker Section'),
        ('PHYSICALLY_CHALLENGED', 'Physically Challenged'),
        ('SPORTS', 'Sports Quota'),
        ('NRI', 'NRI Quota'),
    ]
    
    RELIGION_CHOICES = [
        ('HINDU', 'Hindu'),
        ('MUSLIM', 'Muslim'),
        ('CHRISTIAN', 'Christian'),
        ('SIKH', 'Sikh'),
        ('BUDDHIST', 'Buddhist'),
        ('JAIN', 'Jain'),
        ('OTHER', 'Other'),
    ]
    
    # Basic Information (RollNumber equivalent to student_id)
    roll_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique roll number/student identifier"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Academic Information
    section = models.CharField(max_length=1, choices=SECTION_CHOICES, blank=True, null=True)
    academic_year = models.CharField(max_length=9, help_text="e.g., 2023-2024", blank=True, null=True)
    year_of_study = models.CharField(max_length=1, choices=YEAR_OF_STUDY_CHOICES, default='1', help_text="Current year of study (1st, 2nd, 3rd, 4th year)")
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default='1', help_text="Current semester")
    quota = models.CharField(max_length=25, choices=QUOTA_CHOICES, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True, help_text="Academic or admission rank")
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Student's department"
    )
    academic_program = models.ForeignKey(
        'academics.AcademicProgram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Student's academic program (B.Tech, MBA, MCA, etc.)"
    )
    
    # Contact Information
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    student_mobile = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name="Student Mobile"
    )
    
    # Address Information (moved to StudentAddress for normalization)
    village = models.CharField(max_length=200, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    
    # Identity Information
    aadhar_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        help_text="12-digit Aadhar number",
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message="Aadhar number must be exactly 12 digits."
            )
        ]
    )
    
    # Religious and Caste Information
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, blank=True, null=True)
    caste = models.CharField(max_length=100, blank=True, null=True)
    subcaste = models.CharField(max_length=100, blank=True, null=True)
    
    # Parent Information (normalized via StudentContact)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=200, blank=True, null=True)
    father_mobile = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name="Father Mobile"
    )
    mother_mobile = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name="Mother Mobile"
    )
    
    # Academic Status
    enrollment_date = models.DateField(default=timezone.now)
    expected_graduation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Guardian/Parent Information (Legacy fields for compatibility)
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    guardian_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True
    )
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_relationship = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="e.g., Father, Mother, Guardian, etc."
    )
    
    # Emergency Contact (normalized via StudentContact)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True
    )
    emergency_contact_relationship = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    
    # Medical Information
    medical_conditions = models.TextField(
        blank=True, 
        null=True,
        help_text="Any medical conditions or allergies"
    )
    medications = models.TextField(
        blank=True, 
        null=True,
        help_text="Current medications"
    )
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the student")
    profile_picture = models.ImageField(
        upload_to='student_profiles/', 
        blank=True, 
        null=True
    )
    
    # Linked auth user (created automatically)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile'
    )
    
    # System fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_students'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='updated_students'
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        
    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return the student's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate and return the student's age"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def full_address(self):
        """Return the full address as a string"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])


class StudentContact(TimeStampedUUIDModel):
    """Normalized contacts for a student (parent/guardian/emergency/self)."""
    CONTACT_TYPE_CHOICES = [
        ('SELF', 'Self'),
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('GUARDIAN', 'Guardian'),
        ('EMERGENCY', 'Emergency'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")], max_length=17, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'contact_type', 'is_primary')
        indexes = [
            models.Index(fields=['student', 'contact_type']),
        ]


class StudentAddress(TimeStampedUUIDModel):
    """Normalized addresses for a student with address type."""
    ADDRESS_TYPE_CHOICES = [
        ('CURRENT', 'Current'),
        ('PERMANENT', 'Permanent'),
        ('MAILING', 'Mailing'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'address_type', 'is_primary')
        indexes = [
            models.Index(fields=['student', 'address_type']),
        ]


class StudentIdentifierType(models.TextChoices):
    AADHAR = 'AADHAR', 'Aadhar'
    OTHER = 'OTHER', 'Other'


class StudentIdentifier(TimeStampedUUIDModel):
    """Normalized identifiers for students (e.g., Aadhar)."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='identifiers')
    id_type = models.CharField(max_length=20, choices=StudentIdentifierType.choices)
    identifier = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('id_type', 'identifier')
        indexes = [
            models.Index(fields=['student', 'id_type', 'is_primary']),
        ]


class StudentEnrollmentHistory(TimeStampedUUIDModel):
    """Track student enrollment history"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='enrollment_history'
    )
    year_of_study = models.CharField(max_length=1, choices=Student.YEAR_OF_STUDY_CHOICES, default='1')
    semester = models.CharField(max_length=2, choices=Student.SEMESTER_CHOICES, default='1')
    academic_year = models.CharField(max_length=9, help_text="e.g., 2023-2024")
    enrollment_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Student.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-enrollment_date']
        verbose_name = 'Student Enrollment History'
        verbose_name_plural = 'Student Enrollment Histories'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.year_of_study} Year, Sem {self.semester} ({self.academic_year})"


class StudentDocument(TimeStampedUUIDModel):
    """Store student-related documents"""
    
    DOCUMENT_TYPES = [
        ('BIRTH_CERT', 'Birth Certificate'),
        ('TRANSCRIPT', 'Academic Transcript'),
        ('MEDICAL', 'Medical Record'),
        ('IMMUNIZATION', 'Immunization Record'),
        ('PHOTO_ID', 'Photo ID'),
        ('OTHER', 'Other'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(upload_to='student_documents/')
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Document'
        verbose_name_plural = 'Student Documents'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.title}"


class CustomFieldType(models.TextChoices):
    """Types of custom fields that can be created"""
    TEXT = 'text', 'Text'
    NUMBER = 'number', 'Number'
    DATE = 'date', 'Date'
    EMAIL = 'email', 'Email'
    PHONE = 'phone', 'Phone'
    SELECT = 'select', 'Select (Dropdown)'
    MULTISELECT = 'multiselect', 'Multi-Select'
    BOOLEAN = 'boolean', 'Yes/No'
    TEXTAREA = 'textarea', 'Long Text'
    FILE = 'file', 'File Upload'
    URL = 'url', 'URL'


class CustomField(TimeStampedUUIDModel):
    """Model for creating custom fields for students"""
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=CustomFieldType.choices)
    required = models.BooleanField(default=False)
    help_text = models.TextField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)
    choices = models.JSONField(blank=True, null=True, help_text="For select/multiselect fields, provide options as JSON array")
    validation_regex = models.CharField(max_length=200, blank=True, null=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Custom Field'
        verbose_name_plural = 'Custom Fields'
    
    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"


class StudentCustomFieldValue(TimeStampedUUIDModel):
    """Model for storing custom field values for each student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='custom_field_values')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='student_values')
    value = models.TextField(blank=True, null=True)
    file_value = models.FileField(upload_to='student_custom_files/', blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'custom_field')
        verbose_name = 'Student Custom Field Value'
        verbose_name_plural = 'Student Custom Field Values'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.custom_field.label}: {self.value}"


class StudentImport(TimeStampedUUIDModel):
    """Model to track student import history"""
    
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    total_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    
    # Import options
    skip_errors = models.BooleanField(default=False)
    create_login = models.BooleanField(default=True)
    update_existing = models.BooleanField(default=False)
    
    # Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Error details (stored as JSON)
    errors = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    
    # User who performed the import
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_imports'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Import'
        verbose_name_plural = 'Student Imports'
    
    def __str__(self):
        return f"{self.filename} - {self.status} ({self.success_count} imported)"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_rows == 0:
            return 0
        return round((self.success_count / self.total_rows) * 100, 2)
