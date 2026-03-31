from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class RolePermission(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_roles)


class IsSuperAdmin(RolePermission):
    allowed_roles = (UserRole.SUPER_ADMIN,)


class IsLandlord(RolePermission):
    allowed_roles = (UserRole.LANDLORD,)


class IsCaretaker(RolePermission):
    allowed_roles = (UserRole.CARETAKER,)


class IsTenant(RolePermission):
    allowed_roles = (UserRole.TENANT,)


class IsLandlordOrCaretaker(RolePermission):
    allowed_roles = (UserRole.LANDLORD, UserRole.CARETAKER)

