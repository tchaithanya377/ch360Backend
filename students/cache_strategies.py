"""
Advanced Caching Strategies for Student Module
Optimized for 20K+ RPS with intelligent cache invalidation
"""

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import hashlib
import json
import time
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StudentCacheManager:
    """
    Advanced cache manager for student data with intelligent invalidation
    """
    
    # Cache key prefixes
    CACHE_PREFIXES = {
        'student_detail': 'student_detail',
        'student_list': 'student_list',
        'student_search': 'student_search',
        'student_statistics': 'student_statistics',
        'student_dashboard': 'student_dashboard',
        'student_analytics': 'student_analytics',
        'student_export': 'student_export',
    }
    
    # Cache TTL settings (in seconds)
    CACHE_TTL = {
        'student_detail': 600,      # 10 minutes
        'student_list': 300,        # 5 minutes
        'student_search': 120,      # 2 minutes
        'student_statistics': 900,  # 15 minutes
        'student_dashboard': 1800,  # 30 minutes
        'student_analytics': 3600,  # 1 hour
        'student_export': 60,       # 1 minute
    }
    
    @classmethod
    def generate_cache_key(cls, cache_type: str, **kwargs) -> str:
        """Generate cache key with consistent format"""
        prefix = cls.CACHE_PREFIXES.get(cache_type, 'student')
        
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_suffix = '_'.join([f"{k}_{v}" for k, v in sorted_kwargs])
            return f"{prefix}:{key_suffix}"
        
        return prefix
    
    @classmethod
    def get_cache_key_hash(cls, cache_type: str, **kwargs) -> str:
        """Generate hash-based cache key for complex parameters"""
        prefix = cls.CACHE_PREFIXES.get(cache_type, 'student')
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    @classmethod
    def get(cls, cache_type: str, **kwargs) -> Optional[Any]:
        """Get cached data"""
        cache_key = cls.generate_cache_key(cache_type, **kwargs)
        return cache.get(cache_key)
    
    @classmethod
    def set(cls, cache_type: str, data: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Set cached data"""
        cache_key = cls.generate_cache_key(cache_type, **kwargs)
        ttl = ttl or cls.CACHE_TTL.get(cache_type, 300)
        return cache.set(cache_key, data, ttl)
    
    @classmethod
    def delete(cls, cache_type: str, **kwargs) -> bool:
        """Delete specific cache entry"""
        cache_key = cls.generate_cache_key(cache_type, **kwargs)
        return cache.delete(cache_key)
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """Delete cache entries matching pattern (Redis only)"""
        if hasattr(cache, 'delete_pattern'):
            return cache.delete_pattern(pattern)
        return 0
    
    @classmethod
    def invalidate_student_caches(cls, student_id: str) -> None:
        """Invalidate all caches related to a specific student"""
        cache_keys_to_delete = [
            cls.generate_cache_key('student_detail', student_id=student_id),
            cls.generate_cache_key('student_documents', student_id=student_id),
            cls.generate_cache_key('student_enrollment_history', student_id=student_id),
        ]
        
        # Delete specific keys
        cache.delete_many(cache_keys_to_delete)
        
        # Delete pattern-based keys (for list caches)
        patterns_to_delete = [
            f"student_list:*",
            f"student_search:*",
            f"student_statistics*",
            f"student_dashboard*",
        ]
        
        for pattern in patterns_to_delete:
            cls.delete_pattern(pattern)
        
        logger.info(f"Invalidated caches for student {student_id}")
    
    @classmethod
    def invalidate_all_student_caches(cls) -> None:
        """Invalidate all student-related caches"""
        patterns_to_delete = [
            f"student_*",
        ]
        
        for pattern in patterns_to_delete:
            cls.delete_pattern(pattern)
        
        logger.info("Invalidated all student caches")


class StudentListCache:
    """
    Specialized cache for student list queries
    """
    
    @staticmethod
    def get_cache_key(request_params: Dict[str, Any]) -> str:
        """Generate cache key for list queries"""
        # Remove pagination parameters for cache key
        cache_params = {k: v for k, v in request_params.items() 
                       if k not in ['page', 'page_size', 'cursor']}
        
        return StudentCacheManager.get_cache_key_hash('student_list', **cache_params)
    
    @staticmethod
    def get_cached_list(request_params: Dict[str, Any]) -> Optional[Any]:
        """Get cached list data"""
        cache_key = StudentListCache.get_cache_key(request_params)
        return cache.get(cache_key)
    
    @staticmethod
    def set_cached_list(request_params: Dict[str, Any], data: Any, ttl: int = 300) -> bool:
        """Set cached list data"""
        cache_key = StudentListCache.get_cache_key(request_params)
        return cache.set(cache_key, data, ttl)
    
    @staticmethod
    def invalidate_list_caches() -> None:
        """Invalidate all list caches"""
        StudentCacheManager.delete_pattern("student_list:*")


class StudentSearchCache:
    """
    Specialized cache for student search queries
    """
    
    @staticmethod
    def get_cache_key(query: str, filters: Dict[str, Any] = None) -> str:
        """Generate cache key for search queries"""
        search_params = {'query': query}
        if filters:
            search_params.update(filters)
        
        return StudentCacheManager.get_cache_key_hash('student_search', **search_params)
    
    @staticmethod
    def get_cached_search(query: str, filters: Dict[str, Any] = None) -> Optional[Any]:
        """Get cached search results"""
        cache_key = StudentSearchCache.get_cache_key(query, filters)
        return cache.get(cache_key)
    
    @staticmethod
    def set_cached_search(query: str, data: Any, filters: Dict[str, Any] = None, ttl: int = 120) -> bool:
        """Set cached search results"""
        cache_key = StudentSearchCache.get_cache_key(query, filters)
        return cache.set(cache_key, data, ttl)
    
    @staticmethod
    def invalidate_search_caches() -> None:
        """Invalidate all search caches"""
        StudentCacheManager.delete_pattern("student_search:*")


class StudentStatisticsCache:
    """
    Specialized cache for student statistics
    """
    
    @staticmethod
    def get_cached_statistics() -> Optional[Any]:
        """Get cached statistics"""
        return StudentCacheManager.get('student_statistics')
    
    @staticmethod
    def set_cached_statistics(data: Any, ttl: int = 900) -> bool:
        """Set cached statistics"""
        return StudentCacheManager.set('student_statistics', data, ttl)
    
    @staticmethod
    def invalidate_statistics_cache() -> None:
        """Invalidate statistics cache"""
        StudentCacheManager.delete('student_statistics')


class StudentDashboardCache:
    """
    Specialized cache for dashboard metrics
    """
    
    @staticmethod
    def get_cached_dashboard_metrics() -> Optional[Any]:
        """Get cached dashboard metrics"""
        return StudentCacheManager.get('student_dashboard')
    
    @staticmethod
    def set_cached_dashboard_metrics(data: Any, ttl: int = 1800) -> bool:
        """Set cached dashboard metrics"""
        return StudentCacheManager.set('student_dashboard', data, ttl)
    
    @staticmethod
    def invalidate_dashboard_cache() -> None:
        """Invalidate dashboard cache"""
        StudentCacheManager.delete('student_dashboard')


class CacheWarmingService:
    """
    Service to warm up caches with frequently accessed data
    """
    
    @staticmethod
    def warm_student_statistics():
        """Warm up student statistics cache"""
        from .models import Student
        from django.db.models import Count, Q
        
        stats = Student.objects.aggregate(
            total_students=Count('id'),
            active_students=Count('id', filter=Q(status='ACTIVE')),
            inactive_students=Count('id', filter=Q(status='INACTIVE')),
            graduated_students=Count('id', filter=Q(status='GRADUATED'))
        )
        
        StudentStatisticsCache.set_cached_statistics(stats)
        logger.info("Warmed up student statistics cache")
    
    @staticmethod
    def warm_dashboard_metrics():
        """Warm up dashboard metrics cache"""
        from .models import Student
        from django.db.models import Count, Q
        from django.db.models.functions import TruncMonth
        
        metrics = Student.objects.aggregate(
            total_students=Count('id'),
            active_students=Count('id', filter=Q(status='ACTIVE')),
            inactive_students=Count('id', filter=Q(status='INACTIVE')),
            graduated_students=Count('id', filter=Q(status='GRADUATED'))
        )
        
        # Get distribution data
        year_distribution = dict(Student.objects.values('year_of_study').annotate(count=Count('id')))
        section_distribution = dict(Student.objects.values('section').annotate(count=Count('id')))
        
        # Monthly enrollments
        monthly_data = Student.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:12]
        
        monthly_enrollments = {str(item['month']): item['count'] for item in monthly_data}
        
        dashboard_data = {
            **metrics,
            'year_distribution': year_distribution,
            'section_distribution': section_distribution,
            'monthly_enrollments': monthly_enrollments
        }
        
        StudentDashboardCache.set_cached_dashboard_metrics(dashboard_data)
        logger.info("Warmed up dashboard metrics cache")
    
    @staticmethod
    def warm_frequently_accessed_students():
        """Warm up cache for frequently accessed students"""
        from .models import Student
        
        # Get top 100 most recently updated students
        recent_students = Student.objects.select_related(
            'department', 'academic_program'
        ).order_by('-updated_at')[:100]
        
        for student in recent_students:
            cache_key = StudentCacheManager.generate_cache_key('student_detail', student_id=student.id)
            if not cache.get(cache_key):
                # Cache student detail
                from .serializers import StudentDetailSerializer
                serializer = StudentDetailSerializer(student)
                cache.set(cache_key, serializer.data, 600)
        
        logger.info("Warmed up frequently accessed students cache")
    
    @classmethod
    def warm_all_caches(cls):
        """Warm up all caches"""
        cls.warm_student_statistics()
        cls.warm_dashboard_metrics()
        cls.warm_frequently_accessed_students()
        logger.info("Completed cache warming for all student data")


# Cache invalidation signals
@receiver(post_save, sender='students.Student')
def invalidate_student_cache_on_save(sender, instance, **kwargs):
    """Invalidate cache when student is saved"""
    StudentCacheManager.invalidate_student_caches(str(instance.id))


@receiver(post_delete, sender='students.Student')
def invalidate_student_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when student is deleted"""
    StudentCacheManager.invalidate_student_caches(str(instance.id))


@receiver(post_save, sender='students.StudentDocument')
def invalidate_student_document_cache(sender, instance, **kwargs):
    """Invalidate cache when student document is saved"""
    StudentCacheManager.invalidate_student_caches(str(instance.student.id))


@receiver(post_save, sender='students.StudentEnrollmentHistory')
def invalidate_student_enrollment_cache(sender, instance, **kwargs):
    """Invalidate cache when student enrollment history is saved"""
    StudentCacheManager.invalidate_student_caches(str(instance.student.id))


# Cache monitoring and analytics
class CacheAnalytics:
    """
    Cache performance analytics and monitoring
    """
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        if hasattr(cache, 'get_stats'):
            return cache.get_stats()
        
        return {
            'hit_rate': 0,
            'miss_rate': 0,
            'total_requests': 0,
            'cache_size': 0
        }
    
    @staticmethod
    def get_cache_hit_rate() -> float:
        """Get cache hit rate percentage"""
        stats = CacheAnalytics.get_cache_stats()
        total_requests = stats.get('total_requests', 0)
        if total_requests == 0:
            return 0.0
        
        hits = stats.get('hits', 0)
        return (hits / total_requests) * 100
    
    @staticmethod
    def get_cache_memory_usage() -> Dict[str, Any]:
        """Get cache memory usage"""
        if hasattr(cache, 'get_memory_usage'):
            return cache.get_memory_usage()
        
        return {
            'used_memory': 0,
            'max_memory': 0,
            'memory_usage_percentage': 0
        }
    
    @staticmethod
    def get_cache_recommendations() -> List[str]:
        """Get cache optimization recommendations"""
        recommendations = []
        
        hit_rate = CacheAnalytics.get_cache_hit_rate()
        if hit_rate < 70:
            recommendations.append("Consider increasing cache TTL for frequently accessed data")
        
        if hit_rate < 50:
            recommendations.append("Review cache key strategy and invalidation patterns")
        
        memory_usage = CacheAnalytics.get_cache_memory_usage()
        if memory_usage.get('memory_usage_percentage', 0) > 80:
            recommendations.append("Consider increasing cache memory or optimizing cache size")
        
        return recommendations
