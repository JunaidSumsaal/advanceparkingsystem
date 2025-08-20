from .models import AuditLog
from rest_framework.permissions import BasePermission
from parking.models import ParkingFacility
import logging

logger = logging.getLogger(__name__)


class IsAdminOrFacilityProvider(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role in ['admin', 'superuser']:
            return True

        if user.role == 'provider':
            facility_id = view.kwargs.get('facility_id')
            if not facility_id:
                return False
            try:
                facility = ParkingFacility.objects.get(id=facility_id)
            except ParkingFacility.DoesNotExist:
                return False
            return facility.provider == user

        return False


class IsProviderOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['provider', 'admin', 'superuser']


class IsAdminOrSuperuser(BasePermission):
    """Allow only admin or superuser roles to manage other accounts."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['admin', 'superuser']
        )


class IsAttendantOrDriver(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['attendant', 'driver']


class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['driver']


class IsAttendant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['attendant']


def log_action(user, action, description="", request=None):
    ip = None
    agent = None
    if request:
        ip = request.META.get("REMOTE_ADDR")
        agent = request.META.get("HTTP_USER_AGENT", "")
    AuditLog.objects.create(
        user=user if user.is_authenticated else None,
        action=action,
        description=description,
        ip_address=ip,
        user_agent=agent
    )

    logger.info(
        description,
        extra={
            "user": getattr(user, "username", "anonymous" if not user or not user.is_authenticated else user.username),
            "action": action,
            "ip": ip,
            "user_agent": agent,
            "session_id": getattr(request, "session", {}).session_key if request and hasattr(request, "session") else None,
        }
    )
