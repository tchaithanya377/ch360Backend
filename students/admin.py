from django.contrib import admin
from django.utils.html import format_html
from .models import Student, StudentEnrollmentHistory, StudentDocument, CustomField, StudentCustomFieldValue, StudentImport


class StudentEnrollmentHistoryInline(admin.TabularInline):
    """Inline admin for student enrollment history"""
    model = StudentEnrollmentHistory
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class StudentDocumentInline(admin.TabularInline):
    """Inline admin for student documents"""
    model = StudentDocument
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'uploaded_by')


class StudentCustomFieldValueInline(admin.TabularInline):
    """Inline admin for student custom field values"""
    model = StudentCustomFieldValue
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model"""
    list_display = [
        'roll_number', 'full_name', 'year_of_study', 'semester', 'section', 'status', 
        'email', 'student_mobile', 'enrollment_date', 'age'
    ]
    list_filter = [
        'status', 'year_of_study', 'semester', 'section', 'gender', 'quota', 'religion',
        'enrollment_date', 'created_at', 'updated_at'
    ]
    search_fields = [
        'roll_number', 'first_name', 'last_name', 'email', 
        'student_mobile', 'father_name', 'mother_name', 'guardian_name'
    ]
    readonly_fields = [
        'id', 'full_name', 'age', 'full_address', 
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    inlines = [StudentEnrollmentHistoryInline, StudentDocumentInline, StudentCustomFieldValueInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'roll_number', 'first_name', 'last_name', 'middle_name',
                'date_of_birth', 'gender'
            )
        }),
        ('Academic Information', {
            'fields': (
                'section', 'academic_year', 'year_of_study', 'semester', 'quota', 'rank'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 'student_mobile', 'address_line1', 'address_line2',
                'city', 'state', 'postal_code', 'country', 'village'
            )
        }),
        ('Identity Information', {
            'fields': (
                'aadhar_number', 'religion', 'caste', 'subcaste'
            )
        }),
        ('Parent Information', {
            'fields': (
                'father_name', 'mother_name', 'father_mobile', 'mother_mobile'
            )
        }),
        ('Guardian Information', {
            'fields': (
                'guardian_name', 'guardian_phone', 'guardian_email',
                'guardian_relationship'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Academic Status', {
            'fields': (
                'enrollment_date', 'expected_graduation_date', 'status'
            )
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'medications')
        }),
        ('Additional Information', {
            'fields': ('notes', 'profile_picture')
        }),
        ('System Information', {
            'fields': (
                'id', 'full_name', 'age', 'full_address',
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by or updated_by based on whether this is a new object"""
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def age(self, obj):
        """Display student age"""
        return obj.age
    age.short_description = 'Age'
    
    def full_name(self, obj):
        """Display student full name"""
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(StudentEnrollmentHistory)
class StudentEnrollmentHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for Student Enrollment History"""
    list_display = [
        'student', 'year_of_study', 'semester', 'academic_year', 
        'enrollment_date', 'completion_date', 'status'
    ]
    list_filter = [
        'year_of_study', 'semester', 'academic_year', 'status', 
        'enrollment_date', 'completion_date'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 
        'student__student_id', 'academic_year'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': (
                'student', 'year_of_study', 'semester', 'academic_year',
                'enrollment_date', 'completion_date', 'status', 'notes'
            )
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Student Documents"""
    list_display = [
        'student', 'document_type', 'title', 
        'uploaded_by', 'created_at'
    ]
    list_filter = [
        'document_type', 'created_at', 'updated_at'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 
        'student__student_id', 'title', 'description'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'uploaded_by'
    ]
    
    fieldsets = (
        (None, {
            'fields': (
                'student', 'document_type', 'title', 
                'description', 'document_file'
            )
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'uploaded_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by when saving"""
        if not change:  # New object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """Admin configuration for Custom Field model"""
    list_display = [
        'name', 'label', 'field_type', 'required', 'is_active', 'order'
    ]
    list_filter = [
        'field_type', 'required', 'is_active', 'created_at', 'updated_at'
    ]
    search_fields = ['name', 'label', 'help_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': (
                'name', 'label', 'field_type', 'required', 'help_text',
                'default_value', 'choices', 'validation_regex', 'min_value',
                'max_value', 'is_active', 'order'
            )
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentCustomFieldValue)
class StudentCustomFieldValueAdmin(admin.ModelAdmin):
    """Admin configuration for Student Custom Field Values"""
    list_display = [
        'student', 'custom_field', 'value', 'created_at'
    ]
    list_filter = [
        'custom_field__field_type', 'created_at', 'updated_at'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__roll_number',
        'custom_field__name', 'custom_field__label', 'value'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': (
                'student', 'custom_field', 'value', 'file_value'
            )
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentImport)
class StudentImportAdmin(admin.ModelAdmin):
    """Admin configuration for Student Import model"""
    list_display = ['filename', 'status', 'success_count', 'error_count', 'total_rows', 'success_rate', 'created_by', 'created_at']
    list_filter = ['status', 'created_at', 'created_by']
    search_fields = ['filename', 'created_by__email']
    readonly_fields = ['filename', 'file_size', 'total_rows', 'success_count', 'error_count', 'warning_count', 
                      'errors', 'warnings', 'created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('filename', 'file_size', 'total_rows')
        }),
        ('Import Results', {
            'fields': ('status', 'success_count', 'error_count', 'warning_count')
        }),
        ('Import Options', {
            'fields': ('skip_errors', 'create_login', 'update_existing')
        }),
        ('Details', {
            'fields': ('errors', 'warnings', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate(self, obj):
        return f"{obj.success_rate}%"
    success_rate.short_description = 'Success Rate'
