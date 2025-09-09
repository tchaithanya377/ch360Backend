from datetime import date

from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AttendanceSession, AttendanceRecord
from .serializers import AttendanceSessionSerializer, AttendanceRecordSerializer
from academics.models import Timetable, CourseEnrollment


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all().select_related('course_section', 'timetable').prefetch_related(
        Prefetch('records', queryset=AttendanceRecord.objects.select_related('student'))
    )
    serializer_class = AttendanceSessionSerializer

    @action(detail=True, methods=['post'])
    def generate_records(self, request, pk=None):
        session = self.get_object()
        enrollments = CourseEnrollment.objects.filter(course_section=session.course_section, status='ENROLLED').select_related('student')
        created = 0
        for enrollment in enrollments:
            AttendanceRecord.objects.get_or_create(session=session, student=enrollment.student)
            created += 1
        return Response({
            'created_records': created,
            'total_records': session.records.count(),
        }, status=status.HTTP_200_OK)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all().select_related('session', 'student')
    serializer_class = AttendanceRecordSerializer

