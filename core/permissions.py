"""
Base permission classes for PharmaSky application.

This module provides reusable permission classes that can be extended
throughout the application for consistent authorization.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from django.contrib.auth.models import AnonymousUser
from accounts.choices import Role
from typing import Any


class IsAuthenticatedUser(BasePermission):
    """
    Permission class that allows access only to authenticated users.
    Enhanced version of DRF's IsAuthenticated with better error messages.
    """
    
    message = "Authentication credentials were not provided or are invalid."
    
    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)


class RoleBasedPermission(BasePermission):
    """
    Base permission class for role-based access control.
    """
    
    allowed_roles = []  # Override in subclasses
    message = "You do not have permission to perform this action."
    
    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if user has required role.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            bool: True if user has required role, False otherwise
        """
        if not request.user or isinstance(request.user, AnonymousUser):
            return False
            
        if not request.user.is_authenticated:
            return False
            
        # Superusers always have access
        if request.user.is_superuser:
            return True
            
        # Check if user role is in allowed roles
        return request.user.role in self.allowed_roles


class PharmacyPermission(RoleBasedPermission):
    """Permission class for pharmacy users."""
    allowed_roles = [Role.PHARMACY]
    message = "Only pharmacy users can access this resource."


class SalesPermission(RoleBasedPermission):
    """Permission class for sales users."""
    allowed_roles = [Role.SALES]
    message = "Only sales users can access this resource."


class ManagerPermission(RoleBasedPermission):
    """Permission class for manager users."""
    allowed_roles = [Role.MANAGER, Role.AREA_MANAGER]
    message = "Only managers can access this resource."


class StorePermission(RoleBasedPermission):
    """Permission class for store users."""
    allowed_roles = [Role.STORE]
    message = "Only store users can access this resource."


class DataEntryPermission(RoleBasedPermission):
    """Permission class for data entry users."""
    allowed_roles = [Role.DATA_ENTRY]
    message = "Only data entry users can access this resource."


class DeliveryPermission(RoleBasedPermission):
    """Permission class for delivery users."""
    allowed_roles = [Role.DELIVERY]
    message = "Only delivery users can access this resource."


class StaffPermission(RoleBasedPermission):
    """Permission class for staff users (managers, sales, data entry)."""
    allowed_roles = [
        Role.MANAGER, 
        Role.AREA_MANAGER, 
        Role.SALES, 
        Role.DATA_ENTRY,
        Role.STORE
    ]
    message = "Only staff members can access this resource."


class IsOwnerOrStaff(BasePermission):
    """
    Permission class that allows access to owners of objects or staff members.
    """
    
    message = "You can only access your own resources or you must be a staff member."
    
    def has_permission(self, request: Request, view: Any) -> bool:
        """Check basic authentication."""
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """
        Check if user owns the object or is staff.
        
        Args:
            request: The request object
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            bool: True if user owns object or is staff, False otherwise
        """
        if request.user.is_superuser:
            return True
            
        # Check if user is staff
        if request.user.role in [Role.MANAGER, Role.AREA_MANAGER, Role.SALES, Role.DATA_ENTRY]:
            return True
            
        # Check ownership
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'pharmacy'):
            return obj.pharmacy == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        return False


class ReadOnlyPermission(BasePermission):
    """
    Permission class that allows read-only access to authenticated users.
    """
    
    message = "This resource is read-only."
    
    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Allow read operations for authenticated users.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            bool: True for safe methods, False for unsafe methods
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        return request.method in ['GET', 'HEAD', 'OPTIONS']

