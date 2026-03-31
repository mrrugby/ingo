from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.serializers import UserSerializer
from apps.accounts.views import build_auth_payload
from apps.tenants.models import TenantProfile
from apps.tenants.serializers import (
    CompleteTenantActivationSerializer,
    TenantCreateSerializer,
    TenantListSerializer,
    VerifyTenantOtpSerializer,
)


class TenantListCreateView(APIView):
    def get_queryset(self, user):
        queryset = TenantProfile.objects.select_related("user", "assigned_property").order_by("user__full_name")
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        if user.role == UserRole.LANDLORD:
            return queryset.filter(assigned_property__landlord=user)
        if user.role == UserRole.CARETAKER:
            return queryset.filter(assigned_property__caretaker_assignments__caretaker=user).distinct()
        if user.role == UserRole.TENANT:
            return queryset.filter(user=user)
        return queryset.none()

    def get(self, request):
        queryset = self.get_queryset(request.user)
        return Response(TenantListSerializer(queryset, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = TenantCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        data = TenantListSerializer(profile, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class VerifyTenantOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyTenantOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.validated_data["tenant_profile"]
        return Response(
            {
                "activation_token": serializer.validated_data["activation_token"],
                "tenant": {
                    "name": profile.user.full_name,
                    "phone_number": profile.user.phone_number,
                },
            }
        )


class CompleteTenantActivationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CompleteTenantActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        payload = build_auth_payload(profile.user)
        payload["tenant_profile"] = TenantListSerializer(profile, context={"request": request}).data
        return Response(payload)


class TenantOtpDetailView(APIView):
    def get_queryset(self, user):
        queryset = TenantProfile.objects.select_related("user", "assigned_property")
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        if user.role == UserRole.LANDLORD:
            return queryset.filter(assigned_property__landlord=user)
        if user.role == UserRole.CARETAKER:
            return queryset.filter(assigned_property__caretaker_assignments__caretaker=user).distinct()
        return queryset.none()

    def get(self, request, tenant_id):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.LANDLORD, UserRole.CARETAKER}:
            return Response({"detail": "You do not have permission to view OTP details."}, status=status.HTTP_403_FORBIDDEN)

        profile = get_object_or_404(self.get_queryset(request.user), user_id=tenant_id)
        return Response(
            {
                "tenant_id": profile.user_id,
                "tenant_name": profile.user.full_name,
                "otp": profile.reveal_otp(),
                "otp_created_at": profile.otp_created_at,
                "otp_used_at": profile.otp_used_at,
            }
        )
