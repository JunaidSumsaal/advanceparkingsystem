from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    AuditLogListView,
    FacilityAttendantManageView,
    RegisterView,
    ProfileView,
    AddAttendantView,
    AdminUserViewSet,
    ChangePasswordView,
    LogoutView
)

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/users/add-attendant/', AddAttendantView.as_view(), name='add-attendant'),
    path(
        'admin/facilities/<int:facility_id>/attendants/',
        FacilityAttendantManageView.as_view(),
        name='facility-attendants-manage'
    ),
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs"),
    path('', include(router.urls)),
]
