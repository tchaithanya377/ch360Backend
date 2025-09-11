"""
Optimized Serializers for Student Module
Minimal data transfer for high-performance APIs
"""

from rest_framework import serializers
from .models import Student, StudentEnrollmentHistory, StudentDocument, CustomField, StudentCustomFieldValue


class StudentMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for high-performance list views
    Only includes essential fields to reduce payload size
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'roll_number', 'full_name', 'email',
            'year_of_study', 'semester', 'section', 'status',
            'department_name', 'academic_program_name'
        ]
        read_only_fields = ['id', 'full_name', 'department_name', 'academic_program_name']


class StudentListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for student list views
    Balances performance with necessary information
    """
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    academic_program_name = serializers.CharField(source='academic_program.name', read_only=True)
    academic_program_code = serializers.CharField(source='academic_program.code', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'roll_number', 'full_name', 'email', 'student_mobile',
            'year_of_study', 'semester', 'section', 'status',
            'department_name', 'department_code',
            'academic_program_name', 'academic_program_code',
            'enrollment_date', 'created_at'
        ]
        read_only_fields = ['id', 'full_name', 'department_name', 'department_code', 
                           'academic_program_name', 'academic_program_code', 'created_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for student detail views
    Includes all necessary information for detailed views
    """
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    
    # Related object information
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    academic_program_name = serializers.CharField(source='academic_program.name', read_only=True)
    academic_program_code = serializers.CharField(source='academic_program.code', read_only=True)
    current_academic_year_name = serializers.CharField(source='current_academic_year.year', read_only=True)
    current_semester_name = serializers.CharField(source='current_semester.name', read_only=True)
    quota_name = serializers.CharField(source='quota.name', read_only=True)
    religion_name = serializers.CharField(source='religion.name', read_only=True)
    caste_name = serializers.CharField(source='caste.name', read_only=True)
    
    # User information
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    
    # Audit information
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    updated_by_email = serializers.CharField(source='updated_by.email', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            # Basic Information
            'id', 'roll_number', 'first_name', 'last_name', 'middle_name',
            'full_name', 'date_of_birth', 'age', 'gender', 'email', 'student_mobile',
            
            # Academic Information
            'section', 'academic_year', 'year_of_study', 'semester', 'rank',
            'department_name', 'department_code', 'academic_program_name', 'academic_program_code',
            'current_academic_year_name', 'current_semester_name', 'quota_name',
            
            # Address Information
            'village', 'address_line1', 'address_line2', 'city', 'state', 
            'postal_code', 'country', 'full_address',
            
            # Identity Information
            'aadhar_number', 'religion_name', 'caste_name', 'subcaste',
            
            # Parent Information
            'father_name', 'mother_name', 'father_mobile', 'mother_mobile',
            
            # Guardian Information
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship',
            
            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            
            # Medical Information
            'medical_conditions', 'medications',
            
            # Academic Status
            'enrollment_date', 'expected_graduation_date', 'status',
            
            # Additional Information
            'notes', 'profile_picture',
            
            # User and Audit Information
            'user_email', 'user_is_active', 'created_by_email', 'updated_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'age', 'full_address', 'created_at', 'updated_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for creating new students
    Only includes fields necessary for creation
    """
    
    class Meta:
        model = Student
        fields = [
            'roll_number', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'email', 'student_mobile',
            'section', 'academic_year', 'year_of_study', 'semester',
            'department', 'academic_program', 'current_academic_year', 'current_semester',
            'quota', 'rank', 'village', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'aadhar_number',
            'religion', 'caste', 'subcaste', 'father_name', 'mother_name',
            'father_mobile', 'mother_mobile', 'guardian_name', 'guardian_phone',
            'guardian_email', 'guardian_relationship', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'medical_conditions', 'medications', 'notes', 'profile_picture',
            'enrollment_date', 'expected_graduation_date', 'status'
        ]
    
    def validate_roll_number(self, value):
        """Validate roll number uniqueness"""
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("Roll number must be unique.")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value and Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email must be unique.")
        return value


class StudentUpdateSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for updating students
    Excludes read-only fields and roll_number
    """
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender',
            'email', 'student_mobile', 'section', 'academic_year', 'year_of_study',
            'semester', 'department', 'academic_program', 'current_academic_year',
            'current_semester', 'quota', 'rank', 'village', 'address_line1',
            'address_line2', 'city', 'state', 'postal_code', 'country',
            'aadhar_number', 'religion', 'caste', 'subcaste', 'father_name',
            'mother_name', 'father_mobile', 'mother_mobile', 'guardian_name',
            'guardian_phone', 'guardian_email', 'guardian_relationship',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'medical_conditions', 'medications',
            'notes', 'profile_picture', 'expected_graduation_date', 'status'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness excluding current instance"""
        if value:
            queryset = Student.objects.filter(email=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Email must be unique.")
        return value


class StudentSearchSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for search results
    Minimal fields for fast search response
    """
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    academic_program_name = serializers.CharField(source='academic_program.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'roll_number', 'full_name', 'email', 'year_of_study',
            'semester', 'section', 'status', 'department_name', 'academic_program_name'
        ]
        read_only_fields = ['id', 'full_name', 'department_name', 'academic_program_name']


class StudentExportSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for bulk export operations
    Includes all necessary fields for export
    """
    full_name = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    academic_program_name = serializers.CharField(source='academic_program.name', read_only=True)
    current_academic_year_name = serializers.CharField(source='current_academic_year.year', read_only=True)
    current_semester_name = serializers.CharField(source='current_semester.name', read_only=True)
    quota_name = serializers.CharField(source='quota.name', read_only=True)
    religion_name = serializers.CharField(source='religion.name', read_only=True)
    caste_name = serializers.CharField(source='caste.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'roll_number', 'full_name', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'email', 'student_mobile', 'section',
            'academic_year', 'year_of_study', 'semester', 'rank', 'status',
            'department_name', 'academic_program_name', 'current_academic_year_name',
            'current_semester_name', 'quota_name', 'village', 'address_line1',
            'address_line2', 'city', 'state', 'postal_code', 'country',
            'aadhar_number', 'religion_name', 'caste_name', 'subcaste',
            'father_name', 'mother_name', 'father_mobile', 'mother_mobile',
            'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'medical_conditions', 'medications',
            'notes', 'enrollment_date', 'expected_graduation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']


class StudentStatisticsSerializer(serializers.Serializer):
    """
    Serializer for student statistics
    """
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    inactive_students = serializers.IntegerField()
    graduated_students = serializers.IntegerField()
    year_distribution = serializers.DictField()
    section_distribution = serializers.DictField()
    academic_year_distribution = serializers.DictField()


class StudentDashboardSerializer(serializers.Serializer):
    """
    Serializer for dashboard metrics
    """
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    inactive_students = serializers.IntegerField()
    graduated_students = serializers.IntegerField()
    recent_enrollments = serializers.IntegerField()
    year_distribution = serializers.DictField()
    section_distribution = serializers.DictField()
    monthly_enrollments = serializers.DictField()


class StudentEnrollmentHistorySerializer(serializers.ModelSerializer):
    """
    Optimized serializer for enrollment history
    """
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = StudentEnrollmentHistory
        fields = [
            'id', 'student', 'student_name', 'year_of_study', 'semester',
            'academic_year', 'enrollment_date', 'completion_date', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'created_at', 'updated_at']


class StudentDocumentSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for student documents
    """
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.email', read_only=True)
    
    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student', 'student_name', 'document_type', 'title',
            'description', 'document_file', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'uploaded_by', 'uploaded_by_name', 'created_at', 'updated_at']


class CustomFieldSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for custom fields
    """
    
    class Meta:
        model = CustomField
        fields = [
            'id', 'name', 'label', 'field_type', 'required', 'help_text',
            'default_value', 'choices', 'validation_regex', 'min_value',
            'max_value', 'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentCustomFieldValueSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for custom field values
    """
    custom_field = CustomFieldSerializer(read_only=True)
    custom_field_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = StudentCustomFieldValue
        fields = [
            'id', 'custom_field', 'custom_field_id', 'value', 'file_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentBulkOperationSerializer(serializers.Serializer):
    """
    Serializer for bulk operations
    """
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of student IDs for bulk operation"
    )
    operation = serializers.ChoiceField(
        choices=['update', 'delete', 'export', 'assign'],
        help_text="Type of bulk operation to perform"
    )
    data = serializers.DictField(
        required=False,
        help_text="Data for bulk update operations"
    )


class StudentAssignmentSerializer(serializers.Serializer):
    """
    Serializer for student assignment operations
    """
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of student IDs to assign"
    )
    department_id = serializers.UUIDField(required=False, allow_null=True)
    academic_program_id = serializers.UUIDField(required=False, allow_null=True)
    academic_year = serializers.CharField(required=False, allow_null=True, max_length=9)
    year_of_study = serializers.CharField(required=False, allow_null=True, max_length=1)
    semester = serializers.CharField(required=False, allow_null=True, max_length=2)
    section = serializers.CharField(required=False, allow_null=True, max_length=1)
    
    def validate_student_ids(self, value):
        """Validate that student IDs exist"""
        if not value:
            raise serializers.ValidationError("At least one student ID is required")
        
        existing_students = Student.objects.filter(id__in=value).count()
        if existing_students != len(value):
            raise serializers.ValidationError("One or more student IDs are invalid")
        
        return value
