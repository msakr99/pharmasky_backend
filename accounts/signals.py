"""
Signals for the accounts app.

Automatically send notifications for account-related events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Pharmacy
from accounts.choices import Role
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


def get_admin_users():
    """Get all admin and manager users."""
    return User.objects.filter(role__in=[Role.ADMIN, Role.MANAGER], is_active=True)


@receiver(post_save, sender=User)
def on_pharmacy_registered(sender, instance, created, **kwargs):
    """
    إرسال إشعار للـ Admin عند تسجيل صيدلية جديدة.
    """
    if created and instance.role == Role.PHARMACY:
        try:
            # إرسال إشعار لجميع الـ Admins
            admins = get_admin_users()
            
            notifications = []
            for admin in admins:
                notifications.append(
                    Notification(
                        user=admin,
                        title="🏪 تسجيل صيدلية جديدة",
                        message=f"تم تسجيل صيدلية جديدة: {instance.name} ({instance.username})",
                        extra={
                            "type": "new_pharmacy_registration",
                            "pharmacy_id": instance.pk,
                            "pharmacy_name": instance.name,
                            "pharmacy_username": instance.username,
                            "area": instance.area.name if instance.area else None,
                        },
                        image_url=""
                    )
                )
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                logger.info(f"Pharmacy registration notification sent to {len(notifications)} admins for pharmacy #{instance.pk}")
                
        except Exception as e:
            logger.error(f"Failed to send pharmacy registration notification: {str(e)}")
