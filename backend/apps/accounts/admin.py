from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("full_name",)
    list_display = ("full_name", "email", "phone_number", "role", "created_by", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("full_name", "email", "phone_number")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "email", "phone_number", "role", "created_by")}),
        ("Access", {"fields": ("password", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("full_name", "email", "role", "password1", "password2", "is_active", "is_staff"),
            },
        ),
    )
    readonly_fields = ("date_joined", "updated_at", "last_login")
