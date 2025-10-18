from django.contrib import admin

from core.admin.abstract_admin import DefaultBaseAdminItems
from notifications.models import Notification, Topic, TopicSubscription, FCMToken
# from notifications.utils import send_user_fcm_message  # Temporarily disabled


@admin.register(Notification)
class NotificationModelAdmin(DefaultBaseAdminItems):
    @admin.action(description="Mark selected notifications as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected notifications as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    # @admin.action(description="Resend notification to users")
    # def resend_notification(self, request, queryset):
    #     for notification in queryset:
    #         if notification.user:
    #             send_user_fcm_message(notification)

    actions = [mark_as_read, mark_as_unread]  # resend_notification temporarily disabled
    list_display = ("id", "user", "topic", "title", "created_at", "is_read")
    search_fields = ("title", "message")
    list_filter = ("is_read", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user", "topic")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Topic)
class TopicModelAdmin(DefaultBaseAdminItems):
    list_display = ("id", "name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TopicSubscription)
class TopicSubscriptionModelAdmin(DefaultBaseAdminItems):
    list_display = ("id", "user", "topic")
    search_fields = ("user__username", "topic__name")
    ordering = ("user__username", "topic__name")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "topic")


@admin.register(FCMToken)
class FCMTokenModelAdmin(DefaultBaseAdminItems):
    """إدارة FCM Tokens في Django Admin"""

    @admin.action(description="Deactivate selected tokens")
    def deactivate_tokens(self, request, queryset):
        """إلغاء تفعيل التوكنات المحددة"""
        queryset.update(is_active=False)
        self.message_user(request, f"تم إلغاء تفعيل {queryset.count()} توكن")

    @admin.action(description="Activate selected tokens")
    def activate_tokens(self, request, queryset):
        """تفعيل التوكنات المحددة"""
        queryset.update(is_active=True)
        self.message_user(request, f"تم تفعيل {queryset.count()} توكن")

    actions = [deactivate_tokens, activate_tokens]
    list_display = (
        "id",
        "user",
        "device_type",
        "device_name",
        "is_active",
        "created_at",
        "last_used",
    )
    list_filter = ("device_type", "is_active", "created_at")
    search_fields = ("user__username", "device_name", "token")
    readonly_fields = ("created_at", "updated_at", "last_used")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
