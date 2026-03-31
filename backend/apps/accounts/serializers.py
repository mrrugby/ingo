from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import UserRole
from apps.common.phone import normalize_phone_number


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "phone_number", "role", "is_active", "created_by", "created_by_name")
        read_only_fields = ("id", "is_active", "created_by", "created_by_name")


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    default_error_messages = {
        "invalid_credentials": "Invalid credentials.",
        "inactive_user": "This account is not active.",
        "wrong_identifier": "Use email for staff roles and phone number for tenant login.",
    }

    def validate(self, attrs):
        identifier = attrs["identifier"].strip()
        password = attrs["password"]

        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user and user.role == UserRole.TENANT:
                self.fail("wrong_identifier")
        else:
            normalized_phone = normalize_phone_number(identifier)
            user = User.objects.filter(phone_number=normalized_phone).first()
            if user and user.role != UserRole.TENANT:
                self.fail("wrong_identifier")

        if not user or not user.check_password(password):
            self.fail("invalid_credentials")

        if not user.is_active:
            self.fail("inactive_user")

        attrs["user"] = user
        return attrs


class ManagedUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[UserRole.LANDLORD, UserRole.CARETAKER])

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "password", "role")
        read_only_fields = ("id",)

    def validate(self, attrs):
        request = self.context["request"]
        creator = request.user
        requested_role = attrs["role"]

        if creator.role == UserRole.SUPER_ADMIN and requested_role != UserRole.LANDLORD:
            raise serializers.ValidationError({"role": "Super admins can only create landlords."})

        if creator.role == UserRole.LANDLORD and requested_role != UserRole.CARETAKER:
            raise serializers.ValidationError({"role": "Landlords can only create caretakers."})

        if creator.role not in {UserRole.SUPER_ADMIN, UserRole.LANDLORD}:
            raise serializers.ValidationError("You do not have permission to create users.")

        attrs["email"] = attrs["email"].lower()
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        creator = self.context["request"].user
        return User.objects.create_user(
            password=password,
            created_by=creator,
            is_active=True,
            **validated_data,
        )
