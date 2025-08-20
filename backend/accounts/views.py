from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, viewsets, status, filters
from .utils import IsAdminOrFacilityProvider, log_action
from .models import AuditLog, NewsletterSubscription, User
from .serializers import AuditLogSerializer, NewsletterSubscriptionSerializer, UserSerializer, RegisterSerializer, AdminUserSerializer, ChangePasswordSerializer
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
            log_action(self.request.user, "filter_users",
                       f"Filtered users by role: {role_filter}", self.request.ip_address)

        user = self.request.user
        if user.role == 'provider':
            facility_ids = ParkingFacility.objects.filter(
                provider=user).values_list('id', flat=True)
            qs = qs.filter(assigned_facilities__id__in=facility_ids).distinct()
            log_action(
                user, "view_users", f"Viewed users in facilities {facility_ids}", user.ip_address)
        if user.role == 'attendant':
            qs = qs.filter(assigned_facilities__attendants=user).distinct()
            log_action(user, "view_attendants",
                       "Viewed assigned attendants", user.ip_address)
        if user.is_staff:
            qs = qs.all()
            log_action(user, "view_all_users",
                       "Viewed all users", user.ip_address)
        return qs

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == 'provider' and not instance.assigned_facilities.filter(provider=user).exists():
            log_action(user, "delete_user_denied",
                       f"Attempted to delete user {instance.username} without permission", user.ip_address)
            raise PermissionDenied(
                "You cannot delete users outside your facilities.")
        instance.delete()


class AddAttendantView(generics.CreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminOrFacilityProvider]

    def perform_create(self, serializer):
        user = self.request.user
        attendant = serializer.save(role='attendant')
        if user.role == 'provider':
            facilities = ParkingFacility.objects.filter(provider=user)
            for facility in facilities:
                facility.attendants.add(attendant)
            log_action(user, "attendant_added",
                       f"Attendant {attendant.username} added", user.ip_address)


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
            log_action(request.user, "access_denied",
                       "Unauthorized access to facility", request.user.ip_address)
            raise PermissionDenied("Not authorized for this facility.")
        log_action(request.user, "access_facility",
                   f"Accessed facility {facility.name}", request.user.ip_address)
        return facility

    def get(self, request, facility_id):
        """List attendants for the facility."""
        facility = self.get_facility(request, facility_id)
        attendants = facility.attendants.all()
        data = UserSerializer(attendants, many=True).data
        log_action(request.user, "list_attendants",
                   f"Listed attendants for facility {facility.name}", request.user.ip_address)
        return Response(data)

    def post(self, request, facility_id):
        facility = self.get_facility(request, facility_id)

        ids = request.data.get(
            'attendant_ids') or request.data.get('attendant_id')
        if not ids:
            log_action(request.user, "assign_attendant_error",
                       "No attendant IDs provided", request.user.ip_address)
            return Response({"detail": "No attendant IDs provided."}, status=400)

        if isinstance(ids, int):
            ids = [ids]
            log_action(request.user, "assign_attendant_single",
                       f"Assigning single attendant ID {ids[0]}", request.user.ip_address)

        attendants = User.objects.filter(id__in=ids, role='attendant')
        new_attendants = [
            a for a in attendants if a not in facility.attendants.all()]
        facility.attendants.add(*new_attendants)
        log_action(request.user, "assign_attendant",
                   f"Assigned {len(new_attendants)} attendants to facility {facility.name}", request.user.ip_address)

        for a in new_attendants:
            AttendantAssignmentLog.objects.create(
                facility=facility,
                attendant=a,
                performed_by=request.user,
                action='assigned'
            )
        log_action(request.user, "attendant_assignment_log",
                   f"Attendant assignment logged for {facility.name}", request.user.ip_address)
        return Response({"detail": f"Assigned {len(new_attendants)} attendant(s) to {facility.name}."})

    def delete(self, request, facility_id):
        """Remove attendants from facility."""
        facility = self.get_facility(request, facility_id)

        ids = request.data.get(
            'attendant_ids') or request.data.get('attendant_id')
        if not ids:
            log_action(request.user, "remove_attendant_error",
                       "No attendant IDs provided", request.user.ip_address)
            return Response({"detail": "No attendant IDs provided."}, status=400)

        if isinstance(ids, int):
            ids = [ids]  # normalize to list
            log_action(request.user, "remove_attendant_single",
                       f"Removing single attendant ID {ids[0]}", request.user.ip_address)

        attendants = User.objects.filter(id__in=ids, role='attendant')

        facility.attendants.remove(*attendants)
        log_action(request.user, "remove_attendant",
                   f"Removed {len(attendants)} attendants from facility {facility.name}", request.user.ip_address)

        for a in attendants:
            AttendantAssignmentLog.objects.create(
                facility=facility,
                attendant=a,
                performed_by=request.user,
                action='removed'
            )
        log_action(request.user, "attendant_removal_log",
                   f"Attendant removal logged for {facility.name}", request.user.ip_address)
        return Response({"detail": f"Removed {attendants.count()} attendant(s) from {facility.name}."})


class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        log_action(self.request.user, "change_password",
                   "User requested password change", self.request)
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        log_action(user, "password_changed", "User changed password", request)
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


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "description", "user__username", "ip_address"]
    ordering_fields = ["created_at", "user"]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        user_id = self.request.query_params.get("user")
        if category:
            qs = qs.filter(category=category)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class NewsletterSubscriptionView(generics.RetrieveUpdateAPIView):
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = NewsletterSubscription.objects.get_or_create(
            user=self.request.user, 
            defaults={"email": self.request.user.email}
        )
        return obj


class PublicNewsletterSubscriptionView(generics.CreateAPIView):
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()
