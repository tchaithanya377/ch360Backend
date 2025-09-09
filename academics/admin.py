from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    AcademicProgram, Course, CourseSection, Syllabus, SyllabusTopic, 
    Timetable, CourseEnrollment, AcademicCalendar
)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'department', 'duration_years', 'total_credits', 'is_active']
    list_filter = ['level', 'department', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['level', 'name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'level', 'credits', 'department', 'get_total_sections', 'status', 'created_at']
    list_filter = ['level', 'status', 'department', 'programs']
    search_fields = ['code', 'title', 'description']
    ordering = ['code', 'title']
    filter_horizontal = ['prerequisites', 'programs']
    
    def get_total_sections(self, obj):
        return obj.get_total_sections()
    get_total_sections.short_description = 'Total Sections'


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ['course', 'section_number', 'section_type', 'academic_year', 'semester', 'faculty', 'current_enrollment', 'max_students', 'is_active']
    list_filter = ['section_type', 'academic_year', 'semester', 'is_active', 'course__department', 'faculty']
    search_fields = ['course__code', 'course__title', 'section_number', 'faculty__name']
    ordering = ['course__code', 'section_number', 'academic_year', 'semester']
    list_editable = ['is_active', 'max_students']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'faculty')


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['course', 'version', 'academic_year', 'semester', 'status', 'approved_by', 'approved_at']
    list_filter = ['status', 'academic_year', 'semester', 'course__department']
    search_fields = ['course__code', 'course__title', 'learning_objectives']
    ordering = ['-academic_year', '-semester', 'course__code']
    readonly_fields = ['approved_at']
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'APPROVED' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SyllabusTopic)
class SyllabusTopicAdmin(admin.ModelAdmin):
    list_display = ['syllabus', 'week_number', 'title', 'duration_hours', 'order']
    list_filter = ['week_number', 'syllabus__academic_year', 'syllabus__semester']
    search_fields = ['title', 'description', 'syllabus__course__code']
    ordering = ['syllabus__course__code', 'week_number', 'order']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['course_section', 'timetable_type', 'day_of_week', 'start_time', 'end_time', 'room', 'is_active']
    list_filter = ['timetable_type', 'day_of_week', 'is_active', 'course_section__academic_year', 'course_section__semester']
    search_fields = ['course_section__course__code', 'room', 'notes']
    ordering = ['day_of_week', 'start_time']
    list_editable = ['is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course_section__course', 'course_section__faculty')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_section', 'status', 'enrollment_type', 'enrollment_date', 'grade', 'attendance_percentage']
    list_filter = ['status', 'enrollment_type', 'course_section__academic_year', 'course_section__semester', 'course_section__course__department']
    search_fields = ['student__roll_number', 'student__first_name', 'student__last_name', 'course_section__course__code']
    ordering = ['-enrollment_date', 'course_section__course__code']
    list_editable = ['status', 'grade', 'attendance_percentage']
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'course_section__course', 'course_section__faculty'
        )


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'academic_year', 'semester', 'is_academic_day']
    list_filter = ['event_type', 'academic_year', 'semester', 'is_academic_day']
    search_fields = ['title', 'description']
    ordering = ['start_date', 'title']
    list_editable = ['is_academic_day']


# Custom admin site configuration
admin.site.site_header = "CampsHub360 Academic Administration"
admin.site.site_title = "Academic Admin Portal"
admin.site.index_title = "Welcome to Academic Administration Portal"
