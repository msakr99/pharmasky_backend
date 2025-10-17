"""
Filters for the notifications app.

This module provides filter classes for Notification, Topic, and TopicSubscription models.
"""

from django_filters import rest_framework as filters
from notifications.models import Notification, Topic, TopicSubscription
from core.filters.abstract_filters import ListIDFilter, ListBooleanFilter


class NotificationFilter(filters.FilterSet):
    """
    Filter class for Notification model.
    
    Filters:
    - id: Filter by notification ID (supports multiple IDs)
    - user: Filter by user ID (supports multiple IDs)
    - topic: Filter by topic ID (supports multiple IDs)
    - is_read: Filter by read status
    - created_at__gte: Filter notifications created after a date
    - created_at__lte: Filter notifications created before a date
    """
    
    id = ListIDFilter(field_name="pk")
    user = ListIDFilter(field_name="user__pk")
    topic = ListIDFilter(field_name="topic__pk")
    is_read = ListBooleanFilter(field_name="is_read")
    created_at__gte = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at__lte = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    
    class Meta:
        model = Notification
        fields = ["id", "user", "topic", "is_read", "created_at__gte", "created_at__lte"]


class TopicFilter(filters.FilterSet):
    """
    Filter class for Topic model.
    
    Filters:
    - id: Filter by topic ID (supports multiple IDs)
    - name: Filter by exact topic name
    - name__icontains: Filter by topic name (case-insensitive)
    """
    
    id = ListIDFilter(field_name="pk")
    name = filters.CharFilter(field_name="name", lookup_expr="exact")
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    
    class Meta:
        model = Topic
        fields = ["id", "name", "name__icontains"]


class TopicSubscriptionFilter(filters.FilterSet):
    """
    Filter class for TopicSubscription model.
    
    Filters:
    - id: Filter by subscription ID (supports multiple IDs)
    - user: Filter by user ID (supports multiple IDs)
    - topic: Filter by topic ID (supports multiple IDs)
    - is_active: Filter by subscription active status
    - subscribed_at__gte: Filter subscriptions created after a date
    - subscribed_at__lte: Filter subscriptions created before a date
    """
    
    id = ListIDFilter(field_name="pk")
    user = ListIDFilter(field_name="user__pk")
    topic = ListIDFilter(field_name="topic__pk")
    is_active = ListBooleanFilter(field_name="is_active")
    subscribed_at__gte = filters.DateTimeFilter(field_name="subscribed_at", lookup_expr="gte")
    subscribed_at__lte = filters.DateTimeFilter(field_name="subscribed_at", lookup_expr="lte")
    
    class Meta:
        model = TopicSubscription
        fields = ["id", "user", "topic", "is_active", "subscribed_at__gte", "subscribed_at__lte"]

