from django.contrib import admin
from .models import OpenRequest, RequestComment


@admin.register(OpenRequest)
class OpenRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'target', 'status', 'priority', 'assignee', 'created_by', 'is_resolved', 'created_at', 'due_date')
    list_filter = ('target', 'status', 'priority', 'is_resolved', 'created_at')
    search_fields = ('title', 'description')


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'author', 'created_at')
    search_fields = ('content',)

# Register your models here.
