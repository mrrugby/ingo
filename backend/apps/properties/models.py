from django.conf import settings
from django.db import models


class Property(models.Model):
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_properties")
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["landlord", "name"], name="unique_property_per_landlord"),
        ]

    def __str__(self):
        return self.name


class CaretakerAssignment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="caretaker_assignments")
    caretaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="property_assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="caretaker_assignments_made")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["property__name", "caretaker__full_name"]
        constraints = [
            models.UniqueConstraint(fields=["property", "caretaker"], name="unique_caretaker_per_property"),
        ]

    def __str__(self):
        return f"{self.caretaker.full_name} -> {self.property.name}"

