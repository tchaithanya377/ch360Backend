"""
Management command to bulk create users for performance testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import Role, UserRole
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Bulk create users for performance testing'

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=100, help='Number of students to create')
        parser.add_argument('--faculty', type=int, default=50, help='Number of faculty to create')
        parser.add_argument('--admins', type=int, default=10, help='Number of admins to create')
        parser.add_argument('--password', type=str, default='TestPass123!', help='Default password for all users')
        parser.add_argument('--role-assign', action='store_true', help='Assign roles to created users')

    def handle(self, *args, **options):
        students_count = options['students']
        faculty_count = options['faculty']
        admins_count = options['admins']
        password = options['password']
        assign_roles = options['role_assign']

        self.stdout.write(f"Creating {students_count} students, {faculty_count} faculty, {admins_count} admins...")

        with transaction.atomic():
            # Create students
            if students_count > 0:
                students = self.create_users_bulk('student', students_count, password)
                self.stdout.write(f"✅ Created {len(students)} students")
                
                if assign_roles:
                    self.assign_roles_bulk(students, 'student')

            # Create faculty
            if faculty_count > 0:
                faculty = self.create_users_bulk('faculty', faculty_count, password)
                self.stdout.write(f"✅ Created {len(faculty)} faculty")
                
                if assign_roles:
                    self.assign_roles_bulk(faculty, 'faculty')

            # Create admins
            if admins_count > 0:
                admins = self.create_users_bulk('admin', admins_count, password)
                self.stdout.write(f"✅ Created {len(admins)} admins")
                
                if assign_roles:
                    self.assign_roles_bulk(admins, 'admin')

        self.stdout.write(self.style.SUCCESS('✅ Bulk user creation completed!'))

    def create_users_bulk(self, role_type: str, count: int, password: str):
        """Create users in bulk using bulk_create"""
        users = []
        for i in range(count):
            user = User(
                username=f"test_{role_type}_{i}",
                email=f"test_{role_type}_{i}@example.com",
                is_verified=True,
                is_active=True
            )
            user.set_password(password)
            users.append(user)

        # Bulk create
        created_users = User.objects.bulk_create(users, batch_size=1000)
        return created_users

    def assign_roles_bulk(self, users, role_name: str):
        """Assign roles in bulk"""
        try:
            role = Role.objects.get(name=role_name)
            user_roles = []
            
            for user in users:
                user_role = UserRole(user=user, role=role)
                user_roles.append(user_role)
            
            # Bulk create role assignments
            UserRole.objects.bulk_create(user_roles, batch_size=1000, ignore_conflicts=True)
            self.stdout.write(f"✅ Assigned {role_name} role to {len(users)} users")
            
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"⚠️  Role '{role_name}' not found, skipping role assignment"))
