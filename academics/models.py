from django.db import models
from django.db import transaction
from django.db.models import F, Q, CheckConstraint, Index
from django.conf import settings
from faculty.models import Faculty
from students.models import Student


"""Deprecated local Department model removed in favor of departments.Department."""


class AcademicProgram(models.Model):
    """Model for academic programs/degrees"""
    PROGRAM_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ARCHIVED', 'Archived'),
    ]
    PROGRAM_LEVELS = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('PHD', 'Doctorate'),
        ('DIPLOMA', 'Diploma'),
        ('CERTIFICATE', 'Certificate'),
    ]
    
    name = models.CharField(max_length=200, help_text="Program name (e.g., Bachelor of Computer Science)")
    code = models.CharField(max_length=20, unique=True, help_text="Program code (e.g., BCS)")
    level = models.CharField(max_length=20, choices=PROGRAM_LEVELS, default='UG')
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='academic_programs')
    duration_years = models.PositiveIntegerField(default=4, help_text="Program duration in years")
    total_credits = models.PositiveIntegerField(help_text="Total credits required for graduation")
    description = models.TextField(blank=True, help_text="Program description")
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS, default='ACTIVE', db_default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level', 'name']
        verbose_name = "Academic Program"
        verbose_name_plural = "Academic Programs"
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure status is always set to a valid value
        if not self.status:
            self.status = 'ACTIVE'
        super().save(*args, **kwargs)


class Course(models.Model):
    """Model for academic courses"""
    COURSE_LEVELS = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('PHD', 'Doctorate'),
        ('DIPLOMA', 'Diploma'),
        ('CERTIFICATE', 'Certificate'),
    ]
    
    COURSE_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DRAFT', 'Draft'),
        ('ARCHIVED', 'Archived'),
    ]
    
    code = models.CharField(max_length=20, unique=True, help_text="Course code (e.g., CS101)")
    title = models.CharField(max_length=200, help_text="Course title")
    description = models.TextField(help_text="Course description")
    level = models.CharField(max_length=20, choices=COURSE_LEVELS, default='UG')
    credits = models.PositiveIntegerField(default=3, help_text="Credit hours")
    duration_weeks = models.PositiveIntegerField(default=16, help_text="Duration in weeks")
    max_students = models.PositiveIntegerField(default=50, help_text="Maximum number of students per section")
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, help_text="Prerequisite courses")
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    programs = models.ManyToManyField(AcademicProgram, related_name='courses', help_text="Programs this course belongs to")
    status = models.CharField(max_length=20, choices=COURSE_STATUS, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code', 'title']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def get_enrolled_students_count(self):
        return sum(section.get_enrolled_students_count() for section in self.sections.all())
    
    def get_total_sections(self):
        return self.sections.count()


class CourseSection(models.Model):
    """Model for course sections (multiple sections of the same course)"""
    SECTION_TYPES = [
        ('LECTURE', 'Lecture'),
        ('LAB', 'Laboratory'),
        ('TUTORIAL', 'Tutorial'),
        ('SEMINAR', 'Seminar'),
        ('WORKSHOP', 'Workshop'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section_number = models.CharField(max_length=10, help_text="Section number (e.g., A, B, 01, 02)")
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='LECTURE')
    academic_year = models.CharField(max_length=9, help_text="Academic year (e.g., 2024-2025)")
    semester = models.CharField(max_length=20, help_text="Semester (e.g., Fall, Spring)")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='course_sections')
    max_students = models.PositiveIntegerField(help_text="Maximum students for this section")
    current_enrollment = models.PositiveIntegerField(default=0, help_text="Current number of enrolled students")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'section_number', 'academic_year', 'semester']
        ordering = ['course__code', 'section_number', 'academic_year', 'semester']
        verbose_name = "Course Section"
        verbose_name_plural = "Course Sections"
        constraints = [
            CheckConstraint(check=Q(current_enrollment__gte=0), name='course_section_current_enrollment_nonnegative'),
            CheckConstraint(check=Q(current_enrollment__lte=F('max_students')), name='course_section_enrollment_not_exceed_capacity'),
        ]
        indexes = [
            Index(fields=['faculty', 'academic_year', 'semester']),
            Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.course.code}-{self.section_number} ({self.academic_year} {self.semester})"
    
    def get_enrolled_students_count(self):
        return self.enrollments.filter(status='ENROLLED').count()
    
    def get_available_seats(self):
        return self.max_students - self.current_enrollment
    
    def is_full(self):
        return self.current_enrollment >= self.max_students
    
    def can_enroll_student(self):
        return self.is_active and not self.is_full()


class Syllabus(models.Model):
    """Model for course syllabuses"""
    SYLLABUS_STATUS = [
        ('DRAFT', 'Draft'),
        ('REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived'),
    ]
    
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='syllabus')
    version = models.CharField(max_length=20, default='1.0', help_text="Syllabus version")
    academic_year = models.CharField(max_length=9, help_text="Academic year (e.g., 2024-2025)")
    semester = models.CharField(max_length=20, help_text="Semester (e.g., Fall, Spring)")
    learning_objectives = models.TextField(help_text="Course learning objectives")
    course_outline = models.TextField(help_text="Detailed course outline")
    assessment_methods = models.TextField(help_text="Assessment and evaluation methods")
    grading_policy = models.TextField(help_text="Grading policy and criteria")
    textbooks = models.TextField(help_text="Required and recommended textbooks")
    additional_resources = models.TextField(blank=True, help_text="Additional learning resources")
    status = models.CharField(max_length=20, choices=SYLLABUS_STATUS, default='DRAFT')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_syllabi')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', '-semester', 'course__code']
        verbose_name = "Syllabus"
        verbose_name_plural = "Syllabi"
    
    def __str__(self):
        return f"{self.course.code} Syllabus - {self.academic_year} {self.semester}"


class SyllabusTopic(models.Model):
    """Model for individual topics within a syllabus"""
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='topics')
    week_number = models.PositiveIntegerField(help_text="Week number in the semester")
    title = models.CharField(max_length=200, help_text="Topic title")
    description = models.TextField(help_text="Topic description")
    learning_outcomes = models.TextField(help_text="Specific learning outcomes for this topic")
    readings = models.TextField(blank=True, help_text="Required readings for this topic")
    activities = models.TextField(blank=True, help_text="Learning activities and assignments")
    duration_hours = models.PositiveIntegerField(default=3, help_text="Duration in hours")
    order = models.PositiveIntegerField(default=0, help_text="Order within the week")
    
    class Meta:
        ordering = ['week_number', 'order']
        unique_together = ['syllabus', 'week_number', 'order']
    
    def __str__(self):
        return f"Week {self.week_number}: {self.title}"


class Timetable(models.Model):
    """Model for class timetables"""
    TIMETABLE_TYPE = [
        ('REGULAR', 'Regular Schedule'),
        ('EXAM', 'Examination Schedule'),
        ('MAKEUP', 'Make-up Classes'),
        ('SPECIAL', 'Special Events'),
    ]
    
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    course_section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='timetables', null=True, blank=True)
    timetable_type = models.CharField(max_length=20, choices=TIMETABLE_TYPE, default='REGULAR')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField(help_text="Class start time")
    end_time = models.TimeField(help_text="Class end time")
    room = models.CharField(max_length=50, help_text="Classroom or venue")
    is_active = models.BooleanField(default=True, help_text="Whether this timetable entry is active")
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['course_section', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.course_section} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    def get_duration_minutes(self):
        """Calculate duration in minutes"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes


class CourseEnrollment(models.Model):
    """Enhanced model for student course enrollments"""
    ENROLLMENT_STATUS = [
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
        ('WITHDRAWN', 'Withdrawn'),
        ('WAITLISTED', 'Waitlisted'),
        ('PENDING', 'Pending Approval'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course_section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='ENROLLED')
    grade = models.CharField(max_length=5, blank=True, help_text="Final grade (e.g., A, B+, C)")
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="Grade points")
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Attendance percentage")
    enrollment_type = models.CharField(max_length=20, choices=[
        ('REGULAR', 'Regular'),
        ('AUDIT', 'Audit'),
        ('CREDIT_TRANSFER', 'Credit Transfer'),
        ('REPEAT', 'Repeat Course'),
    ], default='REGULAR')
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course_section']
        ordering = ['-enrollment_date', 'course_section__course__code']
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        indexes = [
            Index(fields=['student', 'status']),
            Index(fields=['course_section', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.course_section} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Override save to update section enrollment count using atomic F() updates"""
        with transaction.atomic():
            if self.pk is None:
                # New enrollment
                super().save(*args, **kwargs)
                if self.status == 'ENROLLED' and self.course_section_id:
                    CourseSection.objects.filter(pk=self.course_section_id).update(
                        current_enrollment=F('current_enrollment') + 1
                    )
            else:
                old_instance = CourseEnrollment.objects.select_for_update().get(pk=self.pk)
                status_changed = old_instance.status != self.status
                course_section_changed = old_instance.course_section_id != self.course_section_id
                super().save(*args, **kwargs)
                if status_changed or course_section_changed:
                    # Decrement from old if previously counted
                    if old_instance.status == 'ENROLLED' and old_instance.course_section_id:
                        CourseSection.objects.filter(pk=old_instance.course_section_id).update(
                            current_enrollment=F('current_enrollment') - 1
                        )
                    # Increment to new if now counted
                    if self.status == 'ENROLLED' and self.course_section_id:
                        CourseSection.objects.filter(pk=self.course_section_id).update(
                            current_enrollment=F('current_enrollment') + 1
                        )
    
    def delete(self, *args, **kwargs):
        """Override delete to update section enrollment count safely"""
        with transaction.atomic():
            if self.status == 'ENROLLED' and self.course_section_id:
                CourseSection.objects.filter(pk=self.course_section_id).update(
                    current_enrollment=F('current_enrollment') - 1
                )
            super().delete(*args, **kwargs)
    
    @property
    def course(self):
        return self.course_section.course
    
    @property
    def faculty(self):
        return self.course_section.faculty
    
    @property
    def academic_year(self):
        return self.course_section.academic_year
    
    @property
    def semester(self):
        return self.course_section.semester


class AcademicCalendar(models.Model):
    """Model for academic calendar events"""
    EVENT_TYPE = [
        ('HOLIDAY', 'Holiday'),
        ('EXAM', 'Examination'),
        ('BREAK', 'Break'),
        ('EVENT', 'Special Event'),
        ('DEADLINE', 'Deadline'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200, help_text="Event title")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    start_date = models.DateField(help_text="Event start date")
    end_date = models.DateField(help_text="Event end date")
    description = models.TextField(help_text="Event description")
    academic_year = models.CharField(max_length=9, help_text="Academic year")
    semester = models.CharField(max_length=20, help_text="Semester (if applicable)")
    is_academic_day = models.BooleanField(default=True, help_text="Whether this is an academic day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
