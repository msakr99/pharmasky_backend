"""
Notification utilities for PharmaSky application.
This module provides helper functions for sending push notifications.
"""

# from push_notifications.models import GCMDevice  # Disabled temporarily
from firebase_admin import messaging
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def send_push_notification(
    device_id: int, 
    title: str, 
    body: str, 
    data: Optional[Dict[str, Any]] = None,
    image_url: Optional[str] = None
) -> bool:
    """
    Send push notification to a specific device.
    
    Args:
        device_id: The ID of the GCM device
        title: Notification title
        body: Notification body
        data: Optional data payload
        image_url: Optional image URL for rich notifications
        
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    try:
        device = GCMDevice.objects.get(pk=device_id)
        
        # Prepare notification message
        notification = messaging.Notification(
            title=title,
            body=body,
        )
        
        if image_url:
            notification.image = image_url
            
        message = messaging.Message(
            notification=notification,
            data=data or {}
        )
        
        # Send notification
        device.send_message(message)
        logger.info(f"Notification sent successfully to device {device_id}")
        return True
        
    except GCMDevice.DoesNotExist:
        logger.error(f"Device with ID {device_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send notification to device {device_id}: {str(e)}")
        return False


def send_bulk_notification(
    user_ids: list,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    image_url: Optional[str] = None
) -> Dict[str, int]:
    """
    Send notification to multiple users.
    
    Args:
        user_ids: List of user IDs to send notification to
        title: Notification title
        body: Notification body
        data: Optional data payload
        image_url: Optional image URL
        
    Returns:
        Dict with success and failure counts
    """
    devices = GCMDevice.objects.filter(user_id__in=user_ids, active=True)
    success_count = 0
    failure_count = 0
    
    for device in devices:
        if send_push_notification(device.pk, title, body, data, image_url):
            success_count += 1
        else:
            failure_count += 1
            
    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'total_devices': devices.count()
    }
