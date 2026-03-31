from django.contrib import admin

from .models import CaretakerAssignment, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "landlord", "location", "created_at")
    search_fields = ("name", "location", "landlord__full_name")


@admin.register(CaretakerAssignment)
class CaretakerAssignmentAdmin(admin.ModelAdmin):
    list_display = ("property", "caretaker", "assigned_by", "created_at")
    search_fields = ("property__name", "caretaker__full_name", "assigned_by__full_name")

