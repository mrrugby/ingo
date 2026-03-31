from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    LANDLORD = "landlord", "Landlord"
    CARETAKER = "caretaker", "Caretaker"
    TENANT = "tenant", "Tenant"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str | None, password: str | None, **extra_fields):
        role = extra_fields.get("role")
        if role != UserRole.TENANT and not email:
            raise ValueError("Email is required for non-tenant users.")

        if email:
            email = self.normalize_email(email).lower()

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email: str | None = None, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("role", UserRole.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    created_by = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="created_users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["full_name", "id"]

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email).lower()

        if self.role == UserRole.TENANT and self.email:
            raise ValidationError("Tenant accounts cannot authenticate with email.")

        if self.role != UserRole.TENANT and not self.email:
            raise ValidationError("Email is required for this role.")

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_role_display()})"
