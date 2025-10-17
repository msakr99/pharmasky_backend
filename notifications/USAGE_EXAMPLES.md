# 📱 أمثلة عملية لاستخدام نظام الإشعارات

## 📋 جدول المحتويات
1. [الاستخدام مع الفواتير](#1-الاستخدام-مع-الفواتير)
2. [الاستخدام من Views](#2-الاستخدام-من-views)
3. [الاستخدام من API](#3-الاستخدام-من-api)
4. [الاستخدام مع Celery Tasks](#4-الاستخدام-مع-celery-tasks)
5. [الاستخدام من Django Shell](#5-الاستخدام-من-django-shell)

---

## 1. الاستخدام مع الفواتير

### ✅ طريقة 1: تلقائياً (Signals) - الأسهل

تم إعداد Signals تشتغل تلقائياً! فقط اعمل الفاتورة وهيتبعت الإشعار أوتوماتيك:

```python
from invoices.models import SaleInvoice

# إنشاء فاتورة عادية
invoice = SaleInvoice.objects.create(
    user=pharmacy_user,
    items_count=5,
    total_quantity=20,
    total_price=1500.00,
    status='PLACED'
)

# ✨ الإشعار هيتبعت تلقائياً للصيدلية!
# "🛒 طلب جديد تم إنشاؤه - تم إنشاء طلبك رقم #123..."
```

### ✅ طريقة 2: استخدام Utility Functions

```python
from invoices.notifications import (
    notify_invoice_created,
    notify_invoice_shipped,
    notify_invoice_delivered,
    notify_invoice_cancelled,
)

# إشعار بإنشاء فاتورة
notify_invoice_created(invoice, invoice_type="sale")

# إشعار بالشحن
notify_invoice_shipped(invoice)

# إشعار بالتوصيل
notify_invoice_delivered(invoice)

# إشعار بالإلغاء
notify_invoice_cancelled(invoice, reason="المنتج غير متوفر")
```

---

## 2. الاستخدام من Views

### مثال 1: عند إنشاء فاتورة في View

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from invoices.models import SaleInvoice
from invoices.notifications import notify_invoice_created

class InvoiceCreateAPIView(APIView):
    def post(self, request):
        # إنشاء الفاتورة
        invoice = SaleInvoice.objects.create(
            user=request.user,
            items_count=request.data.get('items_count'),
            total_quantity=request.data.get('total_quantity'),
            total_price=request.data.get('total_price'),
        )
        
        # إرسال إشعار
        notify_invoice_created(invoice, invoice_type="sale")
        
        return Response({
            "success": True,
            "invoice_id": invoice.pk,
            "message": "تم إنشاء الطلب وإرسال الإشعار بنجاح"
        }, status=status.HTTP_201_CREATED)
```

### مثال 2: عند تحديث حالة الفاتورة

```python
from rest_framework.views import APIView
from invoices.models import SaleInvoice
from invoices.notifications import notify_invoice_status_changed

class InvoiceUpdateStatusAPIView(APIView):
    def patch(self, request, pk):
        invoice = SaleInvoice.objects.get(pk=pk)
        old_status = invoice.status
        new_status = request.data.get('status')
        
        # تحديث الحالة
        invoice.status = new_status
        invoice.save()
        
        # إرسال إشعار بالتغيير
        notify_invoice_status_changed(
            invoice=invoice,
            old_status=old_status,
            new_status=new_status,
            invoice_type="sale"
        )
        
        return Response({
            "success": True,
            "message": "تم تحديث حالة الطلب وإرسال الإشعار"
        })
```

### مثال 3: إشعار مخصص

```python
from notifications.models import Notification

class CustomNotificationView(APIView):
    def post(self, request):
        # إرسال إشعار مخصص
        notification = Notification.objects.create(
            user=request.user,
            title="🎉 عرض خاص",
            message="خصم 30% على جميع المنتجات!",
            extra={
                "discount_percentage": 30,
                "valid_until": "2025-12-31",
                "promo_code": "WINTER30"
            },
            image_url="https://example.com/promo.jpg"
        )
        
        return Response({
            "success": True,
            "notification_id": notification.pk
        })
```

---

## 3. الاستخدام من API

### مثال: إرسال إشعار من API Endpoint

```python
# في views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from core.responses import APIResponse

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_custom_notification(request):
    """
    إرسال إشعار مخصص للمستخدم الحالي.
    """
    notification = Notification.objects.create(
        user=request.user,
        title=request.data.get('title'),
        message=request.data.get('message'),
        extra=request.data.get('extra', {}),
        image_url=request.data.get('image_url', '')
    )
    
    return APIResponse.created(
        data={"notification_id": notification.pk},
        message="تم إرسال الإشعار بنجاح"
    )
```

**استخدام API:**
```bash
curl -X POST http://localhost:8000/api/send-notification/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "إشعار تجريبي",
       "message": "هذا إشعار تجريبي للاختبار",
       "extra": {"type": "test"}
     }'
```

---

## 4. الاستخدام مع Celery Tasks

### إرسال إشعارات بشكل غير متزامن

```python
from notifications.tasks import (
    send_notification_to_user,
    send_notification_to_topic,
    send_bulk_notifications
)

# إرسال إشعار لمستخدم واحد (Async)
send_notification_to_user.delay(
    user_id=123,
    title="إشعار مهم",
    message="لديك رسالة جديدة",
    extra={"type": "message", "message_id": 456}
)

# إرسال إشعار لجميع مشتركي موضوع (Async)
send_notification_to_topic.delay(
    topic_id=1,  # موضوع "عروض وخصومات"
    title="🎉 عرض جديد",
    message="خصم 50% على جميع المنتجات اليوم فقط!"
)

# إرسال إشعار جماعي (Async)
user_ids = [1, 2, 3, 4, 5]
send_bulk_notifications.delay(
    user_ids=user_ids,
    title="تحديث النظام",
    message="سيتم إجراء صيانة للنظام يوم الجمعة"
)
```

### مثال في View مع Celery:

```python
from invoices.notifications import send_invoice_notification_async

class BulkInvoiceCreateView(APIView):
    def post(self, request):
        # إنشاء عدة فواتير
        invoices = []
        for invoice_data in request.data.get('invoices', []):
            invoice = SaleInvoice.objects.create(**invoice_data)
            invoices.append(invoice)
            
            # إرسال إشعار async (لا ينتظر)
            send_invoice_notification_async(
                user_id=invoice.user.id,
                title="طلب جديد",
                message=f"تم إنشاء طلبك رقم #{invoice.pk}",
                invoice_id=invoice.pk
            )
        
        return Response({
            "success": True,
            "created_count": len(invoices)
        })
```

---

## 5. الاستخدام من Django Shell

### اختبار سريع من Shell:

```bash
python manage.py shell
```

```python
from notifications.models import Notification, Topic, TopicSubscription
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. إنشاء موضوع
topic = Topic.objects.create(
    name="عروض اليوم",
    description="عروض وخصومات يومية"
)

# 2. اشتراك مستخدم في الموضوع
user = User.objects.get(id=1)
subscription = TopicSubscription.objects.create(
    user=user,
    topic=topic,
    is_active=True
)

# 3. إرسال إشعار فردي
notification = Notification.objects.create(
    user=user,
    title="مرحباً! 👋",
    message="هذا إشعار تجريبي",
    extra={"test": True}
)

# 4. إرسال إشعار لجميع مشتركي الموضوع
subscribers = TopicSubscription.objects.filter(topic=topic, is_active=True)
for sub in subscribers:
    Notification.objects.create(
        user=sub.user,
        topic=topic,
        title="عرض جديد!",
        message="خصم 30% على جميع المنتجات"
    )

# 5. جلب إشعارات المستخدم
my_notifications = Notification.objects.filter(user=user)
print(f"عدد الإشعارات: {my_notifications.count()}")

# 6. تحديد كمقروء
notification.is_read = True
notification.save()
```

---

## 6. أمثلة متقدمة

### إشعارات مشروطة

```python
from notifications.models import Notification

def send_conditional_notification(user, condition):
    """إرسال إشعار بناءً على شرط معين."""
    
    if condition == "low_balance":
        Notification.objects.create(
            user=user,
            title="⚠️ تنبيه: رصيد منخفض",
            message="رصيدك أقل من 100 جنيه. يرجى الشحن.",
            extra={"type": "balance_alert"}
        )
    
    elif condition == "order_delayed":
        Notification.objects.create(
            user=user,
            title="⏰ تأخير في الطلب",
            message="عذراً، تأخر طلبك بسبب ظروف خارجة عن إرادتنا",
            extra={"type": "delay_alert"}
        )
```

### إشعارات دورية (Scheduled)

```python
# في celery.py
from celery import shared_task
from celery.schedules import crontab

@shared_task
def send_daily_summary():
    """إرسال ملخص يومي لجميع المستخدمين."""
    from notifications.models import Notification
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    users = User.objects.filter(role='PHARMACY')
    
    for user in users:
        # حساب إحصائيات اليوم
        today_orders = user.sale_invoices.filter(
            created_at__date=timezone.now().date()
        ).count()
        
        Notification.objects.create(
            user=user,
            title="📊 ملخص اليوم",
            message=f"لديك {today_orders} طلب جديد اليوم",
            extra={"type": "daily_summary", "orders": today_orders}
        )

# جدولة المهمة
app.conf.beat_schedule = {
    'send-daily-summary': {
        'task': 'send_daily_summary',
        'schedule': crontab(hour=20, minute=0),  # كل يوم الساعة 8 مساءً
    },
}
```

---

## 7. Best Practices

### ✅ DO (افعل):
- استخدم Signals للإشعارات التلقائية
- استخدم Celery للإشعارات الجماعية
- أضف `extra` data مفيدة في الإشعارات
- استخدم emojis في العناوين لجذب الانتباه
- احفظ `image_url` للإشعارات المهمة

### ❌ DON'T (لا تفعل):
- لا ترسل إشعارات كثيرة للمستخدم (spam)
- لا تنسى handle الأخطاء
- لا تحط معلومات حساسة في الإشعارات
- لا تستخدم Signals للعمليات الطويلة (استخدم Celery)

---

## 🎯 ملخص سريع

```python
# 1. إشعار بسيط
Notification.objects.create(user=user, title="عنوان", message="محتوى")

# 2. إشعار مع بيانات إضافية
Notification.objects.create(
    user=user,
    title="عنوان",
    message="محتوى",
    extra={"key": "value"}
)

# 3. إشعار لموضوع (جميع المشتركين)
from invoices.notifications import send_invoice_notification
send_invoice_notification(user, "عنوان", "محتوى", invoice_id=123)

# 4. إشعار async
from notifications.tasks import send_notification_to_user
send_notification_to_user.delay(user.id, "عنوان", "محتوى")
```

---

**لأي استفسارات، راجع `/notifications/README.md` 📚**

