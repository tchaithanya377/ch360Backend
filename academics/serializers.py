from rest_framework import serializers
from .models import (
    Course, Syllabus, SyllabusTopic, Timetable, 
    CourseEnrollment, AcademicCalendar
)
from faculty.serializers import FacultySerializer
from students.serializers import StudentSerializer


class CourseSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    programs = serializers.StringRelatedField(many=True, read_only=True)
    prerequisites = serializers.StringRelatedField(many=True, read_only=True)
    enrolled_students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'title', 'description', 'level', 'credits',
            'duration_weeks', 'max_students', 'prerequisites', 'department', 'programs',
            'status', 'enrolled_students_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_enrolled_students_count(self, obj):
        try:
            return sum(section.get_enrolled_students_count() for section in obj.sections.all())
        except Exception:
            return 0


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'code', 'title', 'description', 'level', 'credits',
            'duration_weeks', 'max_students', 'prerequisites', 'department', 'programs', 'status'
        ]


class SyllabusTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabusTopic
        fields = [
            'id', 'week_number', 'title', 'description', 'learning_outcomes',
            'readings', 'activities', 'duration_hours', 'order'
        ]
        read_only_fields = ['id']


class SyllabusSerializer(serializers.ModelSerializer):
    topics = SyllabusTopicSerializer(many=True, read_only=True)
    course = CourseSerializer(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Syllabus
        fields = [
            'id', 'course', 'version', 'academic_year', 'semester',
            'learning_objectives', 'course_outline', 'assessment_methods',
            'grading_policy', 'textbooks', 'additional_resources', 'status',
            'approved_by', 'approved_at', 'topics', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SyllabusCreateSerializer(serializers.ModelSerializer):
    topics = SyllabusTopicSerializer(many=True, required=False)
    
    class Meta:
        model = Syllabus
        fields = [
            'course', 'version', 'academic_year', 'semester',
            'learning_objectives', 'course_outline', 'assessment_methods',
            'grading_policy', 'textbooks', 'additional_resources', 'status', 'topics'
        ]
    
    def create(self, validated_data):
        topics_data = validated_data.pop('topics', [])
        syllabus = Syllabus.objects.create(**validated_data)
        
        for topic_data in topics_data:
            SyllabusTopic.objects.create(syllabus=syllabus, **topic_data)
        
        return syllabus
    
    def update(self, instance, validated_data):
        topics_data = validated_data.pop('topics', [])
        
        # Update syllabus fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update topics
        if topics_data:
            # Remove existing topics
            instance.topics.all().delete()
            # Create new topics
            for topic_data in topics_data:
                SyllabusTopic.objects.create(syllabus=instance, **topic_data)
        
        return instance


class TimetableSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'course', 'timetable_type', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time',
            'room', 'faculty', 'is_active', 'notes', 'duration_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_course(self, obj):
        try:
            return CourseSerializer(obj.course_section.course).data
        except Exception:
            return None

    def get_faculty(self, obj):
        try:
            from faculty.serializers import FacultySerializer as FSer
            return FSer(obj.course_section.faculty).data
        except Exception:
            return None

    def get_duration_minutes(self, obj):
        try:
            return obj.get_duration_minutes()
        except Exception:
            return None


class TimetableCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = [
            'course_section', 'timetable_type',
            'day_of_week', 'start_time', 'end_time', 'room',
            'is_active', 'notes'
        ]


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = serializers.SerializerMethodField()
    academic_year = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'course', 'academic_year', 'semester',
            'enrollment_date', 'status', 'grade', 'grade_points',
            'attendance_percentage', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollment_date', 'created_at', 'updated_at']

    def get_course(self, obj):
        try:
            return CourseSerializer(obj.course).data
        except Exception:
            return None

    def get_academic_year(self, obj):
        try:
            return obj.course_section.academic_year
        except Exception:
            return None

    def get_semester(self, obj):
        try:
            return obj.course_section.semester
        except Exception:
            return None


class CourseEnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = [
            'student', 'course_section',
            'status', 'grade', 'grade_points', 'attendance_percentage', 'enrollment_type', 'notes'
        ]


class AcademicCalendarSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = AcademicCalendar
        fields = [
            'id', 'title', 'event_type', 'event_type_display', 'start_date',
            'end_date', 'description', 'academic_year', 'semester',
            'is_academic_day', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AcademicCalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = [
            'title', 'event_type', 'start_date', 'end_date', 'description',
            'academic_year', 'semester', 'is_academic_day'
        ]


# Nested serializers for detailed views
class CourseDetailSerializer(CourseSerializer):
    syllabus = SyllabusSerializer(read_only=True)
    timetables = TimetableSerializer(many=True, read_only=True)
    enrollments = CourseEnrollmentSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['syllabus', 'timetables', 'enrollments']


class SyllabusDetailSerializer(SyllabusSerializer):
    topics = SyllabusTopicSerializer(many=True, read_only=True)
    
    class Meta(SyllabusSerializer.Meta):
        fields = SyllabusSerializer.Meta.fields


class TimetableDetailSerializer(TimetableSerializer):
    course = CourseSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    
    class Meta(TimetableSerializer.Meta):
        fields = TimetableSerializer.Meta.fields
