"""
Notification utility functions for invoices.

Easy-to-use functions to send notifications related to invoices.
"""

from notifications.models import Notification
from notifications.tasks import send_notification_to_user
import logging

logger = logging.getLogger(__name__)


def send_invoice_notification(user, title, message, invoice_id, extra_data=None):
    """
    إرسال إشعار للمستخدم بخصوص فاتورة.
    
    Args:
        user: المستخدم المستقبل للإشعار
        title: عنوان الإشعار
        message: محتوى الإشعار
        invoice_id: رقم الفاتورة
        extra_data: بيانات إضافية (dict)
    
    Returns:
        Notification instance or None
    """
    try:
        extra = extra_data or {}
        extra['invoice_id'] = invoice_id
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            extra=extra,
            image_url=""
        )
        
        logger.info(f"Invoice notification sent to user {user.id} for invoice #{invoice_id}")
        return notification
    except Exception as e:
        logger.error(f"Failed to send invoice notification: {str(e)}")
        return None


def send_invoice_notification_async(user_id, title, message, invoice_id, extra_data=None):
    """
    إرسال إشعار للمستخدم بشكل غير متزامن (باستخدام Celery).
    
    Args:
        user_id: ID المستخدم
        title: عنوان الإشعار
        message: محتوى الإشعار
        invoice_id: رقم الفاتورة
        extra_data: بيانات إضافية (dict)
    """
    try:
        extra = extra_data or {}
        extra['invoice_id'] = invoice_id
        
        send_notification_to_user.delay(
            user_id=user_id,
            title=title,
            message=message,
            extra=extra,
            image_url=""
        )
        
        logger.info(f"Async invoice notification queued for user {user_id}, invoice #{invoice_id}")
    except Exception as e:
        logger.error(f"Failed to queue async invoice notification: {str(e)}")


def notify_invoice_created(invoice, invoice_type="purchase"):
    """
    إشعار بإنشاء فاتورة جديدة.
    
    Args:
        invoice: Invoice instance (PurchaseInvoice or SaleInvoice)
        invoice_type: نوع الفاتورة ("purchase" or "sale")
    """
    if invoice_type == "purchase":
        title = "📦 فاتورة شراء جديدة"
        message = f"تم إنشاء فاتورة شراء رقم #{invoice.pk} بقيمة {invoice.total_price} جنيه"
    else:
        title = "🛒 طلب جديد"
        message = f"تم إنشاء طلبك رقم #{invoice.pk} بنجاح. إجمالي المبلغ: {invoice.total_price} جنيه"
    
    return send_invoice_notification(
        user=invoice.user,
        title=title,
        message=message,
        invoice_id=invoice.pk,
        extra_data={
            "type": f"{invoice_type}_invoice",
            "total_price": str(invoice.total_price),
            "items_count": invoice.items_count,
            "status": invoice.status,
        }
    )


def notify_invoice_status_changed(invoice, old_status, new_status, invoice_type="purchase"):
    """
    إشعار بتغيير حالة الفاتورة.
    
    Args:
        invoice: Invoice instance
        old_status: الحالة القديمة
        new_status: الحالة الجديدة
        invoice_type: نوع الفاتورة
    """
    status_messages = {
        'PLACED': "تم استلام طلبك",
        'PROCESSING': "جاري تجهيز طلبك",
        'SHIPPED': "تم شحن طلبك 🚚",
        'DELIVERED': "تم توصيل طلبك بنجاح ✅",
        'CANCELLED': "تم إلغاء طلبك ❌",
    }
    
    message = status_messages.get(
        new_status,
        f"تم تحديث حالة طلبك إلى {new_status}"
    )
    
    return send_invoice_notification(
        user=invoice.user,
        title="🔔 تحديث حالة الطلب",
        message=f"{message} - طلب رقم #{invoice.pk}",
        invoice_id=invoice.pk,
        extra_data={
            "type": "invoice_status_update",
            "old_status": old_status,
            "new_status": new_status,
        }
    )


def notify_invoice_shipped(invoice):
    """إشعار بشحن الفاتورة."""
    return send_invoice_notification(
        user=invoice.user,
        title="📦 تم شحن طلبك",
        message=f"طلبك رقم #{invoice.pk} في الطريق إليك!",
        invoice_id=invoice.pk,
        extra_data={"type": "invoice_shipped"}
    )


def notify_invoice_delivered(invoice):
    """إشعار بتوصيل الفاتورة."""
    return send_invoice_notification(
        user=invoice.user,
        title="✅ تم التوصيل بنجاح",
        message=f"تم توصيل طلبك رقم #{invoice.pk} بنجاح. نتمنى لك تجربة ممتعة!",
        invoice_id=invoice.pk,
        extra_data={"type": "invoice_delivered"}
    )


def notify_invoice_cancelled(invoice, reason=""):
    """إشعار بإلغاء الفاتورة."""
    message = f"تم إلغاء طلبك رقم #{invoice.pk}"
    if reason:
        message += f". السبب: {reason}"
    
    return send_invoice_notification(
        user=invoice.user,
        title="❌ تم إلغاء الطلب",
        message=message,
        invoice_id=invoice.pk,
        extra_data={
            "type": "invoice_cancelled",
            "reason": reason
        }
    )


def notify_payment_received(invoice, amount):
    """إشعار باستلام الدفع."""
    return send_invoice_notification(
        user=invoice.user,
        title="💰 تم استلام الدفع",
        message=f"تم استلام دفعة بقيمة {amount} جنيه لطلبك رقم #{invoice.pk}",
        invoice_id=invoice.pk,
        extra_data={
            "type": "payment_received",
            "amount": str(amount)
        }
    )


def notify_low_stock_alert(user, product_name, current_stock):
    """إشعار بنفاذ المخزون."""
    return Notification.objects.create(
        user=user,
        title="⚠️ تنبيه: مخزون منخفض",
        message=f"المنتج '{product_name}' أوشك على النفاذ. الكمية المتبقية: {current_stock}",
        extra={
            "type": "low_stock_alert",
            "product_name": product_name,
            "current_stock": current_stock
        },
        image_url=""
    )

