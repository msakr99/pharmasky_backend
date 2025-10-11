# دليل استخدام عروض الجملة (Wholesale Offers)

## نظرة عامة

تم إضافة نظام منفصل تماماً لعروض الجملة، مخصص للمتاجر المسجلة كشركات (company=True في StoreProfile).

## المميزات الرئيسية

### 1. انفصال تام عن العروض العادية
- عروض الجملة لها قائمة `max-wholesale-offers` منفصلة عن `max-offers` العادية
- حقل `is_max_wholesale` منفصل عن `is_max`
- لا تؤثر عروض الجملة على العروض العادية والعكس صحيح

### 2. شروط الطلب
- **الحد الأدنى**: 10 علب (افتراضي، قابل للتعديل)
- **الزيادة**: بمقدار 5 علب (افتراضي، قابل للتعديل)
- مثال: يمكن طلب 10، 15، 20، 25 علبة... إلخ

### 3. متطلبات الاستخدام
- يجب أن يكون `company=True` في `StoreProfile` للمتجر
- إذا حاولت إنشاء عرض جملة لمتجر ليس شركة، ستظهر رسالة خطأ

## الـ Models

### حقول جديدة في نموذج Offer:

```python
is_wholesale = BooleanField(default=False)
# هل هذا عرض جملة؟

wholesale_min_quantity = PositiveIntegerField(default=10)
# الحد الأدنى للطلب (افتراضي: 10 علب)

wholesale_increment = PositiveIntegerField(default=5)
# مقدار الزيادة المسموح بها (افتراضي: 5 علب)

is_max_wholesale = BooleanField(default=False)
# هل هذا أفضل عرض جملة للمنتج؟
```

## الـ APIs

### 1. قائمة جميع عروض الجملة (للإدارة)
```
GET /api/offers/wholesale-offers/
```
- الصلاحيات: Sales, DataEntry, Manager
- يعرض جميع عروض الجملة
- يدعم البحث والفلترة والترتيب

### 2. قائمة أفضل عروض الجملة (للصيدليات)
```
GET /api/offers/max-wholesale-offers/
```
- الصلاحيات: Sales, DataEntry, Pharmacy, Manager
- يعرض فقط العروض ذات `is_max_wholesale=True`
- منفصل تماماً عن `/max-offers/`
- يدعم البحث والفلترة

### 3. إنشاء عرض جملة
```
POST /api/offers/wholesale-offers/create/
```
Body:
```json
{
  "product_code": 12345,
  "available_amount": 100,
  "purchase_discount_percentage": 15.50,
  "is_wholesale": true,
  "wholesale_min_quantity": 10,
  "wholesale_increment": 5,
  "min_purchase": 0,
  "operating_number": "OP-2024-001"
}
```

**ملاحظة**: يتحقق النظام تلقائياً من أن المتجر لديه `company=True`

### 4. رفع عروض جملة من Excel
```
POST /api/offers/wholesale-offers/upload/
```
Body (multipart/form-data):
```
file: [Excel file]
user: [Store ID]
is_wholesale: true
```

الأعمدة المطلوبة في الملف:
- `product_code`: كود المنتج
- `available_amount`: الكمية المتاحة
- `purchase_discount_percentage`: نسبة الخصم
- `max_amount_per_invoice`: الحد الأقصى لكل فاتورة
- `min_purchase`: الحد الأدنى للشراء
- `product_expiry_date`: تاريخ الانتهاء
- `operating_number`: رقم التشغيل

الأعمدة الاختيارية:
- `wholesale_min_quantity`: الحد الأدنى للجملة (افتراضي: 10)
- `wholesale_increment`: مقدار الزيادة (افتراضي: 5)

### 5. تحديث عرض جملة
```
PATCH /api/offers/wholesale-offers/{id}/change/
```

### 6. حذف عرض جملة
```
DELETE /api/offers/wholesale-offers/{id}/destroy/
```

### 7. تحميل عروض الجملة كـ Excel
```
GET /api/offers/max-wholesale-offers/excel/
```
- يصدر ملف Excel بأفضل عروض الجملة
- يدعم فلتر `payment_period`

## آلية عمل max_wholesale

### حساب أفضل عرض جملة:

1. عند إنشاء/تحديث/حذف عرض جملة
2. يتم البحث عن جميع عروض الجملة للمنتج نفسه
3. يتم إيجاد أعلى خصم (`selling_discount_percentage`)
4. جميع العروض بهذا الخصم يتم تعليمها `is_max_wholesale=True`
5. باقي العروض `is_max_wholesale=False`

### دوال Utils الخاصة:

```python
# حساب أفضل عرض جملة للمنتج
calculate_max_wholesale_offer(product)

# حساب أفضل عرض جملة من عرض محدد
calculate_max_wholesale_offer_from_offer(offer)

# تحديث عرض جملة
update_wholesale_offer(offer, data)
```

## الفلاتر

يمكن استخدام الفلاتر التالية:

- `is_wholesale=true`: فقط عروض الجملة
- `is_max_wholesale=true`: فقط أفضل عروض الجملة
- `wholesale_min_quantity`: حسب الحد الأدنى
- `user`: حسب المتجر/الشركة

## أمثلة الاستخدام

### مثال 1: إنشاء عرض جملة
```bash
curl -X POST https://api.example.com/api/offers/wholesale-offers/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": 12345,
    "available_amount": 500,
    "purchase_discount_percentage": 18.00,
    "is_wholesale": true,
    "wholesale_min_quantity": 20,
    "wholesale_increment": 10
  }'
```

### مثال 2: الحصول على أفضل عروض الجملة
```bash
curl -X GET https://api.example.com/api/offers/max-wholesale-offers/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### مثال 3: البحث في عروض الجملة
```bash
curl -X GET "https://api.example.com/api/offers/max-wholesale-offers/?search=aspirin" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ملاحظات مهمة

1. **الانفصال التام**: عروض الجملة منفصلة تماماً عن العروض العادية ولا تؤثر على بعضها
2. **التحقق من الشركة**: النظام يتحقق تلقائياً من `company=True` عند إنشاء عروض جملة
3. **الحد الأدنى والزيادة**: يمكن تخصيص الحد الأدنى ومقدار الزيادة لكل عرض
4. **Max Offers**: لكل منتج قد يكون له `is_max=True` للعروض العادية و `is_max_wholesale=True` لعروض الجملة في نفس الوقت
5. **السلات**: عروض الجملة لا تؤثر على السلات العادية (حالياً)

## التحديثات المستقبلية المحتملة

- [ ] إضافة نظام سلة خاص بالجملة
- [ ] إضافة تقارير خاصة بالجملة
- [ ] إضافة إشعارات للعروض الجديدة
- [ ] دعم خصومات متدرجة حسب الكمية

## استفسارات وملاحظات

للاستفسارات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

