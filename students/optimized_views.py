"""
High-Performance Optimized Views for Students Module
Implements caching, query optimization, and performance monitoring
"""
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q, Count, Avg
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Student, StudentDocument, StudentCustomFieldValue, StudentEnrollmentHistory
from .serializers import StudentSerializer, StudentDetailSerializer
from campshub360.cache_utils import cached_query, cached_model, cache_manager
from campshub360.performance_monitor import monitor_performance
from campshub360.security import rate_limit_by_user, log_security_events
import time


class HighPerformanceStudentViewSet(viewsets.ModelViewSet):
    """
    High-performance Student ViewSet with advanced caching and optimization
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'year_of_study', 'semester', 'section', 'status']
    search_fields = ['first_name', 'last_name', 'roll_number', 'email']
    ordering_fields = ['created_at', 'roll_number', 'first_name', 'last_name']
    ordering = ['roll_number']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'detail']:
            return StudentDetailSerializer
        return StudentSerializer
    
    @cached_query(ttl=300)  # Cache for 5 minutes
    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related"""
        return Student.objects.select_related(
            'user', 'created_by', 'updated_by'
        ).prefetch_related(
            'documents',
            'custom_field_values__custom_field',
            'enrollment_history'
        ).only(
            'id', 'roll_number', 'first_name', 'last_name', 'email',
            'academic_year', 'year_of_study', 'semester', 'section', 'status',
            'created_at', 'user_id', 'created_by_id', 'updated_by_id'
        )
    
    @monitor_performance
    @rate_limit_by_user
    @log_security_events
    def list(self, request, *args, **kwargs):
        """Optimized list view with caching"""
        # Check cache first
        cache_key = f"students_list:{hash(str(request.query_params))}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            request._cache_hit = True
            return Response(cached_result)
        
        request._cache_hit = False
        
        # Get queryset and apply filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            # Cache the result
            cache.set(cache_key, result.data, 300)  # 5 minutes
            return result
        
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        cache.set(cache_key, result, 300)
        return Response(result)
    
    @monitor_performance
    @rate_limit_by_user
    def retrieve(self, request, *args, **kwargs):
        """Optimized retrieve view with caching"""
        student_id = kwargs.get('pk')
        cache_key = f"student_detail:{student_id}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            request._cache_hit = True
            return Response(cached_result)
        
        request._cache_hit = False
        
        # Get student with optimized queries
        student = get_object_or_404(
            Student.objects.select_related(
                'user', 'created_by', 'updated_by'
            ).prefetch_related(
                Prefetch('documents', queryset=StudentDocument.objects.select_related('uploaded_by')),
                Prefetch('custom_field_values', queryset=StudentCustomFieldValue.objects.select_related('custom_field')),
                Prefetch('enrollment_history', queryset=StudentEnrollmentHistory.objects.all())
            ),
            pk=student_id
        )
        
        serializer = self.get_serializer(student)
        result = serializer.data
        
        # Cache the result
        cache.set(cache_key, result, 600)  # 10 minutes
        return Response(result)
    
    @action(detail=False, methods=['get'])
    @monitor_performance
    @cached_query(ttl=600)  # Cache for 10 minutes
    def statistics(self, request):
        """Get student statistics with caching"""
        cache_key = "student_statistics"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Calculate statistics
        stats = {
            'total_students': Student.objects.count(),
            'active_students': Student.objects.filter(status='ACTIVE').count(),
            'by_grade': dict(Student.objects.values('year_of_study').annotate(count=Count('id'))),
            'by_academic_year': dict(Student.objects.values('academic_year').annotate(count=Count('id'))),
            'by_section': dict(Student.objects.values('section').annotate(count=Count('id'))),
            'recent_enrollments': Student.objects.filter(
                created_at__gte=time.time() - 30*24*60*60  # Last 30 days
            ).count()
        }
        
        cache.set(cache_key, stats, 600)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    @monitor_performance
    def search(self, request):
        """Advanced search with full-text search capabilities"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter required'}, status=400)
        
        # Use database full-text search if available
        if len(query) > 2:
            # PostgreSQL full-text search
            students = Student.objects.extra(
                where=["to_tsvector('english', first_name || ' ' || last_name || ' ' || roll_number || ' ' || COALESCE(email, '')) @@ plainto_tsquery('english', %s)"],
                params=[query]
            ).select_related('user')[:50]  # Limit results
        else:
            # Fallback to regular search
            students = Student.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(roll_number__icontains=query) |
                Q(email__icontains=query)
            ).select_related('user')[:50]
        
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @monitor_performance
    def documents(self, request, pk=None):
        """Get student documents with caching"""
        cache_key = f"student_documents:{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        student = self.get_object()
        documents = student.documents.select_related('uploaded_by').all()
        
        # Serialize documents
        from .serializers import StudentDocumentSerializer
        serializer = StudentDocumentSerializer(documents, many=True)
        result = serializer.data
        
        cache.set(cache_key, result, 300)  # 5 minutes
        return Response(result)
    
    @action(detail=True, methods=['get'])
    @monitor_performance
    def enrollment_history(self, request, pk=None):
        """Get student enrollment history with caching"""
        cache_key = f"student_enrollment_history:{pk}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        student = self.get_object()
        history = student.enrollment_history.all().order_by('-created_at')
        
        # Serialize history
        from .serializers import StudentEnrollmentHistorySerializer
        serializer = StudentEnrollmentHistorySerializer(history, many=True)
        result = serializer.data
        
        cache.set(cache_key, result, 600)  # 10 minutes
        return Response(result)
    
    @action(detail=False, methods=['post'])
    @monitor_performance
    @rate_limit_by_user
    def bulk_import(self, request):
        """Bulk import students with performance optimization"""
        # This would implement bulk import with chunking and progress tracking
        # For now, return a placeholder response
        return Response({
            'message': 'Bulk import endpoint - implementation needed',
            'status': 'pending'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def perform_create(self, serializer):
        """Override create to invalidate cache"""
        instance = serializer.save()
        # Invalidate related caches
        cache.delete_many([
            'student_statistics',
            f"students_list:*",  # This would need more sophisticated cache invalidation
        ])
        return instance
    
    def perform_update(self, serializer):
        """Override update to invalidate cache"""
        instance = serializer.save()
        # Invalidate specific student cache
        cache.delete(f"student_detail:{instance.id}")
        cache.delete(f"student_documents:{instance.id}")
        cache.delete(f"student_enrollment_history:{instance.id}")
        cache.delete('student_statistics')
        return instance
    
    def perform_destroy(self, instance):
        """Override destroy to invalidate cache"""
        student_id = instance.id
        instance.delete()
        # Invalidate caches
        cache.delete_many([
            f"student_detail:{student_id}",
            f"student_documents:{student_id}",
            f"student_enrollment_history:{student_id}",
            'student_statistics',
        ])


class HighPerformanceStudentAnalyticsViewSet(viewsets.ViewSet):
    """
    High-performance analytics for student data
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    @monitor_performance
    @cached_query(ttl=1800)  # Cache for 30 minutes
    def dashboard_metrics(self, request):
        """Get dashboard metrics with caching"""
        cache_key = "student_dashboard_metrics"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Calculate comprehensive metrics
        metrics = {
            'total_students': Student.objects.count(),
            'active_students': Student.objects.filter(status='ACTIVE').count(),
            'inactive_students': Student.objects.filter(status='INACTIVE').count(),
            'grade_distribution': dict(Student.objects.values('year_of_study').annotate(count=Count('id'))),
            'section_distribution': dict(Student.objects.values('section').annotate(count=Count('id'))),
            'academic_year_distribution': dict(Student.objects.values('academic_year').annotate(count=Count('id'))),
            'recent_enrollments': Student.objects.filter(
                created_at__gte=time.time() - 7*24*60*60  # Last 7 days
            ).count(),
            'monthly_enrollments': self._get_monthly_enrollments(),
        }
        
        cache.set(cache_key, metrics, 1800)
        return Response(metrics)
    
    def _get_monthly_enrollments(self):
        """Get monthly enrollment statistics"""
        from django.db.models.functions import TruncMonth
        
        monthly_data = Student.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return {str(item['month']): item['count'] for item in monthly_data}
    
    @action(detail=False, methods=['get'])
    @monitor_performance
    @cached_query(ttl=3600)  # Cache for 1 hour
    def performance_insights(self, request):
        """Get performance insights and recommendations"""
        cache_key = "student_performance_insights"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Calculate performance insights
        insights = {
            'query_performance': self._analyze_query_performance(),
            'cache_efficiency': self._analyze_cache_efficiency(),
            'optimization_recommendations': self._get_optimization_recommendations(),
        }
        
        cache.set(cache_key, insights, 3600)
        return Response(insights)
    
    def _analyze_query_performance(self):
        """Analyze database query performance"""
        # This would analyze slow queries and provide insights
        return {
            'avg_query_time': 0.15,  # Placeholder
            'slow_queries': 0,
            'optimization_opportunities': []
        }
    
    def _analyze_cache_efficiency(self):
        """Analyze cache hit rates and efficiency"""
        # This would analyze cache performance
        return {
            'hit_rate': 85.5,  # Placeholder
            'miss_rate': 14.5,
            'recommendations': ['Increase cache TTL for frequently accessed data']
        }
    
    def _get_optimization_recommendations(self):
        """Get optimization recommendations"""
        return [
            'Consider adding database indexes for frequently queried fields',
            'Implement query result caching for complex aggregations',
            'Use database views for complex joins',
            'Consider implementing read replicas for analytics queries'
        ]
