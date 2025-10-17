"""
Notification utility functions for finance operations.

Functions to send notifications for payments and returns.
"""

from notifications.models import Notification
from notifications.tasks import send_notification_to_user
import logging

logger = logging.getLogger(__name__)


# ==========================================
# Payment Notifications
# ==========================================

def notify_purchase_payment(payment):
    """
    إرسال إشعار للمخزن عند تسجيل دفعة شراء.
    
    Args:
        payment: PurchasePayment instance
    """
    try:
        notification = Notification.objects.create(
            user=payment.user,
            title="💰 دفعة شراء جديدة",
            message=f"تم تسجيل دفعة شراء بقيمة {payment.amount} جنيه. طريقة الدفع: {payment.get_method_display()}",
            extra={
                "type": "purchase_payment",
                "payment_id": payment.pk,
                "amount": str(payment.amount),
                "method": payment.method,
                "remarks": payment.remarks,
            },
            image_url=""
        )
        logger.info(f"Payment notification sent to user {payment.user.id}")
        return notification
    except Exception as e:
        logger.error(f"Failed to send purchase payment notification: {str(e)}")
        return None


def notify_sale_payment(payment):
    """
    إرسال إشعار للصيدلية عند تسجيل دفعة بيع.
    
    Args:
        payment: SalePayment instance
    """
    try:
        notification = Notification.objects.create(
            user=payment.user,
            title="✅ تم تسجيل دفعتك",
            message=f"تم تسجيل دفعة بقيمة {payment.amount} جنيه بنجاح. طريقة الدفع: {payment.get_method_display()}",
            extra={
                "type": "sale_payment",
                "payment_id": payment.pk,
                "amount": str(payment.amount),
                "method": payment.method,
                "remarks": payment.remarks,
            },
            image_url=""
        )
        logger.info(f"Payment notification sent to user {payment.user.id}")
        return notification
    except Exception as e:
        logger.error(f"Failed to send sale payment notification: {str(e)}")
        return None


def notify_payment_received(user, amount, method, payment_type="sale"):
    """
    إشعار عام باستلام دفعة.
    
    Args:
        user: المستخدم
        amount: المبلغ
        method: طريقة الدفع
        payment_type: نوع الدفع (sale/purchase)
    """
    try:
        title = "💰 تم استلام الدفع" if payment_type == "sale" else "💰 دفعة جديدة"
        message = f"تم تسجيل دفعة بقيمة {amount} جنيه عبر {method}"
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            extra={
                "type": f"{payment_type}_payment_received",
                "amount": str(amount),
                "method": method,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send payment received notification: {str(e)}")
        return None


def notify_payment_reminder(user, outstanding_balance):
    """
    إشعار بتذكير الدفع.
    
    Args:
        user: المستخدم
        outstanding_balance: الرصيد المستحق
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title="⏰ تذكير بالدفع",
            message=f"لديك رصيد مستحق بقيمة {outstanding_balance} جنيه. يرجى السداد في أقرب وقت.",
            extra={
                "type": "payment_reminder",
                "outstanding_balance": str(outstanding_balance),
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send payment reminder: {str(e)}")
        return None


# ==========================================
# Return Notifications
# ==========================================

def notify_return_created(return_invoice, return_type="sale"):
    """
    إشعار بإنشاء طلب إرجاع.
    
    Args:
        return_invoice: PurchaseReturnInvoice or SaleReturnInvoice instance
        return_type: نوع الإرجاع (sale/purchase)
    """
    try:
        if return_type == "sale":
            title = "↩️ طلب إرجاع تم إنشاؤه"
            message = f"تم إنشاء طلب إرجاع رقم #{return_invoice.pk} بقيمة {return_invoice.total_price} جنيه. سيتم مراجعته قريباً."
        else:
            title = "↩️ مرتجع شراء جديد"
            message = f"تم إنشاء مرتجع شراء رقم #{return_invoice.pk} بقيمة {return_invoice.total_price} جنيه"
        
        notification = Notification.objects.create(
            user=return_invoice.user,
            title=title,
            message=message,
            extra={
                "type": f"{return_type}_return",
                "return_id": return_invoice.pk,
                "total_price": str(return_invoice.total_price),
                "items_count": return_invoice.items_count,
                "status": return_invoice.status,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send return created notification: {str(e)}")
        return None


def notify_return_approved(return_invoice, return_type="sale"):
    """
    إشعار بالموافقة على طلب الإرجاع.
    
    Args:
        return_invoice: Return invoice instance
        return_type: نوع الإرجاع
    """
    try:
        notification = Notification.objects.create(
            user=return_invoice.user,
            title="✅ تمت الموافقة على الإرجاع",
            message=f"تمت الموافقة على طلب الإرجاع رقم #{return_invoice.pk}. سيتم معالجة طلبك قريباً.",
            extra={
                "type": "return_approved",
                "return_id": return_invoice.pk,
                "return_type": return_type,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send return approved notification: {str(e)}")
        return None


def notify_return_rejected(return_invoice, reason="", return_type="sale"):
    """
    إشعار برفض طلب الإرجاع.
    
    Args:
        return_invoice: Return invoice instance
        reason: سبب الرفض
        return_type: نوع الإرجاع
    """
    try:
        message = f"عذراً، تم رفض طلب الإرجاع رقم #{return_invoice.pk}"
        if reason:
            message += f". السبب: {reason}"
        
        notification = Notification.objects.create(
            user=return_invoice.user,
            title="❌ تم رفض الإرجاع",
            message=message,
            extra={
                "type": "return_rejected",
                "return_id": return_invoice.pk,
                "reason": reason,
                "return_type": return_type,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send return rejected notification: {str(e)}")
        return None


def notify_return_completed(return_invoice, refund_amount=None, return_type="sale"):
    """
    إشعار بإكمال عملية الإرجاع.
    
    Args:
        return_invoice: Return invoice instance
        refund_amount: مبلغ الاسترداد
        return_type: نوع الإرجاع
    """
    try:
        message = f"تم إكمال عملية الإرجاع رقم #{return_invoice.pk} بنجاح"
        if refund_amount:
            message += f". تم استرداد {refund_amount} جنيه إلى حسابك 💰"
        
        notification = Notification.objects.create(
            user=return_invoice.user,
            title="✅ تم إكمال الإرجاع",
            message=message,
            extra={
                "type": "return_completed",
                "return_id": return_invoice.pk,
                "refund_amount": str(refund_amount) if refund_amount else None,
                "return_type": return_type,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send return completed notification: {str(e)}")
        return None


def notify_refund_processed(user, amount, original_invoice_id=None):
    """
    إشعار بمعالجة استرداد المبلغ.
    
    Args:
        user: المستخدم
        amount: مبلغ الاسترداد
        original_invoice_id: رقم الفاتورة الأصلية
    """
    try:
        message = f"تم معالجة استرداد بقيمة {amount} جنيه"
        if original_invoice_id:
            message += f" للفاتورة رقم #{original_invoice_id}"
        
        notification = Notification.objects.create(
            user=user,
            title="💰 تم استرداد المبلغ",
            message=message,
            extra={
                "type": "refund_processed",
                "amount": str(amount),
                "original_invoice_id": original_invoice_id,
            },
            image_url=""
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to send refund notification: {str(e)}")
        return None

