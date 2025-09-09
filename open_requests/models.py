from django.db import models
from django.conf import settings


class RequestTarget(models.TextChoices):
    STAFF = 'staff', 'Staff'
    FACULTY = 'faculty', 'Faculty'
    STUDENT = 'student', 'Student'
    DEPARTMENT = 'department', 'Department'

class RequestStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'


class RequestPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class OpenRequest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target = models.CharField(max_length=20, choices=RequestTarget.choices)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.OPEN)
    priority = models.CharField(max_length=10, choices=RequestPriority.choices, default=RequestPriority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_open_requests',
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='open_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.title} -> {self.get_target_display()}"


class RequestComment(models.Model):
    request = models.ForeignKey(OpenRequest, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='open_request_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return f"Comment by {self.author} on #{self.request_id}"

# Create your models here.
