"""
Celery tasks for the notifications app.

This module provides asynchronous tasks for sending notifications.
"""

from celery import shared_task
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

get_model = apps.get_model


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_to_user(self, user_id, title, message, extra=None, image_url=""):
    """
    Task to send a notification to a specific user.
    
    Args:
        user_id: ID of the user to send notification to
        title: Notification title
        message: Notification message
        extra: Optional JSON data
        image_url: Optional image URL
    
    Returns:
        dict: Result of notification creation
    """
    try:
        User = get_model("accounts", "User")
        Notification = get_model("notifications", "Notification")
        
        user = User.objects.get(id=user_id)
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            extra=extra,
            image_url=image_url or ""
        )
        
        logger.info(f"Notification created successfully for user {user_id}: {notification.id}")
        
        return {
            "success": True,
            "notification_id": notification.id,
            "user_id": user_id
        }
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {
            "success": False,
            "error": "User not found",
            "user_id": user_id
        }
    except Exception as exc:
        logger.error(f"Error creating notification for user {user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_to_topic(self, topic_id, title, message, extra=None, image_url=""):
    """
    Task to send notifications to all subscribers of a topic.
    
    Args:
        topic_id: ID of the topic
        title: Notification title
        message: Notification message
        extra: Optional JSON data
        image_url: Optional image URL
    
    Returns:
        dict: Result of notifications creation
    """
    try:
        Topic = get_model("notifications", "Topic")
        TopicSubscription = get_model("notifications", "TopicSubscription")
        Notification = get_model("notifications", "Notification")
        
        topic = Topic.objects.get(id=topic_id)
        
        # Get all active subscribers
        subscribers = TopicSubscription.objects.filter(
            topic=topic,
            is_active=True
        ).select_related("user")
        
        if not subscribers.exists():
            logger.warning(f"No active subscribers found for topic {topic_id}")
            return {
                "success": True,
                "message": "No active subscribers",
                "count": 0
            }
        
        # Create notifications for all subscribers
        notifications = []
        for subscription in subscribers:
            notifications.append(
                Notification(
                    user=subscription.user,
                    topic=topic,
                    title=title,
                    message=message,
                    extra=extra,
                    image_url=image_url or ""
                )
            )
        
        created_notifications = Notification.objects.bulk_create(notifications)
        
        logger.info(f"Created {len(created_notifications)} notifications for topic {topic_id}")
        
        return {
            "success": True,
            "count": len(created_notifications),
            "topic_id": topic_id
        }
        
    except Topic.DoesNotExist:
        logger.error(f"Topic with ID {topic_id} not found")
        return {
            "success": False,
            "error": "Topic not found",
            "topic_id": topic_id
        }
    except Exception as exc:
        logger.error(f"Error creating notifications for topic {topic_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_bulk_notifications(self, user_ids, title, message, extra=None, image_url=""):
    """
    Task to send notifications to multiple users.
    
    Args:
        user_ids: List of user IDs
        title: Notification title
        message: Notification message
        extra: Optional JSON data
        image_url: Optional image URL
    
    Returns:
        dict: Result of notifications creation
    """
    try:
        User = get_model("accounts", "User")
        Notification = get_model("notifications", "Notification")
        
        # Validate that all users exist
        users = User.objects.filter(id__in=user_ids)
        existing_user_ids = set(users.values_list("id", flat=True))
        invalid_ids = set(user_ids) - existing_user_ids
        
        if invalid_ids:
            logger.warning(f"Invalid user IDs: {invalid_ids}")
        
        # Create notifications for valid users
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    message=message,
                    extra=extra,
                    image_url=image_url or ""
                )
            )
        
        created_notifications = Notification.objects.bulk_create(notifications)
        
        logger.info(f"Created {len(created_notifications)} bulk notifications")
        
        return {
            "success": True,
            "count": len(created_notifications),
            "invalid_user_ids": list(invalid_ids)
        }
        
    except Exception as exc:
        logger.error(f"Error creating bulk notifications: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task
def delete_old_read_notifications(days=30):
    """
    Task to delete old read notifications.
    
    Args:
        days: Number of days after which read notifications should be deleted
    
    Returns:
        dict: Number of deleted notifications
    """
    try:
        Notification = get_model("notifications", "Notification")
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        deleted_count, _ = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Deleted {deleted_count} old read notifications")
        
        return {
            "success": True,
            "deleted_count": deleted_count
        }
        
    except Exception as exc:
        logger.error(f"Error deleting old notifications: {str(exc)}")
        return {
            "success": False,
            "error": str(exc)
        }


@shared_task
def send_scheduled_notification(notification_id):
    """
    Task to send a scheduled notification.
    
    This is useful for notifications that need to be sent at a specific time.
    
    Args:
        notification_id: ID of the notification to mark as sent
    
    Returns:
        dict: Result of notification sending
    """
    try:
        Notification = get_model("notifications", "Notification")
        
        notification = Notification.objects.get(id=notification_id)
        
        # Here you would typically send the notification via push, email, SMS, etc.
        # For now, we just log it
        logger.info(f"Scheduled notification sent: {notification.id} - {notification.title}")
        
        return {
            "success": True,
            "notification_id": notification_id
        }
        
    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} not found")
        return {
            "success": False,
            "error": "Notification not found",
            "notification_id": notification_id
        }
    except Exception as exc:
        logger.error(f"Error sending scheduled notification {notification_id}: {str(exc)}")
        return {
            "success": False,
            "error": str(exc),
            "notification_id": notification_id
        }


@shared_task
def send_shift_notification(shift_id, shift_type='start', custom_message=''):
    """
    إرسال إشعارات لجميع الصيدليات عند بدء أو إغلاق الوردية.
    
    Args:
        shift_id: ID الوردية
        shift_type: نوع الإشعار ('start' أو 'close')
        custom_message: رسالة مخصصة (اختياري)
    
    Returns:
        dict: نتيجة الإرسال
    """
    try:
        User = get_model("accounts", "User")
        Notification = get_model("notifications", "Notification")
        WorkShift = get_model("core", "WorkShift")
        
        shift = WorkShift.objects.get(id=shift_id)
        
        # جلب جميع الصيدليات النشطة
        pharmacies = User.objects.filter(
            role='PHARMACY',
            is_active=True
        )
        
        if not pharmacies.exists():
            logger.warning("No active pharmacies found to send shift notification")
            return {
                "success": True,
                "message": "No active pharmacies",
                "count": 0
            }
        
        # تحديد العنوان والرسالة حسب النوع
        if shift_type == 'start':
            title = "🟢 النظام متاح الآن"
            if custom_message:
                message = custom_message
            else:
                message = (
                    f"مرحباً! بدأت الوردية الآن ({shift.start_time.strftime('%I:%M %p')}). "
                    f"يمكنك تقديم الطلبات والاستفسارات. نحن في خدمتك!"
                )
            notification_type = "shift_started"
        else:  # close
            title = "🔴 تم إغلاق النظام"
            if custom_message:
                message = custom_message
            else:
                duration = shift.get_duration()
                message = (
                    f"تم إغلاق الوردية ({shift.end_time.strftime('%I:%M %p')}). "
                    f"مدة الوردية: {duration}. "
                    f"شكراً لكم! سنكون متاحين في الوردية القادمة."
                )
            notification_type = "shift_closed"
        
        # إنشاء الإشعارات
        notifications = []
        for pharmacy in pharmacies:
            notifications.append(
                Notification(
                    user=pharmacy,
                    title=title,
                    message=message,
                    extra={
                        "type": notification_type,
                        "shift_id": shift_id,
                        "shift_type": shift_type,
                        "timestamp": timezone.now().isoformat(),
                    },
                    image_url=""
                )
            )
        
        # Bulk create
        created_notifications = Notification.objects.bulk_create(notifications)
        
        logger.info(
            f"Shift {shift_type} notification sent to {len(created_notifications)} pharmacies "
            f"for shift #{shift_id}"
        )
        
        return {
            "success": True,
            "count": len(created_notifications),
            "shift_id": shift_id,
            "shift_type": shift_type
        }
        
    except WorkShift.DoesNotExist:
        logger.error(f"WorkShift with ID {shift_id} not found")
        return {
            "success": False,
            "error": "Shift not found",
            "shift_id": shift_id
        }
    except Exception as exc:
        logger.error(f"Error sending shift notification: {str(exc)}")
        return {
            "success": False,
            "error": str(exc)
        }


@shared_task
def send_payment_due_reminders():
    """
    Task to send payment due reminders to pharmacies.
    
    Checks all pharmacies and sends reminders based on their payment period's
    reminder_days_before setting.
    
    Returns:
        dict: Summary of reminders sent
    """
    try:
        User = get_model("accounts", "User")
        Account = get_model("finance", "Account")
        Notification = get_model("notifications", "Notification")
        UserProfile = get_model("profiles", "UserProfile")
        
        today = timezone.now().date()
        notifications_sent = 0
        
        # Get all pharmacies with profiles and payment periods
        pharmacies = User.objects.filter(
            role='PHARMACY',
            is_active=True,
            profile__isnull=False,
            profile__payment_period__isnull=False
        ).select_related('profile', 'profile__payment_period', 'account')
        
        logger.info(f"Checking payment reminders for {pharmacies.count()} pharmacies")
        
        for pharmacy in pharmacies:
            try:
                profile = pharmacy.profile
                payment_period = profile.payment_period
                account = getattr(pharmacy, 'account', None)
                
                if not account:
                    continue
                
                # Check if account has outstanding balance (negative balance = owe money)
                if account.balance >= 0:
                    continue  # No outstanding balance
                
                outstanding_amount = abs(account.balance)
                
                # Get last invoice date
                last_invoice_date = profile.latest_invoice_date
                if not last_invoice_date:
                    continue
                
                # Calculate payment due date
                payment_due_date = last_invoice_date.date() + timedelta(days=payment_period.period_in_days)
                
                # Calculate reminder date (due date - reminder_days_before)
                reminder_days = payment_period.reminder_days_before
                reminder_date = payment_due_date - timedelta(days=reminder_days)
                
                # If today is the reminder date, send notification
                if today == reminder_date:
                    Notification.objects.create(
                        user=pharmacy,
                        title="⏰ تذكير: موعد التحصيل قريب",
                        message=(
                            f"لديك رصيد مستحق بقيمة {outstanding_amount:.2f} جنيه. "
                            f"موعد التحصيل بعد {reminder_days} أيام ({payment_due_date}). "
                            f"يرجى السداد في الموعد المحدد لتجنب أي رسوم تأخير."
                        ),
                        extra={
                            "type": "payment_due_reminder",
                            "outstanding_balance": str(outstanding_amount),
                            "due_date": str(payment_due_date),
                            "days_until_due": reminder_days,
                            "payment_period": payment_period.name,
                        },
                        image_url=""
                    )
                    notifications_sent += 1
                    logger.info(
                        f"Payment reminder sent to {pharmacy.name} "
                        f"(balance: {outstanding_amount}, due: {payment_due_date})"
                    )
                
                # Also check for overdue payments
                elif today > payment_due_date:
                    days_overdue = (today - payment_due_date).days
                    
                    # Send overdue reminder every 7 days
                    if days_overdue % 7 == 0:
                        Notification.objects.create(
                            user=pharmacy,
                            title="⚠️ تنبيه: دفعة متأخرة",
                            message=(
                                f"لديك رصيد متأخر بقيمة {outstanding_amount:.2f} جنيه. "
                                f"تأخر الدفع {days_overdue} يوم. "
                                f"يرجى السداد فوراً لتجنب رسوم التأخير الإضافية."
                            ),
                            extra={
                                "type": "payment_overdue",
                                "outstanding_balance": str(outstanding_amount),
                                "due_date": str(payment_due_date),
                                "days_overdue": days_overdue,
                                "payment_period": payment_period.name,
                            },
                            image_url=""
                        )
                        notifications_sent += 1
                        logger.warning(
                            f"Overdue payment reminder sent to {pharmacy.name} "
                            f"({days_overdue} days overdue)"
                        )
                        
            except Exception as e:
                logger.error(f"Error processing reminder for pharmacy {pharmacy.id}: {str(e)}")
                continue
        
        logger.info(f"Payment reminders completed. Sent {notifications_sent} notifications.")
        
        return {
            "success": True,
            "notifications_sent": notifications_sent,
            "pharmacies_checked": pharmacies.count()
        }
        
    except Exception as exc:
        logger.error(f"Error in send_payment_due_reminders: {str(exc)}")
        return {
            "success": False,
            "error": str(exc)
        }
