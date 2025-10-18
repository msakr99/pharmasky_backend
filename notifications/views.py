"""
Views for the notifications app.

This module provides API views for managing notifications, topics, and subscriptions.
"""

from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from notifications.models import Notification, Topic, TopicSubscription, FCMToken
from notifications.serializers import (
    NotificationReadSerializer,
    NotificationWriteSerializer,
    NotificationUpdateSerializer,
    TopicReadSerializer,
    TopicWriteSerializer,
    TopicSubscriptionReadSerializer,
    TopicSubscriptionWriteSerializer,
    BulkNotificationSerializer,
    FCMTokenSerializer,
)
from core.responses import APIResponse
from core.views.abstract_paginations import CustomPageNumberPagination
from accounts.permissions import AdminRoleAuthentication, ManagerRoleAuthentication


# ===========================
# Notification Views
# ===========================

class NotificationListAPIView(ListAPIView):
    """
    List all notifications for the authenticated user.
    
    Filters:
    - is_read: Filter by read status (true/false)
    - topic: Filter by topic ID
    
    Search:
    - Search in title and message
    
    Ordering:
    - created_at (default: -created_at)
    - is_read
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationReadSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_read", "topic"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """Return notifications for the authenticated user only."""
        user = self.request.user
        return Notification.objects.filter(user=user).select_related("user", "topic")


class UnreadNotificationListAPIView(ListAPIView):
    """List only unread notifications for the authenticated user."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationReadSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """Return only unread notifications for the authenticated user."""
        user = self.request.user
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).select_related("user", "topic")


class NotificationRetrieveAPIView(RetrieveAPIView):
    """Retrieve a single notification by ID."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationReadSerializer
    
    def get_queryset(self):
        """Ensure users can only retrieve their own notifications."""
        return Notification.objects.filter(user=self.request.user).select_related("user", "topic")


class NotificationUpdateAPIView(UpdateAPIView):
    """
    Update a notification (mainly for marking as read/unread).
    
    Only the owner of the notification can update it.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationUpdateSerializer
    
    def get_queryset(self):
        """Ensure users can only update their own notifications."""
        return Notification.objects.filter(user=self.request.user)


class NotificationCreateAPIView(CreateAPIView):
    """
    Create a new notification.
    
    Admin/Manager only. Can send to specific user or all subscribers of a topic.
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = NotificationWriteSerializer
    queryset = Notification.objects.none()


class BulkNotificationCreateAPIView(CreateAPIView):
    """
    Send bulk notifications to multiple users.
    
    Admin/Manager only.
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = BulkNotificationSerializer
    queryset = Notification.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create bulk notifications."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notifications = serializer.save()
        
        return APIResponse.created(
            data=serializer.to_representation(notifications),
            message=_("Bulk notifications sent successfully.")
        )


class MarkAllNotificationsAsReadAPIView(APIView):
    """Mark all notifications as read for the authenticated user."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Mark all user notifications as read."""
        user = request.user
        updated_count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)
        
        return APIResponse.success(
            data={"updated_count": updated_count},
            message=_("{count} notifications marked as read.").format(count=updated_count)
        )


class NotificationDeleteAPIView(DestroyAPIView):
    """
    Delete a notification.
    
    Only the owner can delete their notification.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ensure users can only delete their own notifications."""
        return Notification.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete notification and return success response."""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message=_("Notification deleted successfully.")
        )


class NotificationStatsAPIView(APIView):
    """Get notification statistics for the authenticated user."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Return notification statistics."""
        user = request.user
        
        total_count = Notification.objects.filter(user=user).count()
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        read_count = total_count - unread_count
        
        stats = {
            "total": total_count,
            "unread": unread_count,
            "read": read_count,
        }
        
        return APIResponse.success(
            data=stats,
            message=_("Notification statistics retrieved successfully.")
        )


# ===========================
# Topic Views
# ===========================

class TopicListAPIView(ListAPIView):
    """
    List all available topics.
    
    Available for all authenticated users.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TopicReadSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]
    
    def get_queryset(self):
        """Return all topics."""
        return Topic.objects.all()


class TopicRetrieveAPIView(RetrieveAPIView):
    """Retrieve a single topic by ID."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = TopicReadSerializer
    queryset = Topic.objects.all()


class TopicCreateAPIView(CreateAPIView):
    """
    Create a new topic.
    
    Admin/Manager only.
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = TopicWriteSerializer
    queryset = Topic.objects.none()


class TopicUpdateAPIView(UpdateAPIView):
    """
    Update a topic.
    
    Admin/Manager only.
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    serializer_class = TopicWriteSerializer
    queryset = Topic.objects.all()


class TopicDeleteAPIView(DestroyAPIView):
    """
    Delete a topic.
    
    Admin/Manager only.
    """
    
    permission_classes = [AdminRoleAuthentication | ManagerRoleAuthentication]
    queryset = Topic.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        """Delete topic and return success response."""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message=_("Topic deleted successfully.")
        )


# ===========================
# Topic Subscription Views
# ===========================

class TopicSubscriptionListAPIView(ListAPIView):
    """
    List all topic subscriptions for the authenticated user.
    
    Shows which topics the user is subscribed to.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSubscriptionReadSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["subscribed_at"]
    ordering = ["-subscribed_at"]
    
    def get_queryset(self):
        """Return subscriptions for the authenticated user only."""
        user = self.request.user
        return TopicSubscription.objects.filter(user=user).select_related("user", "topic")


class TopicSubscriptionCreateAPIView(CreateAPIView):
    """
    Subscribe to a topic.
    
    Users can subscribe themselves to topics.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSubscriptionWriteSerializer
    queryset = TopicSubscription.objects.none()


class TopicSubscriptionUpdateAPIView(UpdateAPIView):
    """
    Update subscription status (activate/deactivate).
    
    Users can only update their own subscriptions.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSubscriptionWriteSerializer
    
    def get_queryset(self):
        """Ensure users can only update their own subscriptions."""
        return TopicSubscription.objects.filter(user=self.request.user)


class TopicSubscriptionDeleteAPIView(DestroyAPIView):
    """
    Unsubscribe from a topic.
    
    Users can only delete their own subscriptions.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ensure users can only delete their own subscriptions."""
        return TopicSubscription.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete subscription and return success response."""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message=_("Successfully unsubscribed from topic.")
        )


class MyTopicsAPIView(APIView):
    """
    Get all topics with subscription status for the authenticated user.
    
    Shows which topics the user is subscribed to and which are available.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Return all topics with user's subscription status."""
        user = request.user
        
        # Get all user subscriptions
        user_subscriptions = TopicSubscription.objects.filter(
            user=user
        ).values_list("topic_id", "is_active")
        
        subscription_map = {topic_id: is_active for topic_id, is_active in user_subscriptions}
        
        # Get all topics
        topics = Topic.objects.all()
        
        topics_data = []
        for topic in topics:
            topic_data = TopicReadSerializer(topic).data
            topic_data["is_subscribed"] = topic.id in subscription_map
            topic_data["subscription_active"] = subscription_map.get(topic.id, False)
            topics_data.append(topic_data)
        
        return APIResponse.success(
            data=topics_data,
            message=_("Topics with subscription status retrieved successfully.")
        )


# ===========================
# FCM Token Views
# ===========================

class SaveFCMTokenAPIView(CreateAPIView):
    """
    حفظ FCM Token للمستخدم المسجل
    
    يستخدم لتسجيل FCM Token من Firebase Cloud Messaging
    لإرسال Push Notifications للمستخدم
    
    **Body Parameters:**
    - fcm_token (string, required): FCM Token من Firebase
    - device_type (string, optional): نوع الجهاز (web, android, ios)
    - device_name (string, optional): اسم الجهاز
    
    **Example Request:**
    ```json
    {
        "fcm_token": "eLxBu5Z8QoWx...",
        "device_type": "web",
        "device_name": "Chrome on Windows"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "id": 1,
            "message": "FCM Token saved successfully",
            "device_type": "web",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    ```
    """
    
    serializer_class = FCMTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """حفظ FCM Token وإرجاع استجابة منسقة"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return APIResponse.success(
            data=serializer.to_representation(instance),
            message=_("FCM Token saved successfully"),
            status_code=status.HTTP_201_CREATED,
        )


class ListUserFCMTokensAPIView(ListAPIView):
    """
    عرض جميع FCM Tokens الخاصة بالمستخدم الحالي
    
    يعرض جميع الأجهزة المسجلة للمستخدم
    """
    
    serializer_class = FCMTokenSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """الحصول على tokens الخاصة بالمستخدم الحالي فقط"""
        return FCMToken.objects.filter(user=self.request.user, is_active=True)
    
    def list(self, request, *args, **kwargs):
        """إرجاع قائمة الـ tokens بشكل منسق"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=_("FCM Tokens retrieved successfully"),
        )


class DeleteFCMTokenAPIView(DestroyAPIView):
    """
    حذف FCM Token (إلغاء تسجيل جهاز)
    
    يستخدم عندما يريد المستخدم إيقاف الإشعارات على جهاز معين
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """الحصول على tokens الخاصة بالمستخدم الحالي فقط"""
        return FCMToken.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """حذف Token وإرجاع استجابة منسقة"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.success(
            message=_("FCM Token deleted successfully")
        )

