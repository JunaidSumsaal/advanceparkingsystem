from rest_framework.permissions import BasePermission
from parking.models import ParkingFacility

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