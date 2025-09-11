"""
Optimized URL Configuration for Student Module
High-performance routing for 20K+ RPS
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .performance_optimizations import OptimizedStudentViewSet, StudentAnalyticsViewSet

# Create optimized router for high-performance endpoints
router = DefaultRouter()
router.register(r'api/students', OptimizedStudentViewSet, basename='student-optimized')
router.register(r'api/analytics', StudentAnalyticsViewSet, basename='student-analytics')

# Legacy router for backward compatibility
legacy_router = DefaultRouter()
legacy_router.register(r'api/students-legacy', views.StudentViewSet, basename='student-legacy')
legacy_router.register(r'api/enrollment-history', views.StudentEnrollmentHistoryViewSet, basename='enrollment-history')
legacy_router.register(r'api/documents', views.StudentDocumentViewSet, basename='student-documents')
legacy_router.register(r'api/custom-fields', views.CustomFieldViewSet, basename='custom-field')
legacy_router.register(r'api/custom-field-values', views.StudentCustomFieldValueViewSet, basename='custom-field-value')

app_name = 'students'

urlpatterns = [
    # High-performance API routes
    path('', include(router.urls)),
    
    # Legacy API routes (for backward compatibility)
    path('legacy/', include(legacy_router.urls)),
    
    # Web interface routes
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('list/', views.student_list_view, name='list'),
    path('detail/<uuid:student_id>/', views.student_detail_view, name='detail'),
    
    # High-performance student division and assignment routes
    path('api/students/divisions/', OptimizedStudentViewSet.as_view({'get': 'divisions'}), name='student-divisions-optimized'),
    path('api/students/assign/', OptimizedStudentViewSet.as_view({'post': 'assign_students'}), name='assign-students-optimized'),
    path('api/students/bulk-assign/', OptimizedStudentViewSet.as_view({'post': 'bulk_assign_by_criteria'}), name='bulk-assign-students-optimized'),
    path('api/students/division-statistics/', OptimizedStudentViewSet.as_view({'get': 'division_statistics'}), name='division-statistics-optimized'),
    
    # Legacy student division routes (for backward compatibility)
    path('api/students-legacy/divisions/', views.StudentViewSet.as_view({'get': 'divisions'}), name='student-divisions-legacy'),
    path('api/students-legacy/assign/', views.StudentViewSet.as_view({'post': 'assign_students'}), name='assign-students-legacy'),
    path('api/students-legacy/bulk-assign/', views.StudentViewSet.as_view({'post': 'bulk_assign_by_criteria'}), name='bulk-assign-students-legacy'),
    path('api/students-legacy/division-statistics/', views.StudentViewSet.as_view({'get': 'division_statistics'}), name='division-statistics-legacy'),
    
    # High-performance analytics routes
    path('api/analytics/dashboard-metrics/', StudentAnalyticsViewSet.as_view({'get': 'dashboard_metrics'}), name='dashboard-metrics'),
    path('api/analytics/performance-metrics/', StudentAnalyticsViewSet.as_view({'get': 'performance_metrics'}), name='performance-metrics'),
    
    # High-performance search and export routes
    path('api/students/search/', OptimizedStudentViewSet.as_view({'get': 'search'}), name='student-search-optimized'),
    path('api/students/export/', OptimizedStudentViewSet.as_view({'get': 'bulk_export'}), name='student-export-optimized'),
    path('api/students/statistics/', OptimizedStudentViewSet.as_view({'get': 'statistics'}), name='student-statistics-optimized'),
    
    # Legacy search and export routes (for backward compatibility)
    path('api/students-legacy/search/', views.StudentViewSet.as_view({'get': 'search'}), name='student-search-legacy'),
    path('api/students-legacy/statistics/', views.StudentViewSet.as_view({'get': 'statistics'}), name='student-statistics-legacy'),
]
