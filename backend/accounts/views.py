from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, viewsets, status
from .utils import IsAdminOrFacilityProvider
from .models import User
from .serializers import UserSerializer, RegisterSerializer, AdminUserSerializer, ChangePasswordSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from parking.models import AttendantAssignmentLog, ParkingFacility
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminOrFacilityProvider]

    def get_queryset(self):
        qs = User.objects.all()
        role_filter = self.request.query_params.get('role')
        if role_filter:
            qs = qs.filter(role=role_filter)

        user = self.request.user
        if user.role == 'provider' or user.is_staff:
            facility_ids = ParkingFacility.objects.filter(provider=user).values_list('id', flat=True)
            qs = qs.filter(assigned_facilities__id__in=facility_ids).distinct()

        return qs

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == 'provider' and not instance.assigned_facilities.filter(provider=user).exists():
            raise PermissionDenied("You cannot delete users outside your facilities.")
        instance.delete()

class AddAttendantView(generics.CreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminOrFacilityProvider]

    def perform_create(self, serializer):
        user = self.request.user
        attendant = serializer.save(role='attendant')

        # If provider, assign attendant to their facilities
        if user.role == 'provider':
            facilities = ParkingFacility.objects.filter(provider=user)
            for facility in facilities:
                facility.attendants.add(attendant)


class FacilityAttendantManageView(APIView):
    """
    Manage attendants for a specific facility.
    GET: List attendants
    POST: Assign attendants
    DELETE: Remove attendants
    """
    permission_classes = [IsAdminOrFacilityProvider]

    def get_facility(self, request, facility_id):
        facility = get_object_or_404(ParkingFacility, id=facility_id)
        if request.user.role == 'provider' and facility.provider != request.user:
            raise PermissionDenied("Not authorized for this facility.")
        return facility

    def get(self, request, facility_id):
        """List attendants for the facility."""
        facility = self.get_facility(request, facility_id)
        attendants = facility.attendants.all()
        data = UserSerializer(attendants, many=True).data
        return Response(data)

    def post(self, request, facility_id):
        """Assign attendants to facility."""
        facility = self.get_facility(request, facility_id)
        attendant_ids = request.data.get('attendant_ids', [])

        # Filter only attendants
        attendants = User.objects.filter(id__in=attendant_ids, role='attendant')

        # Avoid duplicates
        new_attendants = [a for a in attendants if a not in facility.attendants.all()]
        facility.attendants.add(*new_attendants)

        # Log actions
        for a in new_attendants:
            AttendantAssignmentLog.objects.create(
                facility=facility,
                attendant=a,
                performed_by=request.user,
                action='assigned'
            )

        return Response({"detail": f"Assigned {len(new_attendants)} attendant(s) to {facility.name}."})

    def delete(self, request, facility_id):
        """Remove attendants from facility."""
        facility = self.get_facility(request, facility_id)
        attendant_ids = request.data.get('attendant_ids', [])
        attendants = User.objects.filter(id__in=attendant_ids, role='attendant')

        facility.attendants.remove(*attendants)

        # Log actions
        for a in attendants:
            AttendantAssignmentLog.objects.create(
                facility=facility,
                attendant=a,
                performed_by=request.user,
                action='removed'
            )

        return Response({"detail": f"Removed {attendants.count()} attendant(s) from {facility.name}."})


class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Blacklist the provided refresh token so it cannot be used again.
    POST payload: { "refresh": "<refresh_token>" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
