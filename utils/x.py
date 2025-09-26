from push_notifications.models import APNSDevice, GCMDevice
from firebase_admin import messaging


def send_notification():
    device = GCMDevice.objects.get(pk=2)
    # Basic notification
    device.send_message(
        messaging.Message(
            notification=messaging.Notification(
                title="Hello World",
                body="What a beautiful day.",
                image="http://127.0.0.1:8092/assets/images/header-logo.png",
            ),
            data={"key1": "value1", "key2": "value2"},
        )
    )
