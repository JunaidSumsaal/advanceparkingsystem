from rest_framework import permissions


class IsProviderOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['provider', 'admin', 'superuser']


class IsAdminOrSuperuser(permissions.BasePermission):
    """Allow only admin or superuser roles to manage other accounts."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['admin', 'superuser']
        )
