from django.db import models
from django.conf import settings
import uuid
import json
from datetime import datetime

class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class APICollection(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_collections')
    is_public = models.BooleanField(default=False)
    base_url = models.URLField(blank=True, help_text="Base URL for all requests in this collection")
    
    def __str__(self):
        return self.name

class APIEnvironment(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_environments')
    variables = models.JSONField(default=dict, help_text="Environment variables as key-value pairs")
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class APIRequest(TimeStampedUUIDModel):
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    collection = models.ForeignKey(APICollection, on_delete=models.CASCADE, related_name='requests')
    method = models.CharField(max_length=10, choices=HTTP_METHODS, default='GET')
    url = models.URLField()
    headers = models.JSONField(default=dict)
    body = models.TextField(blank=True)
    body_type = models.CharField(max_length=20, default='json', choices=[
        ('json', 'JSON'),
        ('form', 'Form Data'),
        ('raw', 'Raw'),
        ('binary', 'Binary'),
    ])
    params = models.JSONField(default=dict, help_text="Query parameters")
    auth_type = models.CharField(max_length=20, default='none', choices=[
        ('none', 'No Auth'),
        ('bearer', 'Bearer Token'),
        ('basic', 'Basic Auth'),
        ('api_key', 'API Key'),
    ])
    auth_config = models.JSONField(default=dict, help_text="Authentication configuration")
    timeout = models.IntegerField(default=30, help_text="Request timeout in seconds")
    order = models.IntegerField(default=0, help_text="Order within collection")
    
    def __str__(self):
        return f"{self.method} {self.name}"

class APITest(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    request = models.ForeignKey(APIRequest, on_delete=models.CASCADE, related_name='tests')
    test_script = models.TextField(blank=True, help_text="JavaScript test script")
    assertions = models.JSONField(default=list, help_text="List of assertions to run")
    pre_request_script = models.TextField(blank=True, help_text="Script to run before request")
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class APITestResult(TimeStampedUUIDModel):
    test = models.ForeignKey(APITest, on_delete=models.CASCADE, related_name='results')
    request = models.ForeignKey(APIRequest, on_delete=models.CASCADE, related_name='test_results')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ])
    response_status = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in milliseconds")
    error_message = models.TextField(blank=True)
    test_results = models.JSONField(default=dict, help_text="Individual test assertion results")
    executed_at = models.DateTimeField(auto_now_add=True)
    environment = models.ForeignKey(APIEnvironment, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.test.name} - {self.status}"

class APITestSuite(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    collection = models.ForeignKey(APICollection, on_delete=models.CASCADE, related_name='test_suites')
    tests = models.ManyToManyField(APITest, related_name='test_suites')
    environment = models.ForeignKey(APIEnvironment, on_delete=models.SET_NULL, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class APITestSuiteResult(TimeStampedUUIDModel):
    suite = models.ForeignKey(APITestSuite, on_delete=models.CASCADE, related_name='suite_results')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    total_tests = models.IntegerField(default=0)
    passed_tests = models.IntegerField(default=0)
    failed_tests = models.IntegerField(default=0)
    total_time = models.FloatField(null=True, blank=True, help_text="Total execution time in seconds")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    results = models.ManyToManyField(APITestResult, related_name='suite_results')
    
    def __str__(self):
        return f"{self.suite.name} - {self.status}"

class APIAutomation(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    test_suite = models.ForeignKey(APITestSuite, on_delete=models.CASCADE, related_name='automations')
    schedule = models.CharField(max_length=100, blank=True, help_text="Cron expression for scheduling")
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    notification_email = models.EmailField(blank=True)
    retry_count = models.IntegerField(default=0)
    retry_delay = models.IntegerField(default=300, help_text="Retry delay in seconds")
    
    def __str__(self):
        return self.name
