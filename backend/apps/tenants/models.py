from __future__ import annotations

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from apps.common.security import decrypt_value, encrypt_value
from apps.properties.models import Property


class TenantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_profile")
    assigned_property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="tenant_profiles")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_tenant_profiles")
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_ciphertext = models.TextField(blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_used_at = models.DateTimeField(null=True, blank=True)
    activation_completed_at = models.DateTimeField(null=True, blank=True)
    phone_edit_locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__full_name", "id"]

    def issue_otp(self, raw_otp: str) -> None:
        self.otp_hash = make_password(raw_otp)
        self.otp_ciphertext = encrypt_value(raw_otp)
        self.otp_created_at = timezone.now()
        self.otp_used_at = None

    def verify_otp(self, raw_otp: str) -> bool:
        return bool(self.otp_hash) and check_password(raw_otp, self.otp_hash) and self.otp_used_at is None

    def reveal_otp(self) -> str | None:
        if not self.otp_ciphertext or self.otp_used_at:
            return None
        return decrypt_value(self.otp_ciphertext)

    def mark_activated(self) -> None:
        now = timezone.now()
        self.otp_used_at = now
        self.activation_completed_at = now
        self.phone_edit_locked_at = now
        self.otp_hash = ""
        self.otp_ciphertext = ""

    @property
    def can_edit_phone_number(self) -> bool:
        return self.phone_edit_locked_at is None

    def __str__(self):
        return f"{self.user.full_name} @ {self.assigned_property.name}"
