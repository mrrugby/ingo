from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.properties.models import CaretakerAssignment, Property
from apps.tenants.models import TenantProfile


User = get_user_model()


class TenantOnboardingApiTests(APITestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            email="landlord@ingo.test",
            password="LandlordPass123",
            full_name="Lorna Landlord",
            role=UserRole.LANDLORD,
        )
        self.caretaker = User.objects.create_user(
            email="caretaker@ingo.test",
            password="CaretakerPass123",
            full_name="Chris Caretaker",
            role=UserRole.CARETAKER,
            created_by=self.landlord,
        )
        self.property = Property.objects.create(
            landlord=self.landlord,
            name="Acacia Court",
            location="Nairobi West",
            description="Starter property",
        )
        CaretakerAssignment.objects.create(
            property=self.property,
            caretaker=self.caretaker,
            assigned_by=self.landlord,
        )

    def test_caretaker_can_create_and_activate_tenant(self):
        self.client.force_authenticate(user=self.caretaker)
        create_response = self.client.post(
            "/api/tenants/",
            {
                "full_name": "Tina Tenant",
                "phone_number": "+254700111222",
                "property_id": self.property.id,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["full_name"], "Tina Tenant")
        self.assertEqual(len(create_response.data["otp"]), 6)

        tenant_user = User.objects.get(phone_number="+254700111222")
        self.assertEqual(tenant_user.role, UserRole.TENANT)
        self.assertFalse(tenant_user.is_active)

        otp = create_response.data["otp"]
        self.client.force_authenticate(user=None)

        verify_response = self.client.post(
            "/api/tenants/activation/verify/",
            {"name": "Tina Tenant", "otp": otp},
            format="json",
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        activation_response = self.client.post(
            "/api/tenants/activation/complete/",
            {
                "activation_token": verify_response.data["activation_token"],
                "password": "TenantPass123",
                "phone_number": "+254799555444",
            },
            format="json",
        )
        self.assertEqual(activation_response.status_code, status.HTTP_200_OK)

        tenant_user.refresh_from_db()
        tenant_profile = TenantProfile.objects.get(user=tenant_user)
        self.assertTrue(tenant_user.is_active)
        self.assertEqual(tenant_user.phone_number, "+254799555444")
        self.assertIsNotNone(tenant_profile.activation_completed_at)
        self.assertEqual(tenant_profile.otp_hash, "")
        self.assertEqual(tenant_profile.otp_ciphertext, "")

        login_response = self.client.post(
            "/api/auth/login/",
            {"identifier": "+254799555444", "password": "TenantPass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data["user"]["role"], UserRole.TENANT)
        self.assertIn("access", login_response.data)
