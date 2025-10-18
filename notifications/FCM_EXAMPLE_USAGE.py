"""
أمثلة عملية لاستخدام نظام Push Notifications مع FCM
"""

# ═══════════════════════════════════════════════════════════════════
# مثال 1: إرسال إشعار بسيط لمستخدم واحد
# ═══════════════════════════════════════════════════════════════════

def example_send_to_single_user():
    """مثال: إرسال إشعار لمستخدم واحد"""
    from notifications.utils import send_push_to_user
    
    result = send_push_to_user(
        user_id=1,
        title="طلب جديد",
        message="تم استلام طلبك بنجاح!",
        data={
            "order_id": 123,
            "type": "new_order",
            "url": "/orders/123"
        }
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Failure: {result.get('failure')}")


# ═══════════════════════════════════════════════════════════════════
# مثال 2: إرسال إشعار لعدة مستخدمين
# ═══════════════════════════════════════════════════════════════════

def example_send_to_multiple_users():
    """مثال: إرسال إشعار لعدة مستخدمين"""
    from notifications.utils import send_push_notification
    
    # قائمة معرفات المستخدمين
    user_ids = [1, 2, 3, 4, 5]
    
    result = send_push_notification(
        title="عرض خاص",
        message="خصم 20% على جميع الأدوية اليوم!",
        user_ids=user_ids,
        data={
            "type": "offer",
            "discount": 20,
            "url": "/offers"
        }
    )
    
    print(f"Sent to {result.get('success')} users")


# ═══════════════════════════════════════════════════════════════════
# مثال 3: إرسال إشعار لجميع المستخدمين
# ═══════════════════════════════════════════════════════════════════

def example_send_to_all_users():
    """مثال: إرسال إشعار لجميع المستخدمين"""
    from notifications.utils import send_push_to_all_users
    
    result = send_push_to_all_users(
        title="إعلان مهم",
        message="سيتم إيقاف الخدمة للصيانة غدًا من 12 ص إلى 6 ص",
        data={
            "type": "maintenance",
            "start_time": "2024-01-15 00:00:00",
            "end_time": "2024-01-15 06:00:00"
        }
    )
    
    print(f"Sent to all users: {result}")


# ═══════════════════════════════════════════════════════════════════
# مثال 4: إنشاء إشعار في قاعدة البيانات + إرسال Push
# ═══════════════════════════════════════════════════════════════════

def example_create_notification_with_push():
    """مثال: إنشاء إشعار في DB وإرساله كـ Push"""
    from notifications.utils import send_notification_with_push
    
    notification = send_notification_with_push(
        user_id=1,
        title="فاتورة جديدة",
        message="تم إنشاء فاتورة رقم INV-001",
        extra={
            "invoice_id": "INV-001",
            "amount": 1500.00,
            "url": "/invoices/INV-001"
        },
        send_push=True  # إرسال Push Notification
    )
    
    print(f"Notification created: {notification.id}")


# ═══════════════════════════════════════════════════════════════════
# مثال 5: إرسال إشعار مع صورة
# ═══════════════════════════════════════════════════════════════════

def example_send_with_image():
    """مثال: إرسال إشعار مع صورة"""
    from notifications.utils import send_push_notification
    
    result = send_push_notification(
        title="منتج جديد",
        message="تم إضافة Aspirin 500mg إلى المخزون",
        user_ids=[1],
        data={"product_id": 456},
        image_url="https://example.com/images/aspirin.jpg"
    )
    
    print(f"Notification sent with image")


# ═══════════════════════════════════════════════════════════════════
# مثال 6: إرسال إشعار عند إنشاء طلب (في Signal)
# ═══════════════════════════════════════════════════════════════════

# في ملف signals.py
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from notifications.utils import send_notification_with_push

@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    if created:
        # إرسال إشعار للمستخدم عند إنشاء طلب جديد
        send_notification_with_push(
            user_id=instance.user.id,
            title="طلب جديد",
            message=f"تم إنشاء طلبك رقم {instance.order_number}",
            extra={
                "order_id": instance.id,
                "order_number": instance.order_number,
                "total": str(instance.total_amount),
                "url": f"/orders/{instance.id}"
            }
        )
"""


# ═══════════════════════════════════════════════════════════════════
# مثال 7: إرسال إشعار مُجدول باستخدام Celery
# ═══════════════════════════════════════════════════════════════════

# في ملف tasks.py
"""
from celery import shared_task
from notifications.utils import send_push_to_user

@shared_task
def send_payment_reminder(user_id, invoice_id):
    '''إرسال تذكير بالدفع'''
    send_push_to_user(
        user_id=user_id,
        title="تذكير بالدفع",
        message="لديك فاتورة مستحقة الدفع",
        data={
            "type": "payment_reminder",
            "invoice_id": invoice_id,
            "url": f"/invoices/{invoice_id}"
        }
    )

# استخدام:
# send_payment_reminder.apply_async(
#     args=[user_id, invoice_id],
#     countdown=86400  # إرسال بعد 24 ساعة
# )
"""


# ═══════════════════════════════════════════════════════════════════
# مثال 8: إرسال إشعار لمستخدمين بناءً على Role
# ═══════════════════════════════════════════════════════════════════

def example_send_to_pharmacists():
    """مثال: إرسال إشعار لجميع الصيادلة"""
    from accounts.models import User
    from notifications.utils import send_push_notification
    
    # الحصول على جميع الصيادلة
    pharmacist_ids = User.objects.filter(
        role="pharmacist",
        is_active=True
    ).values_list("id", flat=True)
    
    result = send_push_notification(
        title="تحديث المخزون",
        message="تم تحديث قائمة الأدوية المتاحة",
        user_ids=list(pharmacist_ids),
        data={"type": "inventory_update"}
    )
    
    print(f"Sent to {result.get('success')} pharmacists")


# ═══════════════════════════════════════════════════════════════════
# مثال 9: اختبار النظام
# ═══════════════════════════════════════════════════════════════════

def example_test_notification():
    """مثال: اختبار سريع للنظام"""
    from notifications.utils import test_push_notification
    
    result = test_push_notification(user_id=1)
    
    if result.get("success"):
        print("✅ النظام يعمل بنجاح!")
    else:
        print(f"❌ خطأ: {result.get('error')}")


# ═══════════════════════════════════════════════════════════════════
# مثال 10: إرسال إشعار من Django Admin Action
# ═══════════════════════════════════════════════════════════════════

# في ملف admin.py
"""
from django.contrib import admin
from notifications.utils import send_push_to_user

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = ["send_order_notification"]
    
    @admin.action(description="Send notification to users")
    def send_order_notification(self, request, queryset):
        for order in queryset:
            send_push_to_user(
                user_id=order.user.id,
                title="تحديث الطلب",
                message=f"تم تحديث حالة طلبك رقم {order.order_number}",
                data={"order_id": order.id}
            )
        
        self.message_user(
            request,
            f"تم إرسال {queryset.count()} إشعار"
        )
"""


# ═══════════════════════════════════════════════════════════════════
# كيفية التشغيل من Django Shell
# ═══════════════════════════════════════════════════════════════════
"""
1. افتح Django shell:
   python manage.py shell

2. استورد المثال وشغله:
   from notifications.FCM_EXAMPLE_USAGE import example_send_to_single_user
   example_send_to_single_user()

3. أو مباشرة:
   from notifications.utils import test_push_notification
   test_push_notification(user_id=1)
"""


# ═══════════════════════════════════════════════════════════════════
# دالة شاملة لعرض جميع الأمثلة
# ═══════════════════════════════════════════════════════════════════

def run_all_examples():
    """تشغيل جميع الأمثلة (للاختبار فقط)"""
    print("=" * 70)
    print("مثال 1: إرسال لمستخدم واحد")
    print("=" * 70)
    example_send_to_single_user()
    
    print("\n" + "=" * 70)
    print("مثال 2: إرسال لعدة مستخدمين")
    print("=" * 70)
    example_send_to_multiple_users()
    
    print("\n" + "=" * 70)
    print("مثال 4: إنشاء + إرسال")
    print("=" * 70)
    example_create_notification_with_push()
    
    print("\n" + "=" * 70)
    print("مثال 9: اختبار النظام")
    print("=" * 70)
    example_test_notification()


if __name__ == "__main__":
    # إذا تم تشغيل الملف مباشرة
    print("⚠️ هذا الملف يحتوي على أمثلة فقط")
    print("استخدم: python manage.py shell")
    print("ثم: from notifications.FCM_EXAMPLE_USAGE import example_send_to_single_user")

