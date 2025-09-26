from push_notifications.models import GCMDevice
from firebase_admin.messaging import Message, Notification as FCMNotification


def send_user_fcm_message(notification):
    user_devices = GCMDevice.objects.filter(user=notification.user)
    message = Message(
        notification=FCMNotification(
            title=notification.title,
            body=notification.message,
            image=notification.image_url or "http://127.0.0.1:8092/assets/images/notification-logo.png",
        ),
        data={"key1": "value1", "key2": "value2"},
    )
    for device in user_devices:
        device.send_message(message)
