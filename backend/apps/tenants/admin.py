from django.contrib import admin

from .models import TenantProfile


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "assigned_property", "created_by", "otp_created_at", "otp_used_at", "activation_completed_at")
    search_fields = ("user__full_name", "user__phone_number", "assigned_property__name")
