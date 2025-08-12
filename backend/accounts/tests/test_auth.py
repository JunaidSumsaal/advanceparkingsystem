from django.urls import reverse
from parking.models import AttendantAssignmentLog, ParkingFacility
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAPITests(APITestCase):

    def setUp(self):
        # Create roles
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="adminpass", role="admin"
        )
        self.provider_user = User.objects.create_user(
            username="provider", email="provider@example.com", password="providerpass", role="provider"
        )
        self.attendant_user = User.objects.create_user(
            username="attendant", email="attendant@example.com", password="attendantpass", role="attendant"
        )

        # URLs
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.profile_url = reverse("profile")

        # Create test facility
        self.facility = ParkingFacility.objects.create(
            name="Test Facility",
            provider=self.provider_user,
            latitude=0.0,   # Default test coordinate
            longitude=0.0,  # Default test coordinate
            address="123 Test Street",
            capacity=50
        )


    def authenticate(self, user):
        """Helper to authenticate a user and set token in client."""
        response = self.client.post(
            self.login_url, {"username": user.username, "password": "adminpass" if user.role == "admin" else f"{user.role}pass"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ---------------------------
    # Registration Tests
    # ---------------------------

    def test_register_user_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_missing_username(self):
        data = {
            "email": "nouser@example.com",
            "password": "testpass123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    # ---------------------------
    # Login & Token Tests
    # ---------------------------

    def test_login_success(self):
        data = {"username": "admin", "password": "adminpass"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        data = {"username": "admin", "password": "wrongpass"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        login_res = self.client.post(self.login_url, {"username": "admin", "password": "adminpass"})
        refresh_token = login_res.data["refresh"]
        response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    # ---------------------------
    # Profile View Tests
    # ---------------------------

    def test_get_profile_authenticated(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "admin")

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # AdminUserViewSet Tests
    # ---------------------------

    def test_admin_can_list_all_users(self):
        self.authenticate(self.admin_user)
        url = reverse("admin-users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_provider_sees_only_their_attendants(self):
        self.authenticate(self.provider_user)
        url = reverse("admin-users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Providers have no attendants yet
        self.assertEqual(len(response.data), 0)

    def test_admin_can_create_any_user(self):
        self.authenticate(self.admin_user)
        url = reverse("add-attendant")
        data = {"username": "newatt", "email": "att@example.com", "password": "pass123", "role": "attendant"}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newatt").exists())

    def test_provider_role_forced_on_attendant_creation(self):
        self.authenticate(self.provider_user)
        url = reverse("admin-users-list")
        data = {"username": "forcedatt", "email": "f@example.com", "password": "pass123", "role": "admin"}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="forcedatt").role, "attendant")

    # ---------------------------
    # FacilityAttendantManageView Tests
    # ---------------------------

    def test_assign_attendant(self):
        self.authenticate(self.provider_user)
        url = reverse("facility-attendants-manage", args=[self.facility.id])
        data = {"action": "assign", "attendant_id": self.attendant_user.id}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(AttendantAssignmentLog.objects.filter(
            attendant=self.attendant_user, facility=self.facility).exists())

    def test_remove_attendant(self):
        self.authenticate(self.provider_user)
        # First assign
        AttendantAssignmentLog.objects.create(attendant=self.attendant_user, facility=self.facility)
        url = reverse("facility-attendants-manage", args=[self.facility.id])
        data = {"action": "remove", "attendant_id": self.attendant_user.id}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(AttendantAssignmentLog.objects.filter(
            attendant=self.attendant_user, facility=self.facility).exists())

    def test_provider_cannot_manage_other_facility(self):
        other_provider = User.objects.create_user(
            username="prov2", email="p2@example.com", password="pass123", role="provider")
        other_facility = ParkingFacility.objects.create(
            name="Other Facility",
            provider=other_provider,
            latitude=0.0,
            longitude=0.0
        )

        self.authenticate(self.provider_user)
        url = reverse("facility-attendants-manage", args=[other_facility.id])
        res = self.client.post(url, {"action": "assign", "attendant_id": self.attendant_user.id})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
