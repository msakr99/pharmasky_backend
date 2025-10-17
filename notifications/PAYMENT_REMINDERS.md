# ⏰ نظام تذكيرات مواعيد التحصيل

نظام ذكي لإرسال تذكيرات الدفع قبل موعد التحصيل بناءً على إعدادات كل صيدلية.

---

## 📋 جدول المحتويات

1. [كيف يعمل النظام](#كيف-يعمل-النظام)
2. [إعدادات Payment Period](#إعدادات-payment-period)
3. [أنواع التذكيرات](#أنواع-التذكيرات)
4. [أمثلة عملية](#أمثلة-عملية)
5. [الجدولة التلقائية](#الجدولة-التلقائية)

---

## 🎯 كيف يعمل النظام

### المفهوم

```
آخر فاتورة → فترة السداد → موعد التحصيل
     ↓              ↓               ↓
  01/10/2025    30 يوم        31/10/2025
                    ↓
            تذكير قبل 3 أيام
                    ↓
              28/10/2025 ✉️
```

### الآلية

1. **لكل صيدلية** لها `payment_period` مختلف
2. **كل payment_period** له `reminder_days_before` مختلف
3. **Celery Beat** يشتغل يومياً ويفحص الصيدليات
4. **إذا اليوم = تاريخ التذكير** → إرسال إشعار
5. **إذا متأخر عن الموعد** → إرسال تنبيه (كل 7 أيام)

---

## ⚙️ إعدادات Payment Period

### إضافة حقل جديد

تم إضافة حقل `reminder_days_before` لموديل `PaymentPeriod`:

```python
class PaymentPeriod(models.Model):
    name = models.CharField(max_length=255)
    period_in_days = models.PositiveIntegerField()
    addition_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    reminder_days_before = models.PositiveIntegerField(
        default=3,
        help_text="عدد الأيام قبل موعد التحصيل لإرسال تذكير"
    )
```

### أمثلة إعدادات

| Payment Period | المدة | نسبة الإضافة | تذكير قبل | الاستخدام |
|---------------|-------|--------------|-----------|-----------|
| نقداً | 0 يوم | 0% | 0 يوم | دفع فوري |
| أسبوع | 7 أيام | 0.5% | 2 يوم | صيدليات صغيرة |
| 15 يوم | 15 يوم | 1% | 3 أيام | صيدليات متوسطة |
| شهر | 30 يوم | 2% | 5 أيام | صيدليات كبيرة |
| شهرين | 60 يوم | 4% | 7 أيام | عملاء VIP |

### إنشاء Payment Periods من Admin

```python
# من Django Admin أو Shell
from profiles.models import PaymentPeriod

# فترة أسبوع - تذكير قبل يومين
PaymentPeriod.objects.create(
    name="أسبوع",
    period_in_days=7,
    addition_percentage=0.5,
    reminder_days_before=2  # ⭐
)

# فترة شهر - تذكير قبل 5 أيام
PaymentPeriod.objects.create(
    name="شهر",
    period_in_days=30,
    addition_percentage=2.0,
    reminder_days_before=5  # ⭐
)

# فترة شهرين - تذكير قبل أسبوع
PaymentPeriod.objects.create(
    name="شهرين",
    period_in_days=60,
    addition_percentage=4.0,
    reminder_days_before=7  # ⭐
)
```

---

## 🔔 أنواع التذكيرات

### 1. تذكير قبل الموعد ⏰

يُرسل **مرة واحدة** قبل موعد التحصيل بالمدة المحددة:

```
⏰ تذكير: موعد التحصيل قريب

لديك رصيد مستحق بقيمة 15,000 جنيه.
موعد التحصيل بعد 5 أيام (31/10/2025).
يرجى السداد في الموعد المحدد لتجنب أي رسوم تأخير.
```

**Extra Data:**
```json
{
  "type": "payment_due_reminder",
  "outstanding_balance": "15000.00",
  "due_date": "2025-10-31",
  "days_until_due": 5,
  "payment_period": "شهر"
}
```

---

### 2. تنبيه الدفعات المتأخرة ⚠️

يُرسل **كل 7 أيام** بعد تجاوز موعد التحصيل:

```
⚠️ تنبيه: دفعة متأخرة

لديك رصيد متأخر بقيمة 15,000 جنيه.
تأخر الدفع 14 يوم.
يرجى السداد فوراً لتجنب رسوم التأخير الإضافية.
```

**Extra Data:**
```json
{
  "type": "payment_overdue",
  "outstanding_balance": "15000.00",
  "due_date": "2025-10-31",
  "days_overdue": 14,
  "payment_period": "شهر"
}
```

---

## 📱 أمثلة عملية

### مثال 1: صيدلية بفترة أسبوع

```python
from profiles.models import PaymentPeriod, UserProfile
from django.utils import timezone

# Payment Period: أسبوع (تذكير قبل يومين)
period = PaymentPeriod.objects.get(name="أسبوع")
print(f"المدة: {period.period_in_days} يوم")
print(f"تذكير قبل: {period.reminder_days_before} يوم")

# صيدلية معها الفترة دي
pharmacy = User.objects.get(id=123)
profile = pharmacy.profile
profile.payment_period = period
profile.save()

# صيدلية تعمل طلب يوم 1 أكتوبر
invoice = SaleInvoice.objects.create(
    user=pharmacy,
    total_price=5000.00,
    status='PLACED'
)

# تحديث آخر فاتورة
profile.latest_invoice_date = timezone.now()
profile.save()

# الحسابات:
# آخر فاتورة: 01/10/2025
# فترة السداد: 7 أيام
# موعد التحصيل: 08/10/2025
# تذكير قبل: 2 يوم
# تاريخ التذكير: 06/10/2025

# ✨ يوم 06/10/2025 الساعة 9 صباحاً:
# "⏰ تذكير: موعد التحصيل قريب"
# "لديك رصيد مستحق بقيمة 5000 جنيه. موعد التحصيل بعد 2 أيام (08/10/2025)"
```

---

### مثال 2: صيدلية بفترة شهر

```python
# Payment Period: شهر (تذكير قبل 5 أيام)
period = PaymentPeriod.objects.get(name="شهر")

pharmacy.profile.payment_period = period
pharmacy.profile.save()

# آخر فاتورة: 01/10/2025
# فترة السداد: 30 يوم
# موعد التحصيل: 31/10/2025
# تذكير قبل: 5 أيام
# تاريخ التذكير: 26/10/2025

# ✨ يوم 26/10/2025 الساعة 9 صباحاً:
# "⏰ تذكير: موعد التحصيل قريب"
# "لديك رصيد مستحق بقيمة 20000 جنيه. موعد التحصيل بعد 5 أيام (31/10/2025)"
```

---

### مثال 3: دفعة متأخرة

```python
# الصيدلية لم تدفع في الموعد المحدد

# موعد التحصيل كان: 31/10/2025
# اليوم: 07/11/2025 (متأخر 7 أيام)

# ✨ يوم 07/11/2025 الساعة 9 صباحاً:
# "⚠️ تنبيه: دفعة متأخرة"
# "لديك رصيد متأخر بقيمة 20000 جنيه. تأخر الدفع 7 يوم"

# ✨ يوم 14/11/2025 (متأخر 14 يوم):
# "⚠️ تنبيه: دفعة متأخرة"
# "لديك رصيد متأخر بقيمة 20000 جنيه. تأخر الدفع 14 يوم"

# وهكذا كل 7 أيام...
```

---

## 📊 الجدولة التلقائية

### Celery Beat Schedule

تم إضافة جدولة تلقائية في `project/celery.py`:

```python
app.conf.beat_schedule = {
    # تذكيرات الدفع يومياً
    'send-payment-due-reminders': {
        'task': 'notifications.tasks.send_payment_due_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9:00 صباحاً
    },
    
    # حذف الإشعارات القديمة أسبوعياً
    'delete-old-notifications': {
        'task': 'notifications.tasks.delete_old_read_notifications',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # الأحد 2:00 صباحاً
        'args': (30,)  # حذف الأقدم من 30 يوم
    },
}
```

### تخصيص المواعيد

يمكنك تغيير المواعيد:

```python
# كل ساعة
'schedule': crontab(minute=0)

# كل يوم الساعة 8 صباحاً
'schedule': crontab(hour=8, minute=0)

# كل يوم الساعة 9 صباحاً و 5 مساءً
'schedule': crontab(hour='9,17', minute=0)

# كل اثنين وخميس الساعة 10 صباحاً
'schedule': crontab(hour=10, minute=0, day_of_week='1,4')

# أول يوم في كل شهر
'schedule': crontab(hour=9, minute=0, day_of_month=1)
```

---

## 🧪 الاختبار

### 1. اختبار يدوي:

```bash
# من Terminal
docker exec -it pharmasky_web python manage.py shell
```

```python
from notifications.tasks import send_payment_due_reminders

# تشغيل المهمة يدوياً
result = send_payment_due_reminders()
print(result)
# {'success': True, 'notifications_sent': 5, 'pharmacies_checked': 120}
```

### 2. اختبار Celery Task:

```bash
# من Terminal
docker exec -it pharmasky_web python manage.py shell
```

```python
from notifications.tasks import send_payment_due_reminders

# تشغيل async
task = send_payment_due_reminders.delay()
print(f"Task ID: {task.id}")

# انتظر النتيجة
result = task.get()
print(result)
```

### 3. عمل Migration:

```bash
# إنشاء migration لحقل reminder_days_before
docker exec -it pharmasky_web python manage.py makemigrations profiles

# تطبيق Migration
docker exec -it pharmasky_web python manage.py migrate profiles
```

### 4. إنشاء Payment Periods:

```bash
docker exec -it pharmasky_web python manage.py shell
```

```python
from profiles.models import PaymentPeriod

# حذف القديم (اختياري)
PaymentPeriod.objects.all().delete()

# إنشاء فترات جديدة مع التذكيرات
periods = [
    {"name": "نقداً", "period_in_days": 0, "addition_percentage": 0, "reminder_days_before": 0},
    {"name": "أسبوع", "period_in_days": 7, "addition_percentage": 0.5, "reminder_days_before": 2},
    {"name": "15 يوم", "period_in_days": 15, "addition_percentage": 1.0, "reminder_days_before": 3},
    {"name": "شهر", "period_in_days": 30, "addition_percentage": 2.0, "reminder_days_before": 5},
    {"name": "45 يوم", "period_in_days": 45, "addition_percentage": 3.0, "reminder_days_before": 7},
    {"name": "شهرين", "period_in_days": 60, "addition_percentage": 4.0, "reminder_days_before": 10},
]

for period_data in periods:
    period, created = PaymentPeriod.objects.get_or_create(
        name=period_data["name"],
        defaults=period_data
    )
    if created:
        print(f"✓ تم إنشاء: {period.name} (تذكير قبل {period.reminder_days_before} يوم)")
    else:
        # تحديث
        period.reminder_days_before = period_data["reminder_days_before"]
        period.save()
        print(f"○ تم تحديث: {period.name}")

print(f"\n✅ إجمالي الفترات: {PaymentPeriod.objects.count()}")
```

---

## 🎯 أمثلة عملية

### سيناريو 1: صيدلية بفترة شهر

```python
from django.utils import timezone
from datetime import timedelta

# إعدادات الصيدلية
pharmacy = User.objects.get(id=123)
profile = pharmacy.profile
payment_period = profile.payment_period

print(f"اسم الصيدلية: {pharmacy.name}")
print(f"فترة الدفع: {payment_period.name}")
print(f"المدة: {payment_period.period_in_days} يوم")
print(f"تذكير قبل: {payment_period.reminder_days_before} يوم")

# آخر فاتورة
last_invoice_date = profile.latest_invoice_date
print(f"آخر فاتورة: {last_invoice_date.date()}")

# حساب موعد التحصيل
due_date = last_invoice_date.date() + timedelta(days=payment_period.period_in_days)
print(f"موعد التحصيل: {due_date}")

# حساب تاريخ التذكير
reminder_date = due_date - timedelta(days=payment_period.reminder_days_before)
print(f"تاريخ التذكير: {reminder_date}")

# الرصيد المستحق
account = pharmacy.account
outstanding = abs(account.balance)
print(f"الرصيد المستحق: {outstanding} جنيه")
```

**Output:**
```
اسم الصيدلية: صيدلية النور
فترة الدفع: شهر
المدة: 30 يوم
تذكير قبل: 5 يوم
آخر فاتورة: 2025-10-01
موعد التحصيل: 2025-10-31
تاريخ التذكير: 2025-10-26
الرصيد المستحق: 15000.0 جنيه
```

---

### سيناريو 2: صيدليات مختلفة بفترات مختلفة

```python
from profiles.models import PaymentPeriod

# 3 صيدليات بفترات مختلفة
pharmacies_data = [
    {"name": "صيدلية الأمل", "period": "أسبوع"},     # تذكير قبل 2 يوم
    {"name": "صيدلية النور", "period": "شهر"},       # تذكير قبل 5 أيام
    {"name": "صيدلية السلام", "period": "شهرين"},    # تذكير قبل 10 أيام
]

for data in pharmacies_data:
    pharmacy = User.objects.filter(name=data["name"]).first()
    if pharmacy and pharmacy.profile:
        period = PaymentPeriod.objects.get(name=data["period"])
        pharmacy.profile.payment_period = period
        pharmacy.profile.save()
        
        print(f"✓ {pharmacy.name}: تذكير قبل {period.reminder_days_before} يوم")
```

**النتيجة:**
- صيدلية الأمل → تذكير قبل يومين
- صيدلية النور → تذكير قبل 5 أيام
- صيدلية السلام → تذكير قبل 10 أيام

---

### سيناريو 3: تشغيل Task يدوياً

```python
from notifications.tasks import send_payment_due_reminders

# تشغيل المهمة يدوياً للاختبار
result = send_payment_due_reminders()

print(f"✓ نجحت: {result['success']}")
print(f"✓ إشعارات مُرسلة: {result['notifications_sent']}")
print(f"✓ صيدليات تم فحصها: {result['pharmacies_checked']}")
```

---

## ⚙️ التخصيص المتقدم

### تخصيص الرسالة حسب الرصيد

```python
# في notifications/tasks.py
# يمكنك تعديل الرسالة بناءً على المبلغ

if outstanding_amount < 1000:
    title = "⏰ تذكير بسيط"
    emoji = "💙"
elif outstanding_amount < 10000:
    title = "⏰ تذكير: موعد التحصيل قريب"
    emoji = "💛"
else:
    title = "⏰ تذكير مهم: موعد التحصيل قريب"
    emoji = "🔴"
```

### إرسال إشعارات إضافية للـ Admin

```python
# إذا كانت الدفعة المتأخرة كبيرة (> 50,000)
if outstanding_amount > 50000 and days_overdue > 14:
    # إشعار للـ Admin
    admins = User.objects.filter(role='ADMIN')
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title="⚠️ تنبيه: دفعة كبيرة متأخرة",
            message=f"{pharmacy.name} لديها رصيد متأخر {outstanding_amount} جنيه ({days_overdue} يوم)",
            extra={
                "type": "large_overdue_alert",
                "pharmacy_id": pharmacy.pk,
                "amount": str(outstanding_amount),
                "days_overdue": days_overdue
            }
        )
```

---

## 📊 Admin Panel

### في Django Admin

بعد Migration، في صفحة Payment Period:

```
+--------+------------+------------------+---------------------+
| Name   | Period     | Addition %       | Reminder Days Before|
+--------+------------+------------------+---------------------+
| نقداً  | 0 days     | 0.00%           | 0 days              |
| أسبوع | 7 days     | 0.50%           | 2 days              |
| 15 يوم | 15 days    | 1.00%           | 3 days              |
| شهر    | 30 days    | 2.00%           | 5 days              |
| شهرين  | 60 days    | 4.00%           | 10 days             |
+--------+------------+------------------+---------------------+
```

يمكنك تعديل `Reminder Days Before` لكل فترة من Admin Panel.

---

## 🔧 التشغيل والصيانة

### التحقق من Celery Beat

```bash
# شوف logs
docker logs pharmasky_celery_beat -f

# يجب أن تشوف:
# "Scheduler: Running Task send-payment-due-reminders"
```

### تشغيل يدوي للاختبار

```bash
# تشغيل Task مرة واحدة
docker exec -it pharmasky_celery celery -A project call notifications.tasks.send_payment_due_reminders
```

### مراقبة النتائج

```bash
# عدد التذكيرات المُرسلة
docker exec -it pharmasky_web python manage.py shell
```

```python
from notifications.models import Notification
from django.utils import timezone

# التذكيرات المُرسلة اليوم
today = timezone.now().date()
reminders_today = Notification.objects.filter(
    extra__type='payment_due_reminder',
    created_at__date=today
).count()

print(f"تذكيرات اليوم: {reminders_today}")

# التنبيهات المتأخرة
overdue_today = Notification.objects.filter(
    extra__type='payment_overdue',
    created_at__date=today
).count()

print(f"تنبيهات التأخير اليوم: {overdue_today}")
```

---

## 📝 Migration Required

### 1. إنشاء Migration:

```bash
docker exec -it pharmasky_web python manage.py makemigrations profiles
```

### 2. تطبيق Migration:

```bash
docker exec -it pharmasky_web python manage.py migrate profiles
```

### 3. تحديث Payment Periods الموجودة:

```bash
docker exec -it pharmasky_web python manage.py shell
```

```python
from profiles.models import PaymentPeriod

# تحديث جميع الفترات الموجودة
periods = PaymentPeriod.objects.all()

for period in periods:
    # تعيين قيم افتراضية بناءً على المدة
    if period.period_in_days <= 7:
        period.reminder_days_before = 2
    elif period.period_in_days <= 15:
        period.reminder_days_before = 3
    elif period.period_in_days <= 30:
        period.reminder_days_before = 5
    elif period.period_in_days <= 45:
        period.reminder_days_before = 7
    else:
        period.reminder_days_before = 10
    
    period.save()
    print(f"✓ {period.name}: تذكير قبل {period.reminder_days_before} يوم")
```

---

## 📚 API Usage

### جلب Payment Periods مع التذكيرات:

```bash
curl http://localhost:8000/profiles/payment-periods/ \
     -H "Authorization: Token YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "name": "شهر",
        "period_in_days": 30,
        "addition_percentage": "2.00",
        "reminder_days_before": 5
      }
    ]
  }
}
```

---

## ✅ الخلاصة

### ميزات النظام:

✅ **تذكيرات مخصصة** - كل payment period له مدة تذكير مختلفة  
✅ **تلقائي بالكامل** - Celery Beat يشتغل يومياً الساعة 9 صباحاً  
✅ **تنبيهات التأخير** - كل 7 أيام بعد الموعد  
✅ **معلومات تفصيلية** - الرصيد، الموعد، عدد الأيام  
✅ **مرن** - سهل التخصيص والتعديل  

### الخطوات التالية:

1. ✅ عمل migration للحقل الجديد
2. ✅ تحديث Payment Periods الموجودة
3. ✅ اختبار Task يدوياً
4. ✅ التأكد من Celery Beat شغال
5. ✅ مراقبة الإشعارات

**النظام جاهز للتشغيل! 🚀**

