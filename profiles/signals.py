"""
Signals for the profiles app.

Automatically send notifications for complaint events.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from profiles.models import Complaint
from accounts.choices import Role
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


def get_admin_users():
    """Get all admin and manager users."""
    from accounts.models import User
    return User.objects.filter(role__in=[Role.ADMIN, Role.MANAGER], is_active=True)


@receiver(post_save, sender=Complaint)
def on_complaint_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للـ Admin عند إنشاء شكوى جديدة.
    """
    if created:
        try:
            # إرسال إشعار لجميع الـ Admins
            admins = get_admin_users()
            
            notifications = []
            for admin in admins:
                notifications.append(
                    Notification(
                        user=admin,
                        title="📢 شكوى جديدة",
                        message=f"شكوى جديدة من {instance.user.name}: {instance.subject}",
                        extra={
                            "type": "new_complaint",
                            "complaint_id": instance.pk,
                            "user_id": instance.user.pk,
                            "user_name": instance.user.name,
                            "subject": instance.subject,
                            "body": instance.body,
                        },
                        image_url=""
                    )
                )
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                logger.info(f"Complaint notification sent to {len(notifications)} admins for complaint #{instance.pk}")
                
        except Exception as e:
            logger.error(f"Failed to send complaint notification: {str(e)}")


@receiver(pre_save, sender=Complaint)
def on_complaint_resolved(sender, instance, **kwargs):
    """
    إرسال إشعار للمستخدم عند حل الشكوى.
    """
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            
            # إذا تم حل الشكوى
            if not old_instance.mark_as_solved and instance.mark_as_solved:
                # إشعار للمستخدم صاحب الشكوى
                Notification.objects.create(
                    user=instance.user,
                    title="✅ تم حل شكواك",
                    message=f"تم حل شكواك: {instance.subject}. شكراً لتواصلك معنا.",
                    extra={
                        "type": "complaint_resolved",
                        "complaint_id": instance.pk,
                        "subject": instance.subject,
                    },
                    image_url=""
                )
                logger.info(f"Complaint resolved notification sent to user {instance.user.id}")
                
        except Complaint.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to send complaint resolved notification: {str(e)}")

