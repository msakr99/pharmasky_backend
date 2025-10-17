"""
URL configuration for notifications app.
"""

from django.urls import path
from notifications import views


app_name = "notifications"

urlpatterns = [
    # Notification URLs
    path(
        "notifications/",
        views.NotificationListAPIView.as_view(),
        name="notifications-list",
    ),
    path(
        "notifications/unread/",
        views.UnreadNotificationListAPIView.as_view(),
        name="notifications-unread-list",
    ),
    path(
        "notifications/stats/",
        views.NotificationStatsAPIView.as_view(),
        name="notifications-stats",
    ),
    path(
        "notifications/mark-all-read/",
        views.MarkAllNotificationsAsReadAPIView.as_view(),
        name="notifications-mark-all-read",
    ),
    path(
        "notifications/create/",
        views.NotificationCreateAPIView.as_view(),
        name="notifications-create",
    ),
    path(
        "notifications/bulk-create/",
        views.BulkNotificationCreateAPIView.as_view(),
        name="notifications-bulk-create",
    ),
    path(
        "notifications/<int:pk>/",
        views.NotificationRetrieveAPIView.as_view(),
        name="notifications-detail",
    ),
    path(
        "notifications/<int:pk>/update/",
        views.NotificationUpdateAPIView.as_view(),
        name="notifications-update",
    ),
    path(
        "notifications/<int:pk>/delete/",
        views.NotificationDeleteAPIView.as_view(),
        name="notifications-delete",
    ),
    
    # Topic URLs
    path(
        "topics/",
        views.TopicListAPIView.as_view(),
        name="topics-list",
    ),
    path(
        "topics/my-topics/",
        views.MyTopicsAPIView.as_view(),
        name="my-topics",
    ),
    path(
        "topics/create/",
        views.TopicCreateAPIView.as_view(),
        name="topics-create",
    ),
    path(
        "topics/<int:pk>/",
        views.TopicRetrieveAPIView.as_view(),
        name="topics-detail",
    ),
    path(
        "topics/<int:pk>/update/",
        views.TopicUpdateAPIView.as_view(),
        name="topics-update",
    ),
    path(
        "topics/<int:pk>/delete/",
        views.TopicDeleteAPIView.as_view(),
        name="topics-delete",
    ),
    
    # Topic Subscription URLs
    path(
        "subscriptions/",
        views.TopicSubscriptionListAPIView.as_view(),
        name="subscriptions-list",
    ),
    path(
        "subscriptions/create/",
        views.TopicSubscriptionCreateAPIView.as_view(),
        name="subscriptions-create",
    ),
    path(
        "subscriptions/<int:pk>/update/",
        views.TopicSubscriptionUpdateAPIView.as_view(),
        name="subscriptions-update",
    ),
    path(
        "subscriptions/<int:pk>/delete/",
        views.TopicSubscriptionDeleteAPIView.as_view(),
        name="subscriptions-delete",
    ),
]

