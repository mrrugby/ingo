from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserRole
from apps.accounts.serializers import LoginSerializer, ManagedUserCreateSerializer, UserSerializer
from apps.properties.models import Property
from apps.tenants.models import TenantProfile


User = get_user_model()


def build_auth_payload(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["name"] = user.full_name
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    }


class EmailOrPhoneLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(build_auth_payload(serializer.validated_data["user"]))


class CurrentUserView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardSummaryView(APIView):
    def get(self, request):
        user = request.user

        if user.role == UserRole.SUPER_ADMIN:
            data = {
                "role": user.role,
                "counts": {
                    "landlords": User.objects.filter(role=UserRole.LANDLORD).count(),
                    "caretakers": User.objects.filter(role=UserRole.CARETAKER).count(),
                    "tenants": User.objects.filter(role=UserRole.TENANT).count(),
                    "properties": Property.objects.count(),
                    "pending_activations": TenantProfile.objects.filter(otp_used_at__isnull=True).count(),
                },
                "recent_landlords": UserSerializer(
                    User.objects.filter(role=UserRole.LANDLORD).order_by("-date_joined")[:5],
                    many=True,
                ).data,
            }
            return Response(data)

        if user.role == UserRole.LANDLORD:
            properties = Property.objects.filter(landlord=user).annotate(
                tenant_count=Count("tenant_profiles", distinct=True),
                pending_count=Count("tenant_profiles", filter=Q(tenant_profiles__otp_used_at__isnull=True), distinct=True),
            )
            data = {
                "role": user.role,
                "counts": {
                    "properties": properties.count(),
                    "caretakers": User.objects.filter(role=UserRole.CARETAKER, created_by=user).count(),
                    "tenants": TenantProfile.objects.filter(assigned_property__landlord=user).count(),
                    "pending_activations": TenantProfile.objects.filter(assigned_property__landlord=user, otp_used_at__isnull=True).count(),
                },
                "properties": [
                    {
                        "id": prop.id,
                        "name": prop.name,
                        "location": prop.location,
                        "tenant_count": prop.tenant_count,
                        "pending_count": prop.pending_count,
                    }
                    for prop in properties
                ],
            }
            return Response(data)

        if user.role == UserRole.CARETAKER:
            property_ids = Property.objects.filter(caretaker_assignments__caretaker=user).values_list("id", flat=True)
            data = {
                "role": user.role,
                "counts": {
                    "properties": property_ids.count(),
                    "tenants": TenantProfile.objects.filter(assigned_property_id__in=property_ids).count(),
                    "pending_activations": TenantProfile.objects.filter(assigned_property_id__in=property_ids, otp_used_at__isnull=True).count(),
                },
            }
            return Response(data)

        profile = TenantProfile.objects.select_related("assigned_property").get(user=user)
        data = {
            "role": user.role,
            "profile": {
                "name": user.full_name,
                "phone_number": user.phone_number,
                "property": {
                    "id": profile.assigned_property.id,
                    "name": profile.assigned_property.name,
                    "location": profile.assigned_property.location,
                },
                "activated_at": profile.activation_completed_at,
            },
        }
        return Response(data)


class UserManagementView(APIView):
    def get(self, request):
        user = request.user
        if user.role == UserRole.SUPER_ADMIN:
            queryset = User.objects.filter(role=UserRole.LANDLORD).order_by("full_name")
        elif user.role == UserRole.LANDLORD:
            queryset = User.objects.filter(role=UserRole.CARETAKER, created_by=user).order_by("full_name")
        else:
            return Response({"detail": "You do not have permission to view this list."}, status=status.HTTP_403_FORBIDDEN)

        return Response(UserSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = ManagedUserCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
