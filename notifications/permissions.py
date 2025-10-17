"""
Permissions for the notifications app.

This module provides custom permission classes for notification operations.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated
from accounts.choices import Role


class IsNotificationOwner(BasePermission):
    """
    Permission class to check if the user is the owner of the notification.
    
    Used for retrieving, updating, and deleting notifications.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if the user owns the notification."""
        return obj.user == request.user


class IsSubscriptionOwner(BasePermission):
    """
    Permission class to check if the user is the owner of the subscription.
    
    Used for updating and deleting topic subscriptions.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if the user owns the subscription."""
        return obj.user == request.user


class CanCreateNotification(IsAuthenticated):
    """
    Permission class for creating notifications.
    
    Only Admin and Manager users can create notifications.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to create notifications."""
        authenticated = super().has_permission(request, view)
        user = request.user
        
        return bool(
            authenticated and 
            user.role in [Role.ADMIN, Role.MANAGER]
        )


class CanManageTopics(IsAuthenticated):
    """
    Permission class for managing topics (create, update, delete).
    
    Only Admin and Manager users can manage topics.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to manage topics."""
        authenticated = super().has_permission(request, view)
        user = request.user
        
        return bool(
            authenticated and 
            user.role in [Role.ADMIN, Role.MANAGER]
        )


class CanViewAllNotifications(IsAuthenticated):
    """
    Permission class for viewing all notifications (Admin panel).
    
    Only Admin and Manager users can view all notifications.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to view all notifications."""
        authenticated = super().has_permission(request, view)
        user = request.user
        
        return bool(
            authenticated and 
            user.role in [Role.ADMIN, Role.MANAGER]
        )

