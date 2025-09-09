from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, LogoutView, RateLimitedTokenView, RateLimitedRefreshView, RolesPermissionsView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', RateLimitedTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', RateLimitedRefreshView.as_view(), name='token_refresh'),
    path('me/roles-permissions/', RolesPermissionsView.as_view(), name='me_roles_permissions'),
]


