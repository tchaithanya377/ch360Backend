from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course_section', 'date', 'start_time', 'end_time', 'room', 'is_cancelled']
    list_filter = ['date', 'is_cancelled', 'course_section__course__department']
    search_fields = ['course_section__course__code', 'course_section__section_number', 'room', 'notes']
    ordering = ['-date', 'start_time']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'status', 'check_in_time']
    list_filter = ['status', 'session__date']
    search_fields = ['student__roll_number', 'student__user__first_name', 'student__user__last_name']
    ordering = ['session__date', 'student__roll_number']

