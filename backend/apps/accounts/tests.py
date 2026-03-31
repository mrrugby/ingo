from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole


User = get_user_model()


class UserManagementApiTests(APITestCase):
    def setUp(self):
        self.super_admin = User.objects.create_superuser(
            email="owner@ingo.test",
            password="OwnerPass123",
            full_name="System Owner",
        )

    def test_super_admin_can_create_landlord(self):
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.post(
            "/api/auth/users/",
            {
                "full_name": "Grace Landlord",
                "email": "grace@example.com",
                "password": "SecurePass123",
                "role": UserRole.LANDLORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        landlord = User.objects.get(email="grace@example.com")
        self.assertEqual(landlord.role, UserRole.LANDLORD)
        self.assertEqual(landlord.created_by, self.super_admin)

