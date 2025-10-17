# 👨‍💼✨ إشعارات الـ Admin و Wishlist

دليل شامل لإشعارات الـ Admin وإشعارات توفر المنتجات من Wishlist.

---

## 📋 جدول المحتويات

1. [إشعارات الـ Admin](#إشعارات-الـ-admin)
2. [إشعارات Wishlist](#إشعارات-wishlist)
3. [أمثلة عملية](#أمثلة-عملية)
4. [ملخص كامل](#ملخص-كامل)

---

## 👨‍💼 إشعارات الـ Admin

الـ Admin والـ Manager يستلموا إشعارات تلقائية عن جميع الأحداث المهمة في النظام.

### 1. تسجيل صيدلية جديدة 🏪

```python
from accounts.models import User, Pharmacy

# تسجيل صيدلية جديدة
pharmacy = User.objects.create(
    username="+201234567890",
    name="صيدلية النور",
    role='PHARMACY',
    is_active=True
)

# ✨ إشعار تلقائي لجميع الـ Admins:
# "🏪 تسجيل صيدلية جديدة"
# "تم تسجيل صيدلية جديدة: صيدلية النور (+201234567890)"
```

**معلومات الإشعار:**
- العنوان: "🏪 تسجيل صيدلية جديدة"
- المحتوى: اسم الصيدلية ورقم الهاتف
- Extra Data: 
  - `pharmacy_id`: ID الصيدلية
  - `pharmacy_name`: اسم الصيدلية
  - `pharmacy_username`: رقم الهاتف
  - `area`: المنطقة

---

### 2. فاتورة شراء جديدة 📦

```python
from invoices.models import PurchaseInvoice

# إنشاء فاتورة شراء
invoice = PurchaseInvoice.objects.create(
    user=store_user,
    items_count=20,
    total_quantity=100,
    total_price=15000.00,
    status='PLACED'
)

# ✨ إشعار تلقائي لجميع الـ Admins:
# "📦 فاتورة شراء جديدة"
# "فاتورة شراء جديدة #123 من مخزن الأمل بقيمة 15000 جنيه"
```

**معلومات الإشعار:**
- Extra Data:
  - `invoice_id`: رقم الفاتورة
  - `user_id`: ID المخزن
  - `user_name`: اسم المخزن
  - `total_price`: إجمالي السعر
  - `items_count`: عدد الأصناف

---

### 3. فاتورة بيع جديدة (طلب صيدلية) 🛒

```python
from invoices.models import SaleInvoice

# صيدلية تعمل طلب
invoice = SaleInvoice.objects.create(
    user=pharmacy_user,
    items_count=15,
    total_quantity=50,
    total_price=7500.00,
    status='PLACED'
)

# ✨ إشعار تلقائي لجميع الـ Admins:
# "🛒 طلب جديد"
# "طلب جديد #456 من صيدلية النور بقيمة 7500 جنيه"
```

---

### 4. عملية دفع 💰

#### دفعة شراء (من المخزن):
```python
from finance.models import PurchasePayment

payment = PurchasePayment.objects.create(
    user=store_user,
    method='BANK',
    amount=10000.00,
    at=timezone.now()
)

# Admin يستلم نسخة من الإشعار
```

#### دفعة بيع (من الصيدلية):
```python
from finance.models import SalePayment

payment = SalePayment.objects.create(
    user=pharmacy_user,
    method='CASH',
    amount=5000.00,
    at=timezone.now()
)

# Admin يستلم نسخة من الإشعار
```

---

### 5. مرتجعات 📦↩️

```python
from invoices.models import SaleReturnInvoice

# صيدلية ترجع منتجات
return_inv = SaleReturnInvoice.objects.create(
    user=pharmacy_user,
    items_count=3,
    total_quantity=10,
    total_price=1200.00,
    status='PLACED'
)

# Admin يستلم نسخة من الإشعار
```

---

### 6. شكوى جديدة 📢

```python
from profiles.models import Complaint

# صيدلية تقدم شكوى
complaint = Complaint.objects.create(
    user=pharmacy_user,
    subject="مشكلة في التوصيل",
    body="الطلب تأخر 3 أيام بدون سبب واضح",
    mark_as_solved=False
)

# ✨ إشعار تلقائي لجميع الـ Admins:
# "📢 شكوى جديدة"
# "شكوى جديدة من صيدلية النور: مشكلة في التوصيل"
```

**معلومات الإشعار:**
- Extra Data:
  - `complaint_id`: رقم الشكوى
  - `user_id`: ID المستخدم
  - `user_name`: اسم المستخدم
  - `subject`: موضوع الشكوى
  - `body`: محتوى الشكوى

---

### 7. حل الشكوى ✅

```python
# Admin يحل الشكوى
complaint.mark_as_solved = True
complaint.save()

# ✨ إشعار تلقائي للمستخدم صاحب الشكوى:
# "✅ تم حل شكواك"
# "تم حل شكواك: مشكلة في التوصيل. شكراً لتواصلك معنا."
```

---

## ✨ إشعارات Wishlist

عند إضافة صيدلية لمنتج في الـ wishlist، تستلم إشعار تلقائي عند توفر عرض لهذا المنتج.

### كيف يعمل؟

```python
from market.models import PharmacyProductWishList, Product

# 1. الصيدلية تضيف منتج للـ wishlist
product = Product.objects.get(id=123)
PharmacyProductWishList.objects.create(
    pharmacy=pharmacy_user,
    product=product
)

# 2. مخزن يضيف عرض للمنتج
from offers.models import Offer

offer = Offer.objects.create(
    product=product,
    user=store_user,
    available_amount=100,
    remaining_amount=100,
    purchase_discount_percentage=25.00,
    selling_discount_percentage=20.00,
    selling_price=80.00,
    purchase_price=75.00
)

# ✨ إشعار تلقائي للصيدلية:
# "✨ منتج متوفر من قائمة الرغبات!"
# "المنتج 'باراسيتامول 500 مجم' أصبح متوفراً الآن بخصم 20% وسعر 80 جنيه"
```

### معلومات الإشعار:

```json
{
  "type": "wishlist_product_available",
  "product_id": 123,
  "product_name": "باراسيتامول 500 مجم",
  "offer_id": 789,
  "seller_id": 45,
  "seller_name": "مخزن الأمل",
  "discount": "20.00",
  "price": "80.00",
  "available_amount": 100
}
```

---

## 🎯 أمثلة عملية

### مثال 1: سيناريو كامل للصيدلية

```python
from market.models import PharmacyProductWishList, Product
from offers.models import Offer

# صيدلية تدور على منتج
product = Product.objects.get(name__icontains="أموكسيسيلين")

# المنتج مش متوفر، تضيفه للـ wishlist
wishlist_item = PharmacyProductWishList.objects.create(
    pharmacy=pharmacy_user,
    product=product
)

print(f"✓ تم إضافة {product.name} لقائمة الرغبات")

# بعد يومين... مخزن يضيف عرض للمنتج
offer = Offer.objects.create(
    product=product,
    user=store_user,
    available_amount=200,
    remaining_amount=200,
    selling_discount_percentage=22.00,
    selling_price=85.00,
    purchase_discount_percentage=25.00,
    purchase_price=80.00
)

# ✨ الصيدلية تستلم إشعار فوري:
# "✨ منتج متوفر من قائمة الرغبات!"
# "المنتج 'أموكسيسيلين 250 مجم' أصبح متوفراً الآن بخصم 22% وسعر 85 جنيه"
```

### مثال 2: Admin يتابع النشاطات

```python
# في يوم واحد، الـ Admin يستلم:

# 1. صباحاً: تسجيل 3 صيدليات جديدة
# "🏪 تسجيل صيدلية جديدة" (x3)

# 2. ظهراً: 15 طلب جديد من صيدليات
# "🛒 طلب جديد" (x15)

# 3. عصراً: 5 دفعات من صيدليات
# "💰 دفعة جديدة" (x5)

# 4. مساءً: 2 شكاوي
# "📢 شكوى جديدة" (x2)

# 5. ليلاً: مرتجع واحد
# "↩️ طلب إرجاع جديد" (x1)

# Total: 26 إشعار في يوم واحد
```

---

## 📊 ملخص كامل لجميع الإشعارات

### للصيدلية 💊

| الحدث | الإشعار | التلقائي |
|------|---------|----------|
| طلب جديد | 🛒 طلب جديد تم إنشاؤه | ✅ |
| تحديث حالة الطلب | 🔔 تحديث حالة الطلب | ✅ |
| دفعة تم تسجيلها | ✅ تم تسجيل دفعتك | ✅ |
| مرتجع تم إنشاؤه | ↩️ طلب إرجاع تم إنشاؤه | ✅ |
| موافقة على المرتجع | ✅ تمت الموافقة | ✅ |
| رفض المرتجع | ❌ تم رفض الإرجاع | ✅ |
| اكتمال المرتجع | ✅ تم إكمال الإرجاع | ✅ |
| حل الشكوى | ✅ تم حل شكواك | ✅ |
| **منتج من Wishlist متوفر** | **✨ منتج متوفر!** | **✅** |

### للمخزن 🏪

| الحدث | الإشعار | التلقائي |
|------|---------|----------|
| فاتورة شراء جديدة | 📦 فاتورة شراء جديدة | ✅ |
| تحديث حالة فاتورة الشراء | 🔔 تحديث حالة الطلب | ✅ |
| دفعة شراء | 💰 دفعة شراء جديدة | ✅ |
| مرتجع شراء | ↩️ مرتجع شراء جديد | ✅ |

### للـ Admin 👨‍💼

| الحدث | الإشعار | التلقائي |
|------|---------|----------|
| **تسجيل صيدلية جديدة** | **🏪 تسجيل صيدلية جديدة** | **✅** |
| **فاتورة شراء** | **📦 فاتورة شراء جديدة** | **✅** |
| **فاتورة بيع (طلب)** | **🛒 طلب جديد** | **✅** |
| **شكوى جديدة** | **📢 شكوى جديدة** | **✅** |
| دفعة شراء | 💰 دفعة شراء جديدة | ✅ |
| دفعة بيع | ✅ تم تسجيل دفعة | ✅ |
| مرتجع شراء | ↩️ مرتجع شراء جديد | ✅ |
| مرتجع بيع | ↩️ طلب إرجاع جديد | ✅ |

---

## 🔧 التخصيص

### تعطيل إشعارات معينة

يمكنك تعطيل أي signal بتعديل الملف المناسب:

```python
# في offers/signals.py
# علق أو احذف الـ @receiver decorator

# @receiver(post_save, sender=Offer)  # علق هذا السطر
def notify_wishlist_pharmacies_on_offer_created(sender, instance, created, **kwargs):
    # ...
```

### إضافة مستقبلين إضافيين

```python
# في أي signals.py
from notifications.models import Notification

def send_to_specific_users(event_data):
    """إرسال إشعارات لمستخدمين محددين."""
    users = User.objects.filter(role='SALES')  # مثال
    
    notifications = []
    for user in users:
        notifications.append(
            Notification(
                user=user,
                title="إشعار مخصص",
                message="محتوى الإشعار",
                extra=event_data
            )
        )
    
    Notification.objects.bulk_create(notifications)
```

---

## 📱 استعلام الإشعارات من API

### جلب إشعارات Admin:

```bash
# إشعارات Admin فقط
curl http://localhost:8000/notifications/notifications/?extra__type__contains=admin \
     -H "Authorization: Token ADMIN_TOKEN"
```

### جلب إشعارات Wishlist:

```bash
# إشعارات Wishlist فقط
curl http://localhost:8000/notifications/notifications/?extra__type=wishlist_product_available \
     -H "Authorization: Token PHARMACY_TOKEN"
```

---

## ✅ الخلاصة

### التلقائي (Automatic)
✅ **تسجيل صيدلية** → إشعار للـ Admin  
✅ **فواتير** → إشعار للـ Admin والمستخدم  
✅ **دفع** → إشعار للـ Admin والمستخدم  
✅ **مرتجعات** → إشعار للـ Admin والمستخدم  
✅ **شكاوي** → إشعار للـ Admin  
✅ **حل شكوى** → إشعار للمستخدم  
✅ **منتج Wishlist متوفر** → إشعار للصيدليات المهتمة  

**كل شيء تلقائي! النظام يشتغل في الخلفية 🚀**

---

## 📚 ملفات التوثيق الأخرى

- `notifications/README.md` - التوثيق الرئيسي
- `notifications/USAGE_EXAMPLES.md` - أمثلة الفواتير
- `notifications/PAYMENT_RETURN_NOTIFICATIONS.md` - الدفع والمرتجعات
- `notifications/ADMIN_WISHLIST_NOTIFICATIONS.md` - هذا الملف ⭐

---

**🎊 نظام الإشعارات متكامل بالكامل!**

