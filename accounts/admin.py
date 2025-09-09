from django.contrib import admin
from .models import (
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    AuthIdentifier,
    FailedLogin,
    PasswordReset,
    MfaSetup,
    UserSession,
    AuditLog,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_verified', 'last_login')
    search_fields = ('email', 'username')


admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
admin.site.register(AuthIdentifier)
admin.site.register(FailedLogin)
admin.site.register(PasswordReset)
admin.site.register(MfaSetup)
admin.site.register(UserSession)
admin.site.register(AuditLog)


