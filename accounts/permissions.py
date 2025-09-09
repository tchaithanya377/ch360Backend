from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasRole(BasePermission):
    """Require one of the roles to access the view.

    Use by setting `required_roles = ['Admin', 'Registrar']` on the view.
    """

    def has_permission(self, request, view):
        roles = getattr(view, 'required_roles', None)
        user = request.user
        if not roles:
            return True
        if not user or not user.is_authenticated:
            return False
        user_roles = set(user.user_roles.select_related('role').values_list('role__name', flat=True))
        return any(r in user_roles for r in roles)


class HasAnyPermission(BasePermission):
    """Require any of the custom permissions by codename.

    Set `required_permissions = ['students.view_sensitive', 'fees.refund']` on the view.
    """

    def has_permission(self, request, view):
        perms = getattr(view, 'required_permissions', None)
        user = request.user
        if not perms:
            return True
        if not user or not user.is_authenticated:
            return False
        user_perms = set(
            user.user_roles
            .values_list('role__role_permissions__permission__codename', flat=True)
        )
        return any(p in user_perms for p in perms)


