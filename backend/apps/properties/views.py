from __future__ import annotations

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.properties.models import Property
from apps.properties.serializers import CaretakerAssignmentSerializer, PropertyCreateSerializer, PropertySerializer


class PropertyListCreateView(APIView):
    def get_queryset(self, user):
        queryset = Property.objects.all().annotate(
            tenant_count=Count("tenant_profiles", distinct=True),
            pending_count=Count("tenant_profiles", filter=Q(tenant_profiles__otp_used_at__isnull=True), distinct=True),
        ).prefetch_related("caretaker_assignments__caretaker")

        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        if user.role == UserRole.LANDLORD:
            return queryset.filter(landlord=user)
        if user.role == UserRole.CARETAKER:
            return queryset.filter(caretaker_assignments__caretaker=user).distinct()
        return queryset.none()

    def get(self, request):
        queryset = self.get_queryset(request.user)
        return Response(PropertySerializer(queryset, many=True).data)

    def post(self, request):
        if request.user.role != UserRole.LANDLORD:
            return Response({"detail": "Only landlords can create properties."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PropertyCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        property_obj = serializer.save()
        property_obj = self.get_queryset(request.user).get(id=property_obj.id)
        return Response(PropertySerializer(property_obj).data, status=status.HTTP_201_CREATED)


class AssignCaretakerView(APIView):
    def post(self, request, property_id):
        if request.user.role != UserRole.LANDLORD:
            return Response({"detail": "Only landlords can assign caretakers."}, status=status.HTTP_403_FORBIDDEN)

        property_obj = get_object_or_404(Property, id=property_id, landlord=request.user)
        serializer = CaretakerAssignmentSerializer(
            data=request.data,
            context={"request": request, "property": property_obj},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        property_obj = Property.objects.annotate(
            tenant_count=Count("tenant_profiles", distinct=True),
            pending_count=Count("tenant_profiles", filter=Q(tenant_profiles__otp_used_at__isnull=True), distinct=True),
        ).prefetch_related("caretaker_assignments__caretaker").get(id=property_obj.id)
        return Response(PropertySerializer(property_obj).data)
