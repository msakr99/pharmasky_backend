from numpy import isin
from rest_framework.permissions import IsAuthenticated
from accounts.choices import Role
from accounts.models import User


class BaseRoleAuthentication(IsAuthenticated):
    base_role = None

    def has_permission(self, request, view):
        authenticated = super().has_permission(request, view)
        user = request.user

        # ADMIN users should have access to everything
        if authenticated and user.role == Role.ADMIN:
            return True

        if isinstance(self.base_role, list):
            return bool(authenticated and (user.role in self.base_role or user.is_superuser))

        return bool(authenticated and (user.role == self.base_role or user.is_superuser))


class PharmacyRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.PHARMACY


class StoreRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.STORE


class ManagerRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.MANAGER


class AreaManagerRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.AREA_MANAGER


class SalesRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.SALES


class DataEntryRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.DATA_ENTRY


class DeliveryRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.DELIVERY


class AdminRoleAuthentication(BaseRoleAuthentication):
    base_role = Role.ADMIN


class StaffRoleAuthentication(BaseRoleAuthentication):
    base_role = [Role.MANAGER, Role.AREA_MANAGER, Role.SALES, Role.DATA_ENTRY, Role.DELIVERY]
