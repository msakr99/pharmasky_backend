"""
Serializers for the notifications app.

This module provides serializers for Notification, Topic, and TopicSubscription models.
"""

from rest_framework import serializers
from django.apps import apps
from django.utils.translation import gettext_lazy as _

from core.serializers.abstract_serializers import BaseModelSerializer
from notifications.models import Notification, Topic, TopicSubscription, FCMToken


get_model = apps.get_model


class TopicReadSerializer(BaseModelSerializer):
    """Serializer for reading Topic data."""
    
    subscribers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ["id", "name", "description", "subscribers_count"]
    
    def get_subscribers_count(self, obj):
        """Get count of active subscribers for this topic."""
        return obj.subscriptions.filter(is_active=True).count()


class TopicWriteSerializer(BaseModelSerializer):
    """Serializer for creating/updating Topic."""
    
    class Meta:
        model = Topic
        fields = ["name", "description"]
    
    def validate_name(self, value):
        """Validate that topic name is unique."""
        instance = self.instance
        queryset = Topic.objects.filter(name=value)
        
        # Exclude current instance when updating
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(_("A topic with this name already exists."))
        
        return value


class NotificationReadSerializer(BaseModelSerializer):
    """Serializer for reading Notification data."""
    
    class UserSubSerializer(BaseModelSerializer):
        """Sub-serializer for user information."""
        class Meta:
            model = get_model("accounts", "User")
            fields = ["id", "username", "name"]
    
    user = UserSubSerializer(read_only=True)
    topic = TopicReadSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "topic",
            "title",
            "message",
            "is_read",
            "extra",
            "image_url",
            "created_at",
        ]


class NotificationWriteSerializer(BaseModelSerializer):
    """Serializer for creating Notification."""
    
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_model("accounts", "User").objects.all(),
        required=False,
        allow_null=True,
        help_text=_("User to send notification to. Leave empty for topic-based notification.")
    )
    topic = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("Topic to send notification to. Leave empty for user-specific notification.")
    )
    
    class Meta:
        model = Notification
        fields = [
            "user",
            "topic",
            "title",
            "message",
            "extra",
            "image_url",
        ]
    
    def validate(self, attrs):
        """Validate that either user or topic is provided."""
        user = attrs.get("user")
        topic = attrs.get("topic")
        
        if not user and not topic:
            raise serializers.ValidationError({
                "detail": _("Either 'user' or 'topic' must be provided.")
            })
        
        if user and topic:
            raise serializers.ValidationError({
                "detail": _("Cannot specify both 'user' and 'topic'. Choose one.")
            })
        
        return super().validate(attrs)
    
    def create(self, validated_data):
        """Create notification(s) based on user or topic."""
        topic = validated_data.get("topic")
        
        if topic:
            # Create notifications for all active subscribers of the topic
            subscribers = TopicSubscription.objects.filter(
                topic=topic,
                is_active=True
            ).select_related("user")
            
            notifications = []
            for subscription in subscribers:
                notification_data = validated_data.copy()
                notification_data["user"] = subscription.user
                notifications.append(Notification(**notification_data))
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                return notifications[0] if notifications else None
            else:
                raise serializers.ValidationError({
                    "topic": _("No active subscribers found for this topic.")
                })
        else:
            # Create single notification for specific user
            return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return NotificationReadSerializer representation."""
        return NotificationReadSerializer(instance, context=self.context).data


class NotificationUpdateSerializer(BaseModelSerializer):
    """Serializer for updating Notification (mainly for marking as read)."""
    
    class Meta:
        model = Notification
        fields = ["is_read"]


class TopicSubscriptionReadSerializer(BaseModelSerializer):
    """Serializer for reading TopicSubscription data."""
    
    class UserSubSerializer(BaseModelSerializer):
        """Sub-serializer for user information."""
        class Meta:
            model = get_model("accounts", "User")
            fields = ["id", "username", "name"]
    
    user = UserSubSerializer(read_only=True)
    topic = TopicReadSerializer(read_only=True)
    
    class Meta:
        model = TopicSubscription
        fields = ["id", "user", "topic", "subscribed_at", "is_active"]


class TopicSubscriptionWriteSerializer(BaseModelSerializer):
    """Serializer for creating/updating TopicSubscription."""
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    topic = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        required=True
    )
    
    class Meta:
        model = TopicSubscription
        fields = ["user", "topic", "is_active"]
    
    def validate(self, attrs):
        """Validate unique subscription."""
        user = attrs.get("user")
        topic = attrs.get("topic")
        instance = self.instance
        
        # Check if subscription already exists
        queryset = TopicSubscription.objects.filter(user=user, topic=topic)
        
        # Exclude current instance when updating
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError({
                "detail": _("You are already subscribed to this topic.")
            })
        
        return super().validate(attrs)
    
    def to_representation(self, instance):
        """Return TopicSubscriptionReadSerializer representation."""
        return TopicSubscriptionReadSerializer(instance, context=self.context).data


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications to multiple users."""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text=_("List of user IDs to send notification to.")
    )
    title = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    extra = serializers.JSONField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_user_ids(self, value):
        """Validate that user IDs exist."""
        if not value:
            raise serializers.ValidationError(_("User IDs list cannot be empty."))
        
        User = get_model("accounts", "User")
        existing_ids = set(User.objects.filter(id__in=value).values_list("id", flat=True))
        invalid_ids = set(value) - existing_ids
        
        if invalid_ids:
            raise serializers.ValidationError(
                _("The following user IDs do not exist: {ids}").format(
                    ids=", ".join(map(str, invalid_ids))
                )
            )
        
        return value
    
    def create(self, validated_data):
        """Create bulk notifications."""
        user_ids = validated_data.pop("user_ids")
        
        notifications = [
            Notification(user_id=user_id, **validated_data)
            for user_id in user_ids
        ]
        
        created_notifications = Notification.objects.bulk_create(notifications)
        return created_notifications
    
    def to_representation(self, instance):
        """Return count of created notifications."""
        if isinstance(instance, list):
            return {
                "count": len(instance),
                "message": _("{count} notifications created successfully.").format(count=len(instance))
            }
        return NotificationReadSerializer(instance, context=self.context).data


class FCMTokenSerializer(BaseModelSerializer):
    """
    Serializer لحفظ FCM Token
    يستخدم لتسجيل التوكن الخاص بجهاز المستخدم لإرسال Push Notifications
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    fcm_token = serializers.CharField(
        max_length=500, required=True, help_text=_("FCM Token من Firebase")
    )
    device_type = serializers.ChoiceField(
        choices=FCMToken.DEVICE_TYPE_CHOICES,
        default="web",
        help_text=_("نوع الجهاز"),
    )
    device_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=_("اسم الجهاز (اختياري)"),
    )

    class Meta:
        model = FCMToken
        fields = ["id", "user", "fcm_token", "device_type", "device_name"]
        read_only_fields = ["id"]

    def validate_fcm_token(self, value):
        """التحقق من صحة FCM Token"""
        if not value or len(value) < 10:
            raise serializers.ValidationError(
                _("FCM Token غير صالح. يجب أن يكون نصًا طويلًا.")
            )
        return value

    def create(self, validated_data):
        """
        إنشاء أو تحديث FCM Token
        إذا كان التوكن موجودًا، يتم تحديثه بدلاً من إنشاء واحد جديد
        """
        fcm_token = validated_data.pop("fcm_token")
        user = validated_data.get("user")

        # البحث عن التوكن الموجود
        token_obj, created = FCMToken.objects.update_or_create(
            token=fcm_token,
            defaults={
                "user": user,
                "device_type": validated_data.get("device_type", "web"),
                "device_name": validated_data.get("device_name", ""),
                "is_active": True,
            },
        )

        return token_obj

    def to_representation(self, instance):
        """تحويل الاستجابة"""
        return {
            "id": instance.id,
            "message": _("FCM Token saved successfully"),
            "device_type": instance.device_type,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
        }

