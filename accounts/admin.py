from django.contrib import admin
from django.contrib.auth.models import Group
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
    # Keep Groups visible; hide granular user_permissions for simplicity
    exclude = ('user_permissions',)

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'must_change_password')
        }),
        ('Timestamps', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Groups', {
            'fields': ('groups',)
        }),
    )


admin.site.unregister = getattr(admin.site, 'unregister', lambda model: None)

# Hide custom RBAC models from admin menu to avoid duplication; manage via Django Groups instead
try:
    from .models import Role, Permission as CustomPermission, RolePermission, UserRole
    for mdl in (Role, CustomPermission, RolePermission, UserRole):
        try:
            admin.site.unregister(mdl)
        except Exception:
            pass
except Exception:
    pass

# Keep operational/auth tables visible as needed
admin.site.register(AuthIdentifier)
admin.site.register(FailedLogin)
admin.site.register(PasswordReset)
admin.site.register(MfaSetup)
admin.site.register(UserSession)
admin.site.register(AuditLog)


# Ensure Django Group admin remains available (do not unregister)

