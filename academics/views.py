from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Course, Syllabus, SyllabusTopic, Timetable, 
    CourseEnrollment, AcademicCalendar
)
from .serializers import (
    CourseSerializer, CourseCreateSerializer, CourseDetailSerializer,
    SyllabusSerializer, SyllabusCreateSerializer, SyllabusDetailSerializer,
    SyllabusTopicSerializer, TimetableSerializer, TimetableCreateSerializer,
    TimetableDetailSerializer, CourseEnrollmentSerializer, 
    CourseEnrollmentCreateSerializer, AcademicCalendarSerializer,
    AcademicCalendarCreateSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'status', 'credits', 'department', 'programs']
    search_fields = ['code', 'title', 'description']
    ordering_fields = ['code', 'title', 'credits', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action in ['retrieve', 'detail']:
            return CourseDetailSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.select_related('department').prefetch_related('prerequisites', 'programs')
        return queryset
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed course information including syllabus, timetables, and enrollments"""
        course = self.get_object()
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_faculty(self, request):
        """Get courses by specific faculty member"""
        faculty_id = request.query_params.get('faculty_id')
        if faculty_id:
            courses = Course.objects.filter(sections__faculty__id=faculty_id).distinct()
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': 'faculty_id parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Get courses by level"""
        level = request.query_params.get('level')
        if level:
            courses = Course.objects.filter(level=level)
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': 'level parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get course statistics"""
        total_courses = Course.objects.count()
        active_courses = Course.objects.filter(status='ACTIVE').count()
        courses_by_level = Course.objects.values('level').annotate(count=Count('id'))
        
        return Response({
            'total_courses': total_courses,
            'active_courses': active_courses,
            'courses_by_level': courses_by_level
        })


class SyllabusViewSet(viewsets.ModelViewSet):
    """ViewSet for Syllabus model"""
    queryset = Syllabus.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'academic_year', 'semester', 'course']
    search_fields = ['course__code', 'course__title']
    ordering_fields = ['academic_year', 'semester', 'created_at']
    ordering = ['-academic_year', '-semester']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SyllabusCreateSerializer
        elif self.action in ['retrieve', 'detail']:
            return SyllabusDetailSerializer
        return SyllabusSerializer
    
    def get_queryset(self):
        return Syllabus.objects.select_related('course', 'approved_by').prefetch_related('topics')
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed syllabus information including topics"""
        syllabus = self.get_object()
        serializer = self.get_serializer(syllabus)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a syllabus"""
        syllabus = self.get_object()
        if syllabus.status == 'DRAFT':
            syllabus.status = 'APPROVED'
            syllabus.approved_by = request.user
            syllabus.approved_at = timezone.now()
            syllabus.save()
            serializer = self.get_serializer(syllabus)
            return Response(serializer.data)
        return Response({'error': 'Only draft syllabi can be approved'}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_academic_year(self, request):
        """Get syllabi by academic year"""
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            syllabi = Syllabus.objects.filter(academic_year=academic_year)
            serializer = self.get_serializer(syllabi, many=True)
            return Response(serializer.data)
        return Response({'error': 'academic_year parameter required'}, status=400)


class SyllabusTopicViewSet(viewsets.ModelViewSet):
    """ViewSet for SyllabusTopic model"""
    queryset = SyllabusTopic.objects.all()
    serializer_class = SyllabusTopicSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['syllabus', 'week_number']
    ordering_fields = ['week_number', 'order']
    ordering = ['week_number', 'order']
    
    def get_queryset(self):
        return SyllabusTopic.objects.select_related('syllabus')


class TimetableViewSet(viewsets.ModelViewSet):
    """ViewSet for Timetable model"""
    queryset = Timetable.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'timetable_type', 'day_of_week', 'is_active',
        'course_section',
        'course_section__academic_year', 'course_section__semester',
        'course_section__faculty', 'course_section__course'
    ]
    search_fields = ['course_section__course__code', 'course_section__course__title', 'room']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TimetableCreateSerializer
        elif self.action in ['retrieve', 'detail']:
            return TimetableDetailSerializer
        return TimetableSerializer
    
    def get_queryset(self):
        return Timetable.objects.select_related('course_section', 'course_section__course', 'course_section__faculty')
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed timetable information"""
        timetable = self.get_object()
        serializer = self.get_serializer(timetable)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly_schedule(self, request):
        """Get weekly schedule for a specific faculty or course"""
        faculty_id = request.query_params.get('faculty_id')
        course_id = request.query_params.get('course_id')
        academic_year = request.query_params.get('academic_year')
        semester = request.query_params.get('semester')
        
        queryset = Timetable.objects.filter(is_active=True)
        
        if faculty_id:
            queryset = queryset.filter(course_section__faculty_id=faculty_id)
        if course_id:
            queryset = queryset.filter(course_section__course_id=course_id)
        if academic_year:
            queryset = queryset.filter(course_section__academic_year=academic_year)
        if semester:
            queryset = queryset.filter(course_section__semester=semester)
        
        # Group by day of week (return IDs for grouping to keep JSON-serializable)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        weekly_schedule: dict[str, list] = {d: [] for d in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']}
        for item in data:
            day = item.get('day_of_week')
            if day in weekly_schedule:
                weekly_schedule[day].append(item)
        return Response({
            'weekly_schedule': weekly_schedule,
            'all_schedules': data
        })
    
    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """Check for timetable conflicts"""
        faculty_id = request.query_params.get('faculty_id')
        room = request.query_params.get('room')
        academic_year = request.query_params.get('academic_year')
        semester = request.query_params.get('semester')
        
        if not all([faculty_id, room, academic_year, semester]):
            return Response({'error': 'faculty_id, room, academic_year, and semester parameters required'}, status=400)
        
        # Find overlapping schedules
        conflicts = []
        timetables = Timetable.objects.filter(
            course_section__faculty_id=faculty_id,
            room=room,
            course_section__academic_year=academic_year,
            course_section__semester=semester,
            is_active=True
        )
        
        for i, t1 in enumerate(timetables):
            for t2 in timetables[i+1:]:
                if t1.day_of_week == t2.day_of_week:
                    # Check for time overlap
                    if (t1.start_time < t2.end_time and t2.start_time < t1.end_time):
                        conflicts.append({
                            'conflict_type': 'Time Overlap',
                            'timetable1': TimetableSerializer(t1).data,
                            'timetable2': TimetableSerializer(t2).data
                        })
        
        return Response({'conflicts': conflicts, 'total_conflicts': len(conflicts)})


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseEnrollment model"""
    queryset = CourseEnrollment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'student', 'course_section',
        'course_section__academic_year', 'course_section__semester',
        'course_section__course'
    ]
    search_fields = ['student__roll_number', 'student__first_name', 'course_section__course__code']
    ordering_fields = ['enrollment_date']
    ordering = ['-enrollment_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CourseEnrollmentCreateSerializer
        return CourseEnrollmentSerializer
    
    def get_queryset(self):
        return CourseEnrollment.objects.select_related('student', 'course_section', 'course_section__course')
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get enrollments for a specific student"""
        student_id = request.query_params.get('student_id')
        if student_id:
            enrollments = CourseEnrollment.objects.filter(student_id=student_id)
            serializer = self.get_serializer(enrollments, many=True)
            return Response(serializer.data)
        return Response({'error': 'student_id parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """Get enrollments for a specific course"""
        course_id = request.query_params.get('course_id')
        if course_id:
            enrollments = CourseEnrollment.objects.filter(course_section__course_id=course_id)
            serializer = self.get_serializer(enrollments, many=True)
            return Response(serializer.data)
        return Response({'error': 'course_id parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get enrollment statistics"""
        total_enrollments = CourseEnrollment.objects.count()
        active_enrollments = CourseEnrollment.objects.filter(status='ENROLLED').count()
        completed_enrollments = CourseEnrollment.objects.filter(status='COMPLETED').count()
        
        enrollments_by_status = CourseEnrollment.objects.values('status').annotate(count=Count('id'))
        enrollments_by_year = CourseEnrollment.objects.values('course_section__academic_year').annotate(count=Count('id'))
        
        return Response({
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'completed_enrollments': completed_enrollments,
            'enrollments_by_status': enrollments_by_status,
            'enrollments_by_year': enrollments_by_year
        })


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    """ViewSet for AcademicCalendar model"""
    queryset = AcademicCalendar.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'academic_year', 'semester', 'is_academic_day']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'title']
    ordering = ['start_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AcademicCalendarCreateSerializer
        return AcademicCalendarSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming_events(self, request):
        """Get upcoming events"""
        today = timezone.now().date()
        upcoming = AcademicCalendar.objects.filter(
            start_date__gte=today
        ).order_by('start_date')[:10]
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """Get events for a specific month"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not all([year, month]):
            return Response({'error': 'year and month parameters required'}, status=400)
        
        try:
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date()
            
            events = AcademicCalendar.objects.filter(
                start_date__gte=start_date,
                start_date__lt=end_date
            ).order_by('start_date')
            
            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)
            
        except ValueError:
            return Response({'error': 'Invalid year or month'}, status=400)
    
    @action(detail=False, methods=['get'])
    def academic_days(self, request):
        """Get academic days for a specific period"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not all([start_date, end_date]):
            return Response({'error': 'start_date and end_date parameters required'}, status=400)
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            academic_days = AcademicCalendar.objects.filter(
                start_date__gte=start,
                end_date__lte=end,
                is_academic_day=True
            ).order_by('start_date')
            
            serializer = self.get_serializer(academic_days, many=True)
            return Response(serializer.data)
            
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
