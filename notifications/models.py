from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notifications",
        null=True,
        blank=True,
    )
    topic = models.ForeignKey(
        "notifications.Topic",
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notifications",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    extra = models.JSONField(blank=True, null=True)
    image_url = models.URLField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "created_at"])]

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Notification Topic"
        verbose_name_plural = "Notification Topics"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class TopicSubscription(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="topic_subscriptions",
        related_query_name="topic_subscriptions",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        related_query_name="subscriptions",
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Topic Subscription"
        verbose_name_plural = "Topic Subscriptions"
        unique_together = ("user", "topic")
        indexes = [models.Index(fields=["user", "topic"])]

    def __str__(self):
        return f"{self.user} subscribed to {self.topic.name}"


class FCMToken(models.Model):
    """
    موديل لحفظ FCM Tokens الخاصة بالمستخدمين
    يستخدم لإرسال Push Notifications عبر Firebase Cloud Messaging
    """

    DEVICE_TYPE_CHOICES = [
        ("web", "Web"),
        ("android", "Android"),
        ("ios", "iOS"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="fcm_tokens",
        related_query_name="fcm_tokens",
        help_text="المستخدم صاحب التوكن",
    )
    token = models.TextField(
        unique=True, help_text="FCM Token الفريد للجهاز"
    )
    device_type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPE_CHOICES,
        default="web",
        help_text="نوع الجهاز (web, android, ios)",
    )
    device_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="اسم الجهاز (اختياري)",
    )
    is_active = models.BooleanField(
        default=True, help_text="هل التوكن نشط؟"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(
        blank=True,
        null=True,
        help_text="آخر مرة تم استخدام التوكن لإرسال إشعار",
    )

    class Meta:
        verbose_name = "FCM Token"
        verbose_name_plural = "FCM Tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["token"]),
            models.Index(fields=["device_type"]),
        ]

    def __str__(self):
        return f"FCM Token for {self.user.username} ({self.device_type})"

    def mark_as_used(self):
        """تحديث آخر وقت استخدام للتوكن"""
        from django.utils import timezone

        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    def deactivate(self):
        """إلغاء تفعيل التوكن (في حالة فشل الإرسال)"""
        self.is_active = False
        self.save(update_fields=["is_active"])
