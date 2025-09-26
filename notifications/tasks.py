from celery import shared_task


@shared_task
def send_notification():
    """
    Task to send a notification.
    This function should contain the logic to send the notification.
    """
    # Here you would implement the logic to send the notification
    # For example, sending an email, push notification, etc.
    print(f"Sending notification")
    # You can also log this or handle exceptions as needed
