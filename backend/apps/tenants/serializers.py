from __future__ import annotations

import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import UserRole
from apps.common.phone import normalize_phone_number
from apps.properties.models import Property
from apps.tenants.models import TenantProfile


User = get_user_model()
ACTIVATION_SALT = "tenant-activation"
ACTIVATION_TOKEN_MAX_AGE_SECONDS = 900


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def build_activation_token(profile: TenantProfile) -> str:
    return signing.dumps({"tenant_profile_id": profile.id}, salt=ACTIVATION_SALT)


def read_activation_token(token: str) -> int:
    payload = signing.loads(token, salt=ACTIVATION_SALT, max_age=ACTIVATION_TOKEN_MAX_AGE_SECONDS)
    return int(payload["tenant_profile_id"])


class TenantListSerializer(serializers.ModelSerializer):
    tenant_id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    property = serializers.IntegerField(source="assigned_property.id", read_only=True)
    otp = serializers.SerializerMethodField()
    property_name = serializers.CharField(source="assigned_property.name", read_only=True)

    class Meta:
        model = TenantProfile
        fields = (
            "id",
            "tenant_id",
            "full_name",
            "phone_number",
            "is_active",
            "property",
            "property_name",
            "otp",
            "otp_created_at",
            "otp_used_at",
            "activation_completed_at",
        )

    def get_otp(self, obj):
        request = self.context.get("request")
        if not request or not getattr(request.user, "is_authenticated", False):
            return None
        if request.user.role not in {UserRole.LANDLORD, UserRole.CARETAKER, UserRole.SUPER_ADMIN}:
            return None
        return obj.reveal_otp()


class TenantCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=32)
    property_id = serializers.IntegerField()

    def validate_phone_number(self, value):
        normalized = normalize_phone_number(value)
        if not normalized:
            raise serializers.ValidationError("A valid phone number is required.")
        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return normalized

    def validate_property_id(self, value):
        request = self.context["request"]
        property_obj = Property.objects.filter(id=value).first()
        if not property_obj:
            raise serializers.ValidationError("Property not found.")

        if request.user.role == UserRole.LANDLORD and property_obj.landlord_id != request.user.id:
            raise serializers.ValidationError("You can only create tenants for your properties.")

        if request.user.role == UserRole.CARETAKER:
            is_assigned = property_obj.caretaker_assignments.filter(caretaker=request.user).exists()
            if not is_assigned:
                raise serializers.ValidationError("You are not assigned to this property.")

        self.context["property"] = property_obj
        return value

    def validate(self, attrs):
        if self.context["request"].user.role not in {UserRole.LANDLORD, UserRole.CARETAKER}:
            raise serializers.ValidationError("Only landlords and caretakers can create tenants.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        property_obj = self.context["property"]
        creator = self.context["request"].user
        raw_otp = generate_otp()
        user = User.objects.create_user(
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            role=UserRole.TENANT,
            created_by=creator,
            is_active=False,
        )
        profile = TenantProfile.objects.create(user=user, assigned_property=property_obj, created_by=creator)
        profile.issue_otp(raw_otp)
        profile.save()
        self.context["raw_otp"] = raw_otp
        return profile


class VerifyTenantOtpSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        name = attrs["name"].strip()
        otp = attrs["otp"].strip()
        profiles = TenantProfile.objects.select_related("user").filter(user__full_name__iexact=name, otp_used_at__isnull=True)

        matched_profile = None
        for profile in profiles:
            if profile.verify_otp(otp):
                matched_profile = profile
                break

        if matched_profile is None:
            raise serializers.ValidationError("Name and OTP do not match any pending tenant account.")

        attrs["tenant_profile"] = matched_profile
        attrs["activation_token"] = build_activation_token(matched_profile)
        return attrs


class CompleteTenantActivationSerializer(serializers.Serializer):
    activation_token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=False)

    def validate(self, attrs):
        try:
            profile_id = read_activation_token(attrs["activation_token"])
        except signing.SignatureExpired as exc:
            raise serializers.ValidationError({"activation_token": "Activation session is invalid or expired."}) from exc
        except signing.BadSignature as exc:
            raise serializers.ValidationError({"activation_token": "Activation session is invalid or expired."}) from exc

        profile = TenantProfile.objects.select_related("user").filter(id=profile_id).first()
        if not profile or profile.activation_completed_at:
            raise serializers.ValidationError({"activation_token": "This tenant account has already been activated."})

        attrs["tenant_profile"] = profile

        if "phone_number" in attrs:
            normalized_phone = normalize_phone_number(attrs["phone_number"])
            if not normalized_phone:
                raise serializers.ValidationError({"phone_number": "A valid phone number is required."})
            existing_user = User.objects.filter(phone_number=normalized_phone).exclude(id=profile.user_id).exists()
            if existing_user:
                raise serializers.ValidationError({"phone_number": "That phone number is already in use."})
            attrs["phone_number"] = normalized_phone

        validate_password(attrs["password"], user=profile.user)
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        profile: TenantProfile = self.validated_data["tenant_profile"]
        user = profile.user
        user.set_password(self.validated_data["password"])
        user.is_active = True
        if "phone_number" in self.validated_data and profile.can_edit_phone_number:
            user.phone_number = self.validated_data["phone_number"]
        user.save(update_fields=["password", "is_active", "phone_number", "updated_at"])
        profile.mark_activated()
        profile.save(
            update_fields=[
                "otp_used_at",
                "activation_completed_at",
                "phone_edit_locked_at",
                "otp_hash",
                "otp_ciphertext",
                "updated_at",
            ]
        )
        return profile
