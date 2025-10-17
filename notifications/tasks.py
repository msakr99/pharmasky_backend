"""
Celery tasks for the notifications app.

This module provides asynchronous tasks for sending notifications.
"""

from celery import shared_task
from django.apps import apps
from django.utils import timezone
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
