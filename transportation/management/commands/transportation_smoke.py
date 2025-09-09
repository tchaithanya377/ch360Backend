from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from datetime import date
from transportation.models import Stop, Route, RouteStop, Vehicle, Driver, VehicleAssignment, TripSchedule
from django.db.models import Q


class Command(BaseCommand):
    help = "Run transportation API smoke tests using DRF APIClient"

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'tchaitu377@gmail.com'
        password = '123456'
        username = 'tchaitu'

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            user.set_password(password)
            user.save()

        client = APIClient()
        client.force_authenticate(user=user)

        # List endpoints
        for path in [
            '/api/v1/transport/vehicles/',
            '/api/v1/transport/drivers/',
            '/api/v1/transport/stops/',
            '/api/v1/transport/routes/',
            '/api/v1/transport/route-stops/',
            '/api/v1/transport/assignments/',
            '/api/v1/transport/schedules/',
            '/api/v1/transport/passes/',
        ]:
            resp = client.get(path)
            if resp.status_code != 200:
                self.stderr.write(f"GET {path} failed: {resp.status_code} {resp.data}")
                return

        # Create or fetch Stops (idempotent)
        stop_ids = []
        for payload in [
            {'name': 'Gate A', 'landmark': 'Main Gate', 'latitude': 12.9716, 'longitude': 77.5946},
            {'name': 'Library', 'landmark': 'Central Library', 'latitude': 12.9721, 'longitude': 77.5950},
        ]:
            existing = Stop.objects.filter(name=payload['name'], landmark=payload['landmark']).first()
            if existing:
                stop_ids.append(existing.id)
                continue
            resp = client.post('/api/v1/transport/stops/', payload, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create stop failed: {resp.status_code} {resp.data}")
                return
            stop_ids.append(resp.data['id'])

        # Create Route
        # Create or fetch Route
        route = Route.objects.filter(name='Campus Loop').first()
        if route:
            route_id = route.id
        else:
            resp = client.post('/api/v1/transport/routes/', {
                'name': 'Campus Loop', 'description': 'Loop around campus', 'distance_km': '5.2', 'is_active': True
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create route failed: {resp.status_code} {resp.data}")
                return
            route_id = resp.data['id']

        # Attach route stops
        for idx, stop_id in enumerate(stop_ids, start=1):
            if RouteStop.objects.filter(route_id=route_id, stop_id=stop_id).exists():
                continue
            resp = client.post('/api/v1/transport/route-stops/', {
                'route': route_id, 'stop_id': stop_id, 'order_index': idx, 'arrival_offset_min': idx * 5
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create route-stop failed: {resp.status_code} {resp.data}")
                return

        # Create Vehicle
        vehicle = Vehicle.objects.filter(number_plate='KA01AB1234').first()
        if vehicle:
            vehicle_id = vehicle.id
        else:
            resp = client.post('/api/v1/transport/vehicles/', {
                'number_plate': 'KA01AB1234',
                'registration_number': 'REG-0001',
                'make': 'Tata',
                'model': 'Starbus',
                'capacity': 40,
                'is_active': True,
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create vehicle failed: {resp.status_code} {resp.data}")
                return
            vehicle_id = resp.data['id']

        # Create Driver
        driver = Driver.objects.filter(license_number='DL-TEST-001').first()
        if driver:
            driver_id = driver.id
        else:
            resp = client.post('/api/v1/transport/drivers/', {
                'full_name': 'Test Driver',
                'phone': '+919999999999',
                'license_number': 'DL-TEST-001',
                'license_expiry': str(date.today().replace(year=date.today().year + 3)),
                'is_active': True,
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create driver failed: {resp.status_code} {resp.data}")
                return
            driver_id = resp.data['id']

        # Create Assignment
        assignment = VehicleAssignment.objects.filter(vehicle_id=vehicle_id, route_id=route_id, is_active=True).first()
        if assignment:
            assignment_id = assignment.id
        else:
            resp = client.post('/api/v1/transport/assignments/', {
                'vehicle': vehicle_id,
                'driver': driver_id,
                'route': route_id,
                'start_date': str(date.today()),
                'is_active': True,
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create assignment failed: {resp.status_code} {resp.data}")
                return
            assignment_id = resp.data['id']

        # Create Schedule
        if not TripSchedule.objects.filter(assignment_id=assignment_id, day_of_week=0, departure_time='08:00:00').exists():
            resp = client.post('/api/v1/transport/schedules/', {
                'assignment': assignment_id,
                'day_of_week': 0,
                'departure_time': '08:00:00',
                'return_time': '17:00:00',
                'effective_from': str(date.today()),
            }, format='json')
            if resp.status_code not in (200, 201):
                self.stderr.write(f"Create schedule failed: {resp.status_code} {resp.data}")
                return

        self.stdout.write(self.style.SUCCESS('Transportation API smoke test passed.'))


