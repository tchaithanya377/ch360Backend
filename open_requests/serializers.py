from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OpenRequest, RequestComment


class OpenRequestSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(read_only=False, allow_null=True, required=False, queryset=get_user_model().objects.all())

    class Meta:
        model = OpenRequest
        fields = [
            'id', 'title', 'description', 'target', 'status', 'priority', 'due_date', 'assignee',
            'created_by', 'created_at', 'updated_at', 'is_resolved'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    # No __init__ override needed; queryset set at class definition


class RequestCommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RequestComment
        fields = ['id', 'request', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at', 'request']

