from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import UserRole
from apps.properties.models import CaretakerAssignment, Property


User = get_user_model()


class PropertySerializer(serializers.ModelSerializer):
    caretakers = serializers.SerializerMethodField()
    tenant_count = serializers.IntegerField(read_only=True)
    pending_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = ("id", "name", "location", "description", "tenant_count", "pending_count", "caretakers")

    def get_caretakers(self, obj):
        return [
            {"id": assignment.caretaker.id, "full_name": assignment.caretaker.full_name, "email": assignment.caretaker.email}
            for assignment in obj.caretaker_assignments.select_related("caretaker").all()
        ]


class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ("id", "name", "location", "description")
        read_only_fields = ("id",)

    def create(self, validated_data):
        return Property.objects.create(landlord=self.context["request"].user, **validated_data)


class CaretakerAssignmentSerializer(serializers.Serializer):
    caretaker_id = serializers.IntegerField()

    def validate_caretaker_id(self, value):
        request = self.context["request"]
        caretaker = User.objects.filter(id=value, role=UserRole.CARETAKER, created_by=request.user).first()
        if not caretaker:
            raise serializers.ValidationError("Caretaker not found for this landlord.")
        self.context["caretaker"] = caretaker
        return value

    def create(self, validated_data):
        property_obj = self.context["property"]
        caretaker = self.context["caretaker"]
        assignment, _ = CaretakerAssignment.objects.get_or_create(
            property=property_obj,
            caretaker=caretaker,
            defaults={"assigned_by": self.context["request"].user},
        )
        return assignment

