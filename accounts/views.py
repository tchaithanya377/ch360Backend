from rest_framework import generics, permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import AuthIdentifier, IdentifierType
from django.contrib.auth.models import Group
try:
    from ratelimit.decorators import ratelimit
except Exception:  # Fallback if ratelimit isn't installed in the running env
    def ratelimit(*args, **kwargs):
        def _decorator(view):
            return view
        return _decorator
from django.utils.decorators import method_decorator
from django.conf import settings
from students.signals import record_session
from accounts.utils import extract_client_ip, geolocate_ip

from .serializers import RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class RollOrEmailTokenSerializer(TokenObtainPairSerializer):
    """Custom token serializer accepting roll number or email as username field."""

    def validate(self, attrs):
        username = attrs.get('username') or attrs.get(self.username_field)
        password = attrs.get('password')

        user = None
        # Try by email first
        if username:
            user = self._get_user_by_identifier(username)

        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials', code='authorization')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials', code='authorization')

        data = super().validate({'email': user.email, 'password': password})

        request = self.context.get('request')
        if request:
            # record base session
            usession = record_session(user, request)
            # enrich with geo info immediately when available (ignore if DB not migrated yet)
            try:
                ip = extract_client_ip(request)
                raw, country, region, city, lat, lon = geolocate_ip(ip)
                if usession and (country or raw):
                    usession.country = country
                    usession.region = region
                    usession.city = city
                    usession.latitude = lat
                    usession.longitude = lon
                    if raw:
                        usession.location_raw = raw
                    usession.save(update_fields=['country','region','city','latitude','longitude','location_raw'])
            except Exception:
                # DB might not have new columns yet; skip enrichment
                pass

        return data

    def _get_user_by_identifier(self, identifier: str):
        # Match by email
        try:
            return User.objects.get(email__iexact=identifier)
        except User.DoesNotExist:
            pass
        # Match by roll number via AuthIdentifier (stored as USERNAME)
        auth_ids = AuthIdentifier.objects.filter(
            Q(identifier__iexact=identifier),
            Q(id_type=IdentifierType.USERNAME) | Q(id_type=IdentifierType.EMAIL)
        ).select_related('user')
        if auth_ids.exists():
            return auth_ids.first().user
        # As fallback, match username field directly
        try:
            return User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            return None


class RollOrEmailTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = RollOrEmailTokenSerializer


@method_decorator(ratelimit(key='ip', rate=getattr(settings, 'AUTH_RATE_LIMIT_TOKEN', '5/m'), method='POST', block=True), name='post')
class RateLimitedTokenView(RollOrEmailTokenView):
    pass


@method_decorator(ratelimit(key='ip', rate=getattr(settings, 'AUTH_RATE_LIMIT_REFRESH', '10/m'), method='POST', block=True), name='post')
class RateLimitedRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class RolesPermissionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.core.cache import cache
        cache_key = f"rolesperms:{request.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Use Django Groups as roles
        roles = list(
            request.user.groups.values_list('name', flat=True)
        )
        # Use Django auth permissions the user has (including via groups)
        perms = sorted(request.user.get_all_permissions())
        payload = {'roles': roles, 'permissions': perms}
        cache.set(cache_key, payload, timeout=60)
        return Response(payload)
