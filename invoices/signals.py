"""
Signals for the invoices app.

Automatically send notifications when invoice events occur.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from invoices.models import (
    PurchaseInvoice, 
    SaleInvoice,
    PurchaseReturnInvoice,
    SaleReturnInvoice
)
from invoices.choices import (
    PurchaseInvoiceStatusChoice, 
    SaleInvoiceStatusChoice,
    PurchaseReturnInvoiceStatusChoice,
    SaleReturnInvoiceStatusChoice
)
from notifications.models import Notification
from accounts.choices import Role
import logging

logger = logging.getLogger(__name__)


def get_admin_users():
    """Get all admin and manager users."""
    from accounts.models import User
    return User.objects.filter(role__in=[Role.ADMIN, Role.MANAGER], is_active=True)


@receiver(post_save, sender=PurchaseInvoice)
def on_purchase_invoice_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للمستخدم والـ Admin عند إنشاء فاتورة شراء جديدة.
    """
    if created:
        try:
            # إنشاء إشعار للمستخدم (المخزن)
            Notification.objects.create(
                user=instance.user,
                title="📦 فاتورة شراء جديدة",
                message=f"تم إنشاء فاتورة شراء رقم #{instance.pk} بقيمة {instance.total_price} جنيه",
                extra={
                    "type": "purchase_invoice",
                    "invoice_id": instance.pk,
                    "total_price": str(instance.total_price),
                    "items_count": instance.items_count,
                    "status": instance.status,
                },
                image_url=""
            )
            
            # إرسال إشعار للـ Admins
            admins = get_admin_users()
            admin_notifications = []
            for admin in admins:
                admin_notifications.append(
                    Notification(
                        user=admin,
                        title="📦 فاتورة شراء جديدة",
                        message=f"فاتورة شراء جديدة #{instance.pk} من {instance.user.name} بقيمة {instance.total_price} جنيه",
                        extra={
                            "type": "admin_purchase_invoice",
                            "invoice_id": instance.pk,
                            "user_id": instance.user.pk,
                            "user_name": instance.user.name,
                            "total_price": str(instance.total_price),
                            "items_count": instance.items_count,
                        },
                        image_url=""
                    )
                )
            if admin_notifications:
                Notification.objects.bulk_create(admin_notifications)
            
            logger.info(f"Notification sent for Purchase Invoice #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Purchase Invoice #{instance.pk}: {str(e)}")


@receiver(post_save, sender=SaleInvoice)
def on_sale_invoice_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للصيدلية والـ Admin عند إنشاء فاتورة بيع (طلب) جديدة.
    """
    if created:
        try:
            # إنشاء إشعار للصيدلية
            Notification.objects.create(
                user=instance.user,
                title="🛒 طلب جديد تم إنشاؤه",
                message=f"تم إنشاء طلبك رقم #{instance.pk} بنجاح. إجمالي المبلغ: {instance.total_price} جنيه",
                extra={
                    "type": "sale_invoice",
                    "invoice_id": instance.pk,
                    "total_price": str(instance.total_price),
                    "items_count": instance.items_count,
                    "status": instance.status,
                },
                image_url=""
            )
            
            # إرسال إشعار للـ Admins
            admins = get_admin_users()
            admin_notifications = []
            for admin in admins:
                admin_notifications.append(
                    Notification(
                        user=admin,
                        title="🛒 طلب جديد",
                        message=f"طلب جديد #{instance.pk} من {instance.user.name} بقيمة {instance.total_price} جنيه",
                        extra={
                            "type": "admin_sale_invoice",
                            "invoice_id": instance.pk,
                            "user_id": instance.user.pk,
                            "user_name": instance.user.name,
                            "total_price": str(instance.total_price),
                            "items_count": instance.items_count,
                        },
                        image_url=""
                    )
                )
            if admin_notifications:
                Notification.objects.bulk_create(admin_notifications)
            
            logger.info(f"Notification sent for Sale Invoice #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Sale Invoice #{instance.pk}: {str(e)}")


@receiver(pre_save, sender=PurchaseInvoice)
def on_purchase_invoice_status_changed(sender, instance, **kwargs):
    """
    إرسال إشعار عند تغيير حالة فاتورة الشراء.
    """
    if instance.pk:  # فقط للفواتير الموجودة (تحديث)
        try:
            old_instance = PurchaseInvoice.objects.get(pk=instance.pk)
            
            # إذا تغيرت الحالة
            if old_instance.status != instance.status:
                status_messages = {
                    PurchaseInvoiceStatusChoice.PLACED: "تم استلام طلبك",
                    PurchaseInvoiceStatusChoice.PROCESSING: "جاري تجهيز طلبك",
                    PurchaseInvoiceStatusChoice.SHIPPED: "تم شحن طلبك",
                    PurchaseInvoiceStatusChoice.DELIVERED: "تم توصيل طلبك بنجاح",
                    PurchaseInvoiceStatusChoice.CANCELLED: "تم إلغاء طلبك",
                }
                
                message = status_messages.get(
                    instance.status,
                    f"تم تحديث حالة طلبك إلى {instance.get_status_display()}"
                )
                
                Notification.objects.create(
                    user=instance.user,
                    title="📋 تحديث حالة الطلب",
                    message=f"{message} - طلب رقم #{instance.pk}",
                    extra={
                        "type": "invoice_status_update",
                        "invoice_id": instance.pk,
                        "old_status": old_instance.status,
                        "new_status": instance.status,
                    },
                    image_url=""
                )
                logger.info(f"Status change notification sent for Purchase Invoice #{instance.pk}")
        except PurchaseInvoice.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to send status change notification: {str(e)}")


@receiver(pre_save, sender=SaleInvoice)
def on_sale_invoice_status_changed(sender, instance, **kwargs):
    """
    إرسال إشعار عند تغيير حالة فاتورة البيع (طلب الصيدلية).
    """
    if instance.pk:  # فقط للفواتير الموجودة (تحديث)
        try:
            old_instance = SaleInvoice.objects.get(pk=instance.pk)
            
            # إذا تغيرت الحالة
            if old_instance.status != instance.status:
                status_messages = {
                    SaleInvoiceStatusChoice.PLACED: "تم استلام طلبك",
                    SaleInvoiceStatusChoice.PROCESSING: "جاري تجهيز طلبك",
                    SaleInvoiceStatusChoice.SHIPPED: "تم شحن طلبك 🚚",
                    SaleInvoiceStatusChoice.DELIVERED: "تم توصيل طلبك بنجاح ✅",
                    SaleInvoiceStatusChoice.CANCELLED: "تم إلغاء طلبك ❌",
                }
                
                message = status_messages.get(
                    instance.status,
                    f"تم تحديث حالة طلبك إلى {instance.get_status_display()}"
                )
                
                Notification.objects.create(
                    user=instance.user,
                    title="🔔 تحديث حالة الطلب",
                    message=f"{message} - طلب رقم #{instance.pk}",
                    extra={
                        "type": "invoice_status_update",
                        "invoice_id": instance.pk,
                        "old_status": old_instance.status,
                        "new_status": instance.status,
                    },
                    image_url=""
                )
                logger.info(f"Status change notification sent for Sale Invoice #{instance.pk}")
        except SaleInvoice.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to send status change notification: {str(e)}")


# ==========================================
# Return Invoice Notifications
# ==========================================

@receiver(post_save, sender=PurchaseReturnInvoice)
def on_purchase_return_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للمخزن عند إنشاء مرتجع شراء (إرجاع للمورد).
    """
    if created:
        try:
            Notification.objects.create(
                user=instance.user,
                title="↩️ مرتجع شراء جديد",
                message=f"تم إنشاء مرتجع شراء رقم #{instance.pk} بقيمة {instance.total_price} جنيه",
                extra={
                    "type": "purchase_return",
                    "return_id": instance.pk,
                    "total_price": str(instance.total_price),
                    "items_count": instance.items_count,
                    "status": instance.status,
                },
                image_url=""
            )
            logger.info(f"Notification sent for Purchase Return #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Purchase Return #{instance.pk}: {str(e)}")


@receiver(post_save, sender=SaleReturnInvoice)
def on_sale_return_created(sender, instance, created, **kwargs):
    """
    إرسال إشعار للصيدلية عند إنشاء مرتجع بيع (إرجاع للمخزن).
    """
    if created:
        try:
            Notification.objects.create(
                user=instance.user,
                title="↩️ طلب إرجاع تم إنشاؤه",
                message=f"تم إنشاء طلب إرجاع رقم #{instance.pk} بقيمة {instance.total_price} جنيه. سيتم مراجعته قريباً.",
                extra={
                    "type": "sale_return",
                    "return_id": instance.pk,
                    "total_price": str(instance.total_price),
                    "items_count": instance.items_count,
                    "status": instance.status,
                },
                image_url=""
            )
            logger.info(f"Notification sent for Sale Return #{instance.pk}")
        except Exception as e:
            logger.error(f"Failed to send notification for Sale Return #{instance.pk}: {str(e)}")


@receiver(pre_save, sender=PurchaseReturnInvoice)
def on_purchase_return_status_changed(sender, instance, **kwargs):
    """
    إرسال إشعار عند تغيير حالة مرتجع الشراء.
    """
    if instance.pk:
        try:
            old_instance = PurchaseReturnInvoice.objects.get(pk=instance.pk)
            
            if old_instance.status != instance.status:
                status_messages = {
                    PurchaseReturnInvoiceStatusChoice.PLACED: "تم استلام طلب الإرجاع",
                    PurchaseReturnInvoiceStatusChoice.APPROVED: "تمت الموافقة على الإرجاع ✅",
                    PurchaseReturnInvoiceStatusChoice.REJECTED: "تم رفض الإرجاع ❌",
                    PurchaseReturnInvoiceStatusChoice.COMPLETED: "تم إكمال عملية الإرجاع بنجاح",
                }
                
                message = status_messages.get(
                    instance.status,
                    f"تم تحديث حالة الإرجاع إلى {instance.get_status_display()}"
                )
                
                Notification.objects.create(
                    user=instance.user,
                    title="🔔 تحديث حالة المرتجع",
                    message=f"{message} - مرتجع رقم #{instance.pk}",
                    extra={
                        "type": "return_status_update",
                        "return_id": instance.pk,
                        "old_status": old_instance.status,
                        "new_status": instance.status,
                    },
                    image_url=""
                )
                logger.info(f"Status change notification sent for Purchase Return #{instance.pk}")
        except PurchaseReturnInvoice.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to send return status notification: {str(e)}")


@receiver(pre_save, sender=SaleReturnInvoice)
def on_sale_return_status_changed(sender, instance, **kwargs):
    """
    إرسال إشعار عند تغيير حالة مرتجع البيع (إرجاع الصيدلية).
    """
    if instance.pk:
        try:
            old_instance = SaleReturnInvoice.objects.get(pk=instance.pk)
            
            if old_instance.status != instance.status:
                status_messages = {
                    SaleReturnInvoiceStatusChoice.PLACED: "تم استلام طلب الإرجاع",
                    SaleReturnInvoiceStatusChoice.APPROVED: "تمت الموافقة على طلب إرجاعك ✅",
                    SaleReturnInvoiceStatusChoice.REJECTED: "تم رفض طلب الإرجاع ❌",
                    SaleReturnInvoiceStatusChoice.COMPLETED: "تم إكمال عملية الإرجاع واسترداد المبلغ 💰",
                }
                
                message = status_messages.get(
                    instance.status,
                    f"تم تحديث حالة طلب الإرجاع إلى {instance.get_status_display()}"
                )
                
                Notification.objects.create(
                    user=instance.user,
                    title="🔔 تحديث حالة الإرجاع",
                    message=f"{message} - طلب إرجاع رقم #{instance.pk}",
                    extra={
                        "type": "return_status_update",
                        "return_id": instance.pk,
                        "old_status": old_instance.status,
                        "new_status": instance.status,
                    },
                    image_url=""
                )
                logger.info(f"Status change notification sent for Sale Return #{instance.pk}")
        except SaleReturnInvoice.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to send return status notification: {str(e)}")

