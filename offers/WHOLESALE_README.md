# نظام عروض الجملة (Wholesale Offers System)

> نظام متكامل لإدارة عروض الجملة للمتاجر والشركات، منفصل تماماً عن نظام العروض العادية

[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-blue.svg)](https://www.django-rest-framework.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## 📋 المحتويات

1. [نظرة عامة](#-نظرة-عامة)
2. [المميزات](#-المميزات)
3. [التثبيت](#-التثبيت)
4. [التوثيق](#-التوثيق)
5. [الاستخدام السريع](#-الاستخدام-السريع)
6. [الأسئلة الشائعة](#-الأسئلة-الشائعة)

---

## 🎯 نظرة عامة

نظام عروض الجملة هو إضافة جديدة لنظام العروض الموجود، مصمم خصيصاً للشركات والمتاجر الكبيرة. يتميز بـ:

- ✅ **انفصال تام** عن العروض العادية
- ✅ **حد أدنى محدد** (10 علب افتراضياً)
- ✅ **زيادة محددة** (5 علب افتراضياً)
- ✅ **خصومات أكبر** للكميات الكبيرة
- ✅ **maxoffers منفصل** عن العروض العادية

### الفرق الرئيسي

```
العروض العادية          عروض الجملة
    |                       |
    v                       v
max-offers          max-wholesale-offers
    |                       |
is_max=True         is_max_wholesale=True
```

---

## ⭐ المميزات

### 1. إدارة متقدمة للكميات
- حد أدنى قابل للتخصيص لكل عرض
- زيادة محددة (مثلاً: 10, 15, 20, 25...)
- تحكم كامل في الطلبات

### 2. أمان وصلاحيات
- متاح فقط للمتاجر ذات `company=True`
- التحقق التلقائي من الصلاحيات
- فصل تام عن العروض العادية

### 3. APIs متكاملة
- 7 endpoints جديدة
- دعم كامل للبحث والفلترة
- رفع من Excel
- تصدير إلى Excel

### 4. حساب تلقائي لأفضل العروض
- `is_max_wholesale` يتم حسابه تلقائياً
- تحديث ديناميكي عند الإضافة/التعديل/الحذف
- لا يؤثر على `is_max` للعروض العادية

---

## 🚀 التثبيت

### 1. تشغيل Migration

```bash
# تأكد من وجود البيئة الافتراضية مفعلة
python manage.py migrate offers
```

### 2. التحقق من التثبيت

```bash
python manage.py shell
```

```python
from offers.models import Offer

# التحقق من وجود الحقول الجديدة
print(Offer._meta.get_field('is_wholesale'))
print(Offer._meta.get_field('wholesale_min_quantity'))
print(Offer._meta.get_field('wholesale_increment'))
print(Offer._meta.get_field('is_max_wholesale'))

# يجب أن تظهر بدون أخطاء
```

---

## 📚 التوثيق

### الملفات المتاحة:

| الملف | الوصف |
|------|-------|
| [WHOLESALE_OFFERS_GUIDE.md](./WHOLESALE_OFFERS_GUIDE.md) | دليل شامل لاستخدام النظام |
| [WHOLESALE_API_EXAMPLES.md](./WHOLESALE_API_EXAMPLES.md) | أمثلة عملية للـ APIs |
| [WHOLESALE_EXCEL_FORMAT.md](./WHOLESALE_EXCEL_FORMAT.md) | تنسيق ملف Excel للرفع |
| [REGULAR_VS_WHOLESALE.md](./REGULAR_VS_WHOLESALE.md) | مقارنة بين النظامين |
| [WHOLESALE_SUMMARY.md](./WHOLESALE_SUMMARY.md) | ملخص سريع للتغييرات |

---

## 🏃 الاستخدام السريع

### 1. إنشاء عرض جملة

```bash
curl -X POST 'https://api.example.com/api/offers/wholesale-offers/create/' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_code": 12345,
    "available_amount": 500,
    "purchase_discount_percentage": 18.00,
    "is_wholesale": true,
    "wholesale_min_quantity": 20,
    "wholesale_increment": 10
  }'
```

### 2. عرض أفضل عروض الجملة

```bash
curl -X GET 'https://api.example.com/api/offers/max-wholesale-offers/' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### 3. رفع من Excel

```bash
curl -X POST 'https://api.example.com/api/offers/wholesale-offers/upload/' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'file=@wholesale_offers.xlsx' \
  -F 'user=789' \
  -F 'is_wholesale=true'
```

---

## 🔍 الأسئلة الشائعة

### س: هل عروض الجملة تؤثر على العروض العادية؟
**ج:** لا، النظامان منفصلان تماماً. `is_max` و `is_max_wholesale` مستقلان.

### س: هل يمكن للمتجر العادي إنشاء عروض جملة؟
**ج:** لا، يجب أن يكون `company=True` في `StoreProfile`.

### س: ما هي القيم الافتراضية للحد الأدنى والزيادة؟
**ج:** الحد الأدنى = 10 علب، الزيادة = 5 علب. يمكن تخصيصهما لكل عرض.

### س: هل يمكن للمنتج الواحد أن يكون له عرضين (عادي وجملة)؟
**ج:** نعم، وهذا هو المتوقع. العروض العادية للصيدليات الصغيرة، والجملة للشركات.

### س: كيف أعرف أي عرض أفضل؟
**ج:** `is_max=True` للعروض العادية، `is_max_wholesale=True` لعروض الجملة.

### س: هل يمكن البحث في عروض الجملة؟
**ج:** نعم، يدعم البحث بالاسم والفلترة والترتيب. راجع [WHOLESALE_API_EXAMPLES.md](./WHOLESALE_API_EXAMPLES.md).

---

## 📊 البنية التقنية

### Models

```python
class Offer(models.Model):
    # الحقول الموجودة...
    
    # حقول الجملة الجديدة
    is_wholesale = models.BooleanField(default=False)
    wholesale_min_quantity = models.PositiveIntegerField(default=10)
    wholesale_increment = models.PositiveIntegerField(default=5)
    is_max_wholesale = models.BooleanField(default=False)
```

### URLs

```
/api/offers/wholesale-offers/              # قائمة الكل
/api/offers/max-wholesale-offers/          # أفضل العروض
/api/offers/wholesale-offers/create/       # إنشاء
/api/offers/wholesale-offers/upload/       # رفع Excel
/api/offers/wholesale-offers/<id>/change/  # تحديث
/api/offers/wholesale-offers/<id>/destroy/ # حذف
/api/offers/max-wholesale-offers/excel/    # تصدير
```

### Utils

```python
# دوال جديدة
calculate_max_wholesale_offer(product)
calculate_max_wholesale_offer_from_offer(offer)
update_wholesale_offer(offer, data)
```

---

## 🔐 الصلاحيات

| View | الصلاحيات المطلوبة |
|------|-------------------|
| List All | Sales, DataEntry, Manager |
| Max List | Sales, DataEntry, Pharmacy, Manager |
| Create | Sales, DataEntry, Manager, Admin |
| Upload | Sales, DataEntry, Manager, Admin |
| Update | Sales, DataEntry, Manager |
| Delete | Sales, DataEntry, Manager |
| Excel Export | Sales, DataEntry, Manager |

---

## 🧪 الاختبار

### اختبار أساسي

```python
from offers.models import Offer
from accounts.models import Store
from market.models import Product, StoreProductCode

# 1. التحقق من المتجر
store = Store.objects.get(id=YOUR_STORE_ID)
store_profile = store.store.first()
assert store_profile.company == True

# 2. إنشاء عرض جملة
offer = Offer.objects.create(
    product_code=some_product_code,
    product=some_product,
    user=store,
    available_amount=100,
    remaining_amount=100,
    purchase_discount_percentage=18.00,
    purchase_price=41.00,
    selling_discount_percentage=15.00,
    selling_price=42.50,
    is_wholesale=True,
    wholesale_min_quantity=20,
    wholesale_increment=10,
)

# 3. التحقق من الحساب التلقائي
assert offer.is_max_wholesale == True

print("✅ جميع الاختبارات نجحت!")
```

---

## 📈 أمثلة الاستخدام

### مثال 1: شركة أدوية كبيرة

```
الشركة: United Pharma (company=True)
المنتج: Paracetamol 500mg
الكمية المتاحة: 10,000 علبة
الحد الأدنى: 100 علبة
الزيادة: 50 علبة
الخصم: 20%

النتيجة:
- الصيدليات يمكنها الشراء بكميات كبيرة
- الحد الأدنى 100، يمكن طلب: 100, 150, 200, 250...
- خصم كبير (20%) لتشجيع الطلبات الكبيرة
```

### مثال 2: موزع أدوية

```
الموزع: MediDist (company=True)
المنتج: Aspirin 100mg
الكمية المتاحة: 5,000 علبة
الحد الأدنى: 50 علبة
الزيادة: 25 علبة
الخصم: 18%

النتيجة:
- مناسب للصيدليات المتوسطة والكبيرة
- طلبات بكميات محددة: 50, 75, 100, 125...
- خصم جيد (18%) للجملة
```

---

## 🛠️ استكشاف الأخطاء

### خطأ: "عروض الجملة متاحة فقط للمتاجر المسجلة كشركات"

**السبب**: `company=False` في StoreProfile

**الحل**:
```python
store = Store.objects.get(id=YOUR_STORE_ID)
store_profile = store.store.first()
store_profile.company = True
store_profile.save()
```

---

### خطأ: "Product code not found"

**السبب**: الـ `product_code` غير موجود في `StoreProductCode`

**الحل**:
```python
from market.models import StoreProductCode

StoreProductCode.objects.create(
    product=your_product,
    store=your_store,
    code=12345
)
```

---

## 📞 الدعم

للاستفسارات أو المساعدة:
- 📧 البريد الإلكتروني: support@example.com
- 📱 الواتساب: +20xxxxxxxxxx
- 💬 Slack: #offers-support

---

## 📝 التحديثات المستقبلية

- [ ] نظام سلة خاص بالجملة
- [ ] خصومات متدرجة حسب الكمية
- [ ] إشعارات للعروض الجديدة
- [ ] تقارير تحليلية للجملة
- [ ] دعم عروض الجملة في التطبيق المحمول

---

## 🙏 شكر وتقدير

تم تطوير هذا النظام لتحسين تجربة المستخدم وتلبية احتياجات الشركات الكبيرة.

---

## 📜 الترخيص

هذا النظام جزء من نظام Pharmasky الأساسي ويخضع لنفس شروط الترخيص.

---

**آخر تحديث**: 11 أكتوبر 2025

**النسخة**: 1.0.0

**الحالة**: ✅ جاهز للإنتاج

