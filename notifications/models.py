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
