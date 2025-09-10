from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model

from .models import Student, StudentEnrollmentHistory, StudentDocument, CustomField, StudentCustomFieldValue
from .serializers import (
    StudentSerializer, StudentCreateSerializer, StudentUpdateSerializer,
    StudentListSerializer, StudentDetailSerializer, StudentEnrollmentHistorySerializer,
    StudentDocumentSerializer, CustomFieldSerializer, StudentCustomFieldValueSerializer,
    StudentWithCustomFieldsSerializer
)

User = get_user_model()


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing students
    Provides CRUD operations for students
    """
    queryset = Student.objects.select_related(
        'department', 'academic_program', 'current_academic_year', 'current_semester'
    )
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        elif self.action == 'list':
            return StudentListSerializer
        elif self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = Student.objects.select_related(
            'department', 'academic_program', 'current_academic_year', 'current_semester'
        )
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(roll_number__icontains=search) |
                Q(email__icontains=search) |
                Q(father_name__icontains=search) |
                Q(mother_name__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by year of study
        year_filter = self.request.query_params.get('year_of_study', None)
        if year_filter:
            queryset = queryset.filter(year_of_study=year_filter)
        
        # Filter by semester
        semester_filter = self.request.query_params.get('semester', None)
        if semester_filter:
            queryset = queryset.filter(semester=semester_filter)
        
        # Filter by academic program
        program_filter = self.request.query_params.get('academic_program', None)
        if program_filter:
            queryset = queryset.filter(academic_program=program_filter)
        
        # Prefer FK filters when provided (non-breaking deprecation path)
        current_academic_year_id = self.request.query_params.get('current_academic_year', None)
        if current_academic_year_id:
            queryset = queryset.filter(current_academic_year_id=current_academic_year_id)

        current_semester_id = self.request.query_params.get('current_semester', None)
        if current_semester_id:
            queryset = queryset.filter(current_semester_id=current_semester_id)

        # Filter by gender
        gender_filter = self.request.query_params.get('gender', None)
        if gender_filter:
            queryset = queryset.filter(gender=gender_filter)
        
        # Filter by section
        section_filter = self.request.query_params.get('section', None)
        if section_filter:
            queryset = queryset.filter(section=section_filter)
        
        # Filter by quota
        quota_filter = self.request.query_params.get('quota', None)
        if quota_filter:
            queryset = queryset.filter(quota=quota_filter)
        
        # Filter by religion
        religion_filter = self.request.query_params.get('religion', None)
        if religion_filter:
            queryset = queryset.filter(religion=religion_filter)
        
        # Filter by department
        department_filter = self.request.query_params.get('department', None)
        if department_filter:
            queryset = queryset.filter(department=department_filter)
        
        return queryset.order_by('last_name', 'first_name')
    
    def perform_create(self, serializer):
        """Set created_by field when creating a student"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by field when updating a student"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def enrollment_history(self, request, pk=None):
        """Get enrollment history for a specific student"""
        student = self.get_object()
        history = student.enrollment_history.all()
        serializer = StudentEnrollmentHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_enrollment(self, request, pk=None):
        """Add enrollment history entry for a student"""
        student = self.get_object()
        serializer = StudentEnrollmentHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get documents for a specific student"""
        student = self.get_object()
        documents = student.documents.all()
        serializer = StudentDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload a document for a student"""
        student = self.get_object()
        serializer = StudentDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get student statistics"""
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status='ACTIVE').count()
        inactive_students = Student.objects.filter(status='INACTIVE').count()
        graduated_students = Student.objects.filter(status='GRADUATED').count()
        
        # Students by grade level
        grade_stats = {}
        for grade, _ in Student.GRADE_CHOICES:
            grade_stats[f'grade_{grade}'] = Student.objects.filter(grade_level=grade).count()
        
        # Students by gender
        gender_stats = {}
        for gender, _ in Student.GENDER_CHOICES:
            gender_stats[gender] = Student.objects.filter(gender=gender).count()
        
        stats = {
            'total_students': total_students,
            'active_students': active_students,
            'inactive_students': inactive_students,
            'graduated_students': graduated_students,
            'grade_distribution': grade_stats,
            'gender_distribution': gender_stats
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Change student status"""
        student = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in [choice[0] for choice in Student.STATUS_CHOICES]:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student.status = new_status
        student.updated_by = request.user
        student.save()
        
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def custom_fields(self, request, pk=None):
        """Get custom field values for a specific student"""
        student = self.get_object()
        custom_values = student.custom_field_values.all()
        serializer = StudentCustomFieldValueSerializer(custom_values, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_custom_field(self, request, pk=None):
        """Set a custom field value for a student"""
        student = self.get_object()
        custom_field_id = request.data.get('custom_field_id')
        value = request.data.get('value')
        file_value = request.FILES.get('file_value')
        
        if not custom_field_id:
            return Response(
                {'error': 'custom_field_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            custom_field = CustomField.objects.get(id=custom_field_id, is_active=True)
        except CustomField.DoesNotExist:
            return Response(
                {'error': 'Custom field not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create or update the custom field value
        custom_value, created = StudentCustomFieldValue.objects.get_or_create(
            student=student,
            custom_field=custom_field,
            defaults={'value': value, 'file_value': file_value}
        )
        
        if not created:
            custom_value.value = value
            if file_value:
                custom_value.file_value = file_value
            custom_value.save()
        
        serializer = StudentCustomFieldValueSerializer(custom_value)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def available_custom_fields(self, request):
        """Get all available custom fields"""
        custom_fields = CustomField.objects.filter(is_active=True)
        serializer = CustomFieldSerializer(custom_fields, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def divisions(self, request):
        """Get students grouped by department, program, year, semester, and section"""
        from django.db.models import Count
        from departments.models import Department
        from academics.models import AcademicProgram
        
        # Get query parameters
        department_id = request.query_params.get('department', None)
        academic_program_id = request.query_params.get('academic_program', None)
        academic_year = request.query_params.get('academic_year', None)
        year_of_study = request.query_params.get('year_of_study', None)
        semester = request.query_params.get('semester', None)
        section = request.query_params.get('section', None)
        
        # Base queryset
        queryset = Student.objects.filter(status='ACTIVE')
        
        # Apply filters
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if academic_program_id:
            queryset = queryset.filter(academic_program_id=academic_program_id)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        if year_of_study:
            queryset = queryset.filter(year_of_study=year_of_study)
        if semester:
            queryset = queryset.filter(semester=semester)
        if section:
            queryset = queryset.filter(section=section)
        
        # Group students by department, program, year, semester, and section
        divisions = {}
        
        # Get all departments
        departments = Department.objects.filter(is_active=True)
        
        for dept in departments:
            dept_students = queryset.filter(department=dept)
            if dept_students.exists():
                divisions[dept.code] = {
                    'department_id': dept.id,
                    'department_name': dept.name,
                    'department_code': dept.code,
                    'programs': {}
                }
                
                # Group by academic programs
                programs = dept_students.values_list('academic_program', flat=True).distinct()
                for program_id in programs:
                    if program_id:
                        try:
                            program = AcademicProgram.objects.get(id=program_id)
                            program_students = dept_students.filter(academic_program=program)
                            
                            divisions[dept.code]['programs'][program.code] = {
                                'program_id': program.id,
                                'program_name': program.name,
                                'program_code': program.code,
                                'program_level': program.level,
                                'years': {}
                            }
                            
                            # Group by academic year
                            years = program_students.values_list('academic_year', flat=True).distinct()
                            for year in years:
                                if year:
                                    year_students = program_students.filter(academic_year=year)
                                    divisions[dept.code]['programs'][program.code]['years'][year] = {
                                        'year_of_study': {},
                                        'total_students': year_students.count()
                                    }
                                    
                                    # Group by year of study
                                    study_years = year_students.values_list('year_of_study', flat=True).distinct()
                                    for study_year in study_years:
                                        if study_year:
                                            study_year_students = year_students.filter(year_of_study=study_year)
                                            divisions[dept.code]['programs'][program.code]['years'][year]['year_of_study'][study_year] = {
                                                'semesters': {},
                                                'total_students': study_year_students.count()
                                            }
                                            
                                            # Group by semester
                                            semesters = study_year_students.values_list('semester', flat=True).distinct()
                                            for sem in semesters:
                                                if sem:
                                                    semester_students = study_year_students.filter(semester=sem)
                                                    divisions[dept.code]['programs'][program.code]['years'][year]['year_of_study'][study_year]['semesters'][sem] = {
                                                        'sections': {},
                                                        'total_students': semester_students.count()
                                                    }
                                                    
                                                    # Group by section
                                                    sections = semester_students.values_list('section', flat=True).distinct()
                                                    for sec in sections:
                                                        if sec:
                                                            section_students = semester_students.filter(section=sec)
                                                            divisions[dept.code]['programs'][program.code]['years'][year]['year_of_study'][study_year]['semesters'][sem]['sections'][sec] = {
                                                                'students': StudentListSerializer(section_students, many=True).data,
                                                                'count': section_students.count()
                                                            }
                        except AcademicProgram.DoesNotExist:
                            continue
        
        return Response(divisions)
    
    @action(detail=False, methods=['post'])
    def assign_students(self, request):
        """Assign multiple students to department, program, year, semester, and section"""
        student_ids = request.data.get('student_ids', [])
        department_id = request.data.get('department_id')
        academic_program_id = request.data.get('academic_program_id')
        academic_year = request.data.get('academic_year')
        year_of_study = request.data.get('year_of_study')
        semester = request.data.get('semester')
        section = request.data.get('section')
        
        if not student_ids:
            return Response(
                {'error': 'student_ids is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate department if provided
        if department_id:
            try:
                from departments.models import Department
                Department.objects.get(id=department_id, is_active=True)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Invalid department'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate academic program if provided
        if academic_program_id:
            try:
                from academics.models import AcademicProgram
                AcademicProgram.objects.get(id=academic_program_id, is_active=True)
            except AcademicProgram.DoesNotExist:
                return Response(
                    {'error': 'Invalid academic program'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update students
        updated_students = []
        errors = []
        
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                
                # Update fields if provided
                if department_id:
                    student.department_id = department_id
                if academic_program_id:
                    student.academic_program_id = academic_program_id
                if academic_year:
                    student.academic_year = academic_year
                if year_of_study:
                    student.year_of_study = year_of_study
                if semester:
                    student.semester = semester
                if section:
                    student.section = section
                
                student.updated_by = request.user
                student.save()
                updated_students.append(student)
                
            except Student.DoesNotExist:
                errors.append(f'Student with id {student_id} not found')
            except Exception as e:
                errors.append(f'Error updating student {student_id}: {str(e)}')
        
        # Serialize updated students
        serializer = StudentListSerializer(updated_students, many=True)
        
        response_data = {
            'updated_students': serializer.data,
            'updated_count': len(updated_students),
            'errors': errors
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk_assign_by_criteria(self, request):
        """Bulk assign students based on criteria"""
        criteria = request.data.get('criteria', {})
        assignment = request.data.get('assignment', {})
        
        if not assignment:
            return Response(
                {'error': 'assignment data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build filter criteria
        queryset = Student.objects.filter(status='ACTIVE')
        
        # Apply criteria filters
        if criteria.get('current_department'):
            queryset = queryset.filter(department_id=criteria['current_department'])
        if criteria.get('current_academic_program'):
            queryset = queryset.filter(academic_program_id=criteria['current_academic_program'])
        if criteria.get('current_academic_year'):
            queryset = queryset.filter(academic_year=criteria['current_academic_year'])
        if criteria.get('current_year_of_study'):
            queryset = queryset.filter(year_of_study=criteria['current_year_of_study'])
        if criteria.get('current_semester'):
            queryset = queryset.filter(semester=criteria['current_semester'])
        if criteria.get('current_section'):
            queryset = queryset.filter(section=criteria['current_section'])
        if criteria.get('gender'):
            queryset = queryset.filter(gender=criteria['gender'])
        if criteria.get('quota'):
            queryset = queryset.filter(quota=criteria['quota'])
        
        # Validate assignment department if provided
        if assignment.get('department_id'):
            try:
                from departments.models import Department
                Department.objects.get(id=assignment['department_id'], is_active=True)
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Invalid assignment department'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate assignment academic program if provided
        if assignment.get('academic_program_id'):
            try:
                from academics.models import AcademicProgram
                AcademicProgram.objects.get(id=assignment['academic_program_id'], is_active=True)
            except AcademicProgram.DoesNotExist:
                return Response(
                    {'error': 'Invalid assignment academic program'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update students
        update_fields = {}
        if assignment.get('department_id'):
            update_fields['department_id'] = assignment['department_id']
        if assignment.get('academic_program_id'):
            update_fields['academic_program_id'] = assignment['academic_program_id']
        if assignment.get('academic_year'):
            update_fields['academic_year'] = assignment['academic_year']
        if assignment.get('year_of_study'):
            update_fields['year_of_study'] = assignment['year_of_study']
        if assignment.get('semester'):
            update_fields['semester'] = assignment['semester']
        if assignment.get('section'):
            update_fields['section'] = assignment['section']
        
        update_fields['updated_by'] = request.user
        
        # Perform bulk update
        updated_count = queryset.update(**update_fields)
        
        # Get updated students for response
        updated_students = queryset.all()[:50]  # Limit response size
        serializer = StudentListSerializer(updated_students, many=True)
        
        response_data = {
            'updated_count': updated_count,
            'criteria_matched': queryset.count(),
            'sample_updated_students': serializer.data,
            'assignment': assignment
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def division_statistics(self, request):
        """Get statistics for student divisions"""
        from django.db.models import Count
        from departments.models import Department
        
        # Get query parameters for filtering
        department_id = request.query_params.get('department', None)
        academic_year = request.query_params.get('academic_year', None)
        
        # Base queryset
        queryset = Student.objects.filter(status='ACTIVE')
        
        # Apply filters
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        # Get statistics by department
        stats = {}
        departments = Department.objects.filter(is_active=True)
        
        for dept in departments:
            dept_students = queryset.filter(department=dept)
            if dept_students.exists():
                # Count by year
                year_counts = {}
                years = dept_students.values_list('academic_year', flat=True).distinct()
                for year in years:
                    if year:
                        year_students = dept_students.filter(academic_year=year)
                        year_counts[year] = {
                            'total': year_students.count(),
                            'sections': {}
                        }
                        
                        # Count by section
                        sections = year_students.values_list('section', flat=True).distinct()
                        for sec in sections:
                            if sec:
                                section_count = year_students.filter(section=sec).count()
                                year_counts[year]['sections'][sec] = section_count
                
                # Count by year of study
                year_counts = {}
                for year, _ in Student.YEAR_OF_STUDY_CHOICES:
                    count = dept_students.filter(year_of_study=year).count()
                    if count > 0:
                        year_counts[year] = count
                
                # Count by semester
                semester_counts = {}
                for semester, _ in Student.SEMESTER_CHOICES:
                    count = dept_students.filter(semester=semester).count()
                    if count > 0:
                        semester_counts[semester] = count
                
                # Count by gender
                gender_counts = {}
                for gender, _ in Student.GENDER_CHOICES:
                    count = dept_students.filter(gender=gender).count()
                    if count > 0:
                        gender_counts[gender] = count
                
                stats[dept.code] = {
                    'department_id': dept.id,
                    'department_name': dept.name,
                    'department_code': dept.code,
                    'total_students': dept_students.count(),
                    'by_year': year_counts,
                    'by_year_of_study': year_counts,
                    'by_semester': semester_counts,
                    'by_gender': gender_counts
                }
        
        return Response(stats)


class StudentEnrollmentHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student enrollment history"""
    queryset = StudentEnrollmentHistory.objects.all()
    serializer_class = StudentEnrollmentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by student if provided"""
        queryset = StudentEnrollmentHistory.objects.all()
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset.order_by('-enrollment_date')


class StudentDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student documents"""
    queryset = StudentDocument.objects.all()
    serializer_class = StudentDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter by student if provided"""
        queryset = StudentDocument.objects.all()
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        document_type = self.request.query_params.get('document_type', None)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set uploaded_by field when creating a document"""
        serializer.save(uploaded_by=self.request.user)


class CustomFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for managing custom fields"""
    queryset = CustomField.objects.filter(is_active=True)
    serializer_class = CustomFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by field type if provided"""
        queryset = CustomField.objects.filter(is_active=True)
        field_type = self.request.query_params.get('field_type', None)
        if field_type:
            queryset = queryset.filter(field_type=field_type)
        return queryset.order_by('order', 'name')


class StudentCustomFieldValueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student custom field values"""
    queryset = StudentCustomFieldValue.objects.all()
    serializer_class = StudentCustomFieldValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter by student if provided"""
        queryset = StudentCustomFieldValue.objects.all()
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        custom_field_id = self.request.query_params.get('custom_field', None)
        if custom_field_id:
            queryset = queryset.filter(custom_field_id=custom_field_id)
        
        return queryset.order_by('custom_field__order', 'custom_field__name')


# Additional utility views for frontend
def student_dashboard(request):
    """Dashboard view for student management"""
    if not request.user.is_authenticated:
        return render(request, 'registration/login.html')
    
    context = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(status='ACTIVE').count(),
        'recent_students': Student.objects.order_by('-created_at')[:5]
    }
    return render(request, 'students/dashboard.html', context)


def student_list_view(request):
    """List view for students"""
    if not request.user.is_authenticated:
        return render(request, 'registration/login.html')
    
    students = Student.objects.all().order_by('last_name', 'first_name')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query
    }
    return render(request, 'students/student_list.html', context)


def student_detail_view(request, student_id):
    """Detail view for a specific student"""
    if not request.user.is_authenticated:
        return render(request, 'registration/login.html')
    
    student = get_object_or_404(Student, pk=student_id)
    context = {
        'student': student,
        'enrollment_history': student.enrollment_history.all(),
        'documents': student.documents.all()
    }
    return render(request, 'students/student_detail.html', context)
