from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from notifications.models import Notification
from notifications.utils import send_user_fcm_message


@receiver(post_save, sender=Notification)
def on_notification_created(sender, instance, created, **kwargs):
    if created:
        if instance.user:
            send_user_fcm_message(instance)
