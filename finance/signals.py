"""
Signals for the finance app.

Automatically send notifications for payment and transaction events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from finance.models import PurchasePayment, SalePayment
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PurchasePayment)
def on_purchase_payment_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للمخزن عند استلام دفعة شراء (من المورد).
    """
    if created:
        try:
            Notification.objects.create(
                user=instance.user,
                title="💰 دفعة شراء جديدة",
                message=f"تم تسجيل دفعة شراء بقيمة {instance.amount} جنيه. طريقة الدفع: {instance.get_method_display()}",
                extra={
                    "type": "purchase_payment",
                    "payment_id": instance.pk,
                    "amount": str(instance.amount),
                    "method": instance.method,
                    "remarks": instance.remarks,
                },
                image_url=""
            )
            logger.info(f"Payment notification sent for Purchase Payment #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Purchase Payment #{instance.pk}: {str(e)}")


@receiver(post_save, sender=SalePayment)
def on_sale_payment_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للصيدلية عند تسجيل دفعة بيع (للمخزن).
    """
    if created:
        try:
            Notification.objects.create(
                user=instance.user,
                title="✅ تم تسجيل دفعتك",
                message=f"تم تسجيل دفعة بقيمة {instance.amount} جنيه بنجاح. طريقة الدفع: {instance.get_method_display()}",
                extra={
                    "type": "sale_payment",
                    "payment_id": instance.pk,
                    "amount": str(instance.amount),
                    "method": instance.method,
                    "remarks": instance.remarks,
                },
                image_url=""
            )
            logger.info(f"Payment notification sent for Sale Payment #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Sale Payment #{instance.pk}: {str(e)}")

