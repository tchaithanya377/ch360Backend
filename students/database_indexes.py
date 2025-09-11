"""
Database Index Optimizations for Student Module
Critical indexes for 20K+ RPS performance
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add critical database indexes for high-performance student queries
    """
    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        # Critical indexes for high-traffic queries
        
        # 1. Composite index for department + year + section (most common filter)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_dept_year_section_status ON students_student (department_id, year_of_study, section, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_dept_year_section_status;"
        ),
        
        # 2. Index for academic program + year (common filter)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_program_year_status ON students_student (academic_program_id, year_of_study, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_program_year_status;"
        ),
        
        # 3. Index for roll number searches (exact matches)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_roll_number_gin ON students_student USING gin (roll_number gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_roll_number_gin;"
        ),
        
        # 4. Full-text search index for names and email
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_fulltext_search ON students_student USING gin (to_tsvector('english', first_name || ' ' || last_name || ' ' || COALESCE(email, '')));",
            reverse_sql="DROP INDEX IF EXISTS idx_student_fulltext_search;"
        ),
        
        # 5. Index for email searches (unique constraint already exists, but add for performance)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_email_gin ON students_student USING gin (email gin_trgm_ops) WHERE email IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_email_gin;"
        ),
        
        # 6. Index for academic year + semester combinations
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_academic_year_semester ON students_student (academic_year, semester, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_academic_year_semester;"
        ),
        
        # 7. Index for created_at for time-based queries
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_created_at_status ON students_student (created_at DESC, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_created_at_status;"
        ),
        
        # 8. Index for user relationship (if students have user accounts)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_user_id ON students_student (user_id) WHERE user_id IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_user_id;"
        ),
        
        # 9. Index for current academic year and semester (FK relationships)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_current_academic_semester ON students_student (current_academic_year_id, current_semester_id, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_current_academic_semester;"
        ),
        
        # 10. Index for quota and caste (for reporting)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_quota_caste ON students_student (quota_id, caste_id, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_quota_caste;"
        ),
        
        # 11. Partial index for active students only (most queries filter by status)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_active_only ON students_student (department_id, academic_program_id, year_of_study, semester, section) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_active_only;"
        ),
        
        # 12. Index for enrollment date queries
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_enrollment_date ON students_student (enrollment_date DESC, status) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_enrollment_date;"
        ),
        
        # 13. Index for gender distribution queries
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_gender_status ON students_student (gender, status, department_id) WHERE status = 'ACTIVE';",
            reverse_sql="DROP INDEX IF EXISTS idx_student_gender_status;"
        ),
        
        # 14. Index for mobile number searches
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_mobile_gin ON students_student USING gin (student_mobile gin_trgm_ops) WHERE student_mobile IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_mobile_gin;"
        ),
        
        # 15. Index for father/mother name searches
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_parent_names_gin ON students_student USING gin (father_name gin_trgm_ops, mother_name gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_parent_names_gin;"
        ),
        
        # 16. Index for address-based searches
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_address_gin ON students_student USING gin (city gin_trgm_ops, state gin_trgm_ops, village gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_address_gin;"
        ),
        
        # 17. Index for Aadhar number searches (if needed for verification)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_aadhar ON students_student (aadhar_number) WHERE aadhar_number IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_aadhar;"
        ),
        
        # 18. Index for rank-based queries
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_rank ON students_student (rank, academic_program_id, year_of_study) WHERE rank IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_rank;"
        ),
        
        # 19. Index for updated_at for audit queries
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_updated_at ON students_student (updated_at DESC, updated_by_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_updated_at;"
        ),
        
        # 20. Index for expected graduation date
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_student_graduation_date ON students_student (expected_graduation_date, status) WHERE expected_graduation_date IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_student_graduation_date;"
        ),
    ]


# Additional database optimization functions
def optimize_database_settings():
    """
    Database configuration optimizations for PostgreSQL
    """
    return {
        'shared_preload_libraries': 'pg_stat_statements',
        'track_activities': 'on',
        'track_counts': 'on',
        'track_io_timing': 'on',
        'track_functions': 'all',
        'log_statement': 'all',
        'log_min_duration_statement': 1000,  # Log queries taking more than 1 second
        'random_page_cost': 1.1,  # SSD optimization
        'effective_cache_size': '4GB',  # Adjust based on available RAM
        'work_mem': '256MB',  # For sorting and hashing
        'maintenance_work_mem': '1GB',  # For maintenance operations
        'checkpoint_completion_target': 0.9,
        'wal_buffers': '64MB',
        'default_statistics_target': 100,
        'random_page_cost': 1.1,
        'effective_io_concurrency': 200,  # For SSD
    }


def get_query_optimization_recommendations():
    """
    Query optimization recommendations for student queries
    """
    return [
        {
            'query_type': 'student_list',
            'optimization': 'Use select_related() for foreign keys and only() for specific fields',
            'example': 'Student.objects.select_related("department", "academic_program").only("id", "roll_number", "first_name", "last_name")'
        },
        {
            'query_type': 'student_search',
            'optimization': 'Use database full-text search for better performance',
            'example': 'Student.objects.extra(where=["to_tsvector(...) @@ plainto_tsquery(...)"])'
        },
        {
            'query_type': 'student_statistics',
            'optimization': 'Use database aggregation instead of Python loops',
            'example': 'Student.objects.aggregate(total=Count("id"), active=Count("id", filter=Q(status="ACTIVE")))'
        },
        {
            'query_type': 'student_bulk_operations',
            'optimization': 'Use bulk_create, bulk_update for multiple records',
            'example': 'Student.objects.bulk_create(students, batch_size=1000)'
        },
        {
            'query_type': 'student_filtering',
            'optimization': 'Use database-level filtering with proper indexes',
            'example': 'Student.objects.filter(department_id=dept_id, year_of_study=year, status="ACTIVE")'
        }
    ]
