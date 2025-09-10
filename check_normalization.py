#!/usr/bin/env python
"""
Database Normalization Checker for CampusHub360
This script analyzes the current database schema for normalization issues.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campshub360.settings')
django.setup()

from django.db import connection
from students.models import Student, StudentContact, StudentAddress, StudentIdentifier
from departments.models import Department
from academics.models import AcademicProgram, Course, CourseSection


def check_student_normalization():
    """Check Student model normalization"""
    print("🔍 Checking Student Model Normalization...")
    
    issues = []
    
    # Check for redundant fields in Student model
    student_fields = [field.name for field in Student._meta.fields]
    
    redundant_contact_fields = [
        'father_name', 'mother_name', 'father_mobile', 'mother_mobile',
        'guardian_name', 'guardian_phone', 'guardian_email', 'guardian_relationship',
        'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
    ]
    
    redundant_address_fields = [
        'village', 'address_line1', 'address_line2', 'city', 'state', 
        'postal_code', 'country'
    ]
    
    redundant_identifier_fields = [
        'aadhar_number'
    ]
    
    # Check for redundant fields
    for field in redundant_contact_fields + redundant_address_fields + redundant_identifier_fields:
        if field in student_fields:
            issues.append(f"❌ Redundant field '{field}' found in Student model (should be in normalized tables)")
        else:
            print(f"  ✅ Field '{field}' properly normalized")
    
    # Check if normalized tables exist and have data
    try:
        contact_count = StudentContact.objects.count()
        address_count = StudentAddress.objects.count()
        identifier_count = StudentIdentifier.objects.count()
        
        print(f"  📊 StudentContact records: {contact_count}")
        print(f"  📊 StudentAddress records: {address_count}")
        print(f"  📊 StudentIdentifier records: {identifier_count}")
        
        if contact_count == 0:
            issues.append("⚠️  No StudentContact records found - contact data may not be normalized")
        if address_count == 0:
            issues.append("⚠️  No StudentAddress records found - address data may not be normalized")
        if identifier_count == 0:
            issues.append("⚠️  No StudentIdentifier records found - identifier data may not be normalized")
            
    except Exception as e:
        issues.append(f"❌ Error checking normalized tables: {str(e)}")
    
    return issues


def check_choice_fields():
    """Check for hardcoded choice fields"""
    print("\n🔍 Checking Choice Fields...")
    
    issues = []
    
    # Check Student model for hardcoded choices
    student_choices = [
        'GENDER_CHOICES', 'STATUS_CHOICES', 'YEAR_OF_STUDY_CHOICES',
        'SEMESTER_CHOICES', 'SECTION_CHOICES', 'QUOTA_CHOICES', 'RELIGION_CHOICES'
    ]
    
    for choice in student_choices:
        if hasattr(Student, choice):
            issues.append(f"❌ Hardcoded choice '{choice}' found (should be lookup table)")
        else:
            print(f"  ✅ Choice '{choice}' properly normalized")
    
    return issues


def check_foreign_key_relationships():
    """Check foreign key relationships"""
    print("\n🔍 Checking Foreign Key Relationships...")
    
    issues = []
    
    # Check Student model foreign keys
    student_fks = [field for field in Student._meta.fields if field.many_to_one]
    
    print(f"  📊 Student model has {len(student_fks)} foreign key relationships:")
    for fk in student_fks:
        print(f"    - {fk.name}: {fk.related_model.__name__ if fk.related_model else 'Unknown'}")
    
    # Check for missing foreign keys
    expected_fks = ['department', 'academic_program', 'current_academic_year', 'current_semester']
    for fk_name in expected_fks:
        if not any(fk.name == fk_name for fk in student_fks):
            issues.append(f"❌ Missing foreign key '{fk_name}' in Student model")
        else:
            print(f"  ✅ Foreign key '{fk_name}' properly defined")
    
    return issues


def check_data_consistency():
    """Check data consistency"""
    print("\n🔍 Checking Data Consistency...")
    
    issues = []
    
    try:
        # Check for students with missing required data
        total_students = Student.objects.count()
        students_without_dept = Student.objects.filter(department__isnull=True).count()
        students_without_program = Student.objects.filter(academic_program__isnull=True).count()
        
        print(f"  📊 Total students: {total_students}")
        print(f"  📊 Students without department: {students_without_dept}")
        print(f"  📊 Students without program: {students_without_program}")
        
        if students_without_dept > total_students * 0.1:  # More than 10%
            issues.append(f"⚠️  {students_without_dept} students missing department assignment")
        
        if students_without_program > total_students * 0.1:  # More than 10%
            issues.append(f"⚠️  {students_without_program} students missing program assignment")
            
    except Exception as e:
        issues.append(f"❌ Error checking data consistency: {str(e)}")
    
    return issues


def check_database_indexes():
    """Check database indexes"""
    print("\n🔍 Checking Database Indexes...")
    
    issues = []
    
    try:
        with connection.cursor() as cursor:
            # Check indexes on Student table
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'students_student' 
                ORDER BY indexname;
            """)
            
            indexes = cursor.fetchall()
            print(f"  📊 Found {len(indexes)} indexes on students_student table:")
            
            for index_name, index_def in indexes:
                print(f"    - {index_name}")
            
            # Check for missing critical indexes
            index_names = [idx[0] for idx in indexes]
            
            critical_indexes = [
                'students_student_dept_year_section_idx',
                'students_student_status_dept_idx',
                'students_student_roll_name_idx'
            ]
            
            for critical_idx in critical_indexes:
                if critical_idx in index_names:
                    print(f"  ✅ Critical index '{critical_idx}' found")
                else:
                    issues.append(f"❌ Missing critical index '{critical_idx}'")
                    
    except Exception as e:
        issues.append(f"❌ Error checking indexes: {str(e)}")
    
    return issues


def generate_normalization_report():
    """Generate comprehensive normalization report"""
    print("🚀 CampusHub360 Database Normalization Analysis")
    print("=" * 60)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_student_normalization())
    all_issues.extend(check_choice_fields())
    all_issues.extend(check_foreign_key_relationships())
    all_issues.extend(check_data_consistency())
    all_issues.extend(check_database_indexes())
    
    # Generate report
    print("\n📋 NORMALIZATION REPORT")
    print("=" * 60)
    
    if not all_issues:
        print("🎉 EXCELLENT! No normalization issues found!")
        print("✅ Your database schema is properly normalized.")
    else:
        print(f"⚠️  Found {len(all_issues)} normalization issues:")
        print()
        
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
        
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Remove redundant fields from Student model")
        print("2. Create lookup tables for hardcoded choices")
        print("3. Ensure all foreign key relationships are properly defined")
        print("4. Add missing database indexes for performance")
        print("5. Run the normalization migrations to fix these issues")
    
    # Calculate normalization score
    total_checks = 20  # Approximate number of checks
    issues_found = len(all_issues)
    score = max(0, ((total_checks - issues_found) / total_checks) * 100)
    
    print(f"\n📊 NORMALIZATION SCORE: {score:.1f}%")
    
    if score >= 90:
        print("🏆 EXCELLENT - Database is well normalized!")
    elif score >= 75:
        print("👍 GOOD - Minor normalization issues to address")
    elif score >= 50:
        print("⚠️  FAIR - Several normalization issues need attention")
    else:
        print("🔴 POOR - Significant normalization issues require immediate attention")
    
    return all_issues


if __name__ == "__main__":
    try:
        issues = generate_normalization_report()
        sys.exit(0 if not issues else 1)
    except Exception as e:
        print(f"❌ Error running normalization check: {str(e)}")
        sys.exit(1)
