# توثيق تتبع تقليل الكميات في الفواتير
# Invoice Quantity Reduction Tracking Documentation

## نظرة عامة | Overview

تم إضافة ميزة جديدة لتتبع الكميات المقللة من الأصناف في الفواتير. عندما يتم تقليل كمية صنف في الفاتورة (مثلاً من 50 إلى 48)، يتم تسجيل الكمية المحذوفة (2 في هذا المثال) في `deleted_items` تلقائيًا.

A new feature has been added to track quantity reductions in invoice items. When an item's quantity is reduced (e.g., from 50 to 48), the removed quantity (2 in this example) is automatically recorded in `deleted_items`.

---

## السلوك السابق vs الجديد | Previous vs New Behavior

### السلوك السابق | Previous Behavior

```json
// عند تقليل الكمية من 50 إلى 48
{
  "items": [
    {
      "id": 2,
      "quantity": 48,  // تم التقليل
      "remaining_quantity": 50
    }
  ],
  "deleted_items": []  // فارغة، لا يتم تسجيل الكمية المحذوفة
}
```

### السلوك الجديد | New Behavior

```json
// عند تقليل الكمية من 50 إلى 48
{
  "items": [
    {
      "id": 2,
      "quantity": 48,  // الكمية الحالية
      "remaining_quantity": 50
    }
  ],
  "deleted_items": [
    {
      "id": 10,
      "product": {...},
      "quantity": 2,  // الكمية المحذوفة فقط (50 - 48 = 2)
      "remaining_quantity": 2,
      "sub_total": "395.16",  // حسب سعر الوحدة
      "timestamp": "2025-10-09T17:30:00Z"
    }
  ]
}
```

---

## كيف يعمل | How It Works

### 1. عند تحديث الكمية | On Quantity Update

عندما يتم تحديث كمية صنف في الفاتورة:

```python
# API Request
PATCH /api/v1/invoices/sale-invoice-items/2/
{
  "quantity": 48  // الكمية الجديدة (كانت 50)
}
```

يقوم النظام بـ:
1. حساب الفرق: `reduced_quantity = old_quantity - new_quantity = 50 - 48 = 2`
2. إنشاء سجل في `deleted_items` للكمية المحذوفة (2)
3. تحديث العنصر الأصلي ليحتوي على الكمية الجديدة (48)

### 2. المعلومات المسجلة | Recorded Information

السجل المنشأ في `deleted_items` يحتوي على:
- **نفس بيانات المنتج** من العنصر الأصلي
- **الكمية المحذوفة فقط** (ليس الكمية الكاملة)
- **sub_total محسوب** على أساس الكمية المحذوفة
- **timestamp** لتسجيل وقت التقليل

---

## أمثلة عملية | Practical Examples

### مثال 1: تقليل كمية واحد مرة واحدة

```python
# الحالة الأولية
item.quantity = 50

# التحديث الأول
PATCH /api/v1/invoices/sale-invoice-items/2/
{"quantity": 48}

# النتيجة
items[0].quantity = 48
deleted_items[0].quantity = 2  # ✅ تم إضافة سجل جديد
```

---

### مثال 2: تقليل كمية متعددة مرات

```python
# الحالة الأولية
item.quantity = 50

# التحديث الأول
PATCH {"quantity": 48}
# deleted_items[0].quantity = 2

# التحديث الثاني
PATCH {"quantity": 45}
# deleted_items[1].quantity = 3  # ✅ سجل جديد آخر

# النتيجة النهائية
items[0].quantity = 45
deleted_items = [
  {"quantity": 2, "timestamp": "..."},  // التقليل الأول
  {"quantity": 3, "timestamp": "..."}   // التقليل الثاني
]
# إجمالي الكميات المحذوفة = 5
```

---

### مثال 3: زيادة الكمية (لا يتم التسجيل)

```python
# الحالة الأولية
item.quantity = 48

# محاولة زيادة الكمية
PATCH {"quantity": 50}

# النتيجة
items[0].quantity = 50
# ❌ لا يتم إضافة سجل في deleted_items
# لأن الكمية زادت وليست قلت
```

---

## الفرق بين الحذف الكامل والتقليل | Full Delete vs Reduction

### حذف كامل | Full Delete

```python
DELETE /api/v1/invoices/sale-invoice-items/2/

# deleted_items
{
  "quantity": 50,  // الكمية الكاملة
  "sub_total": "9876.00",  // الإجمالي الكامل
  "timestamp": "..."
}
# ✅ يتم حذف العنصر من items تماماً
```

### تقليل الكمية | Quantity Reduction

```python
PATCH /api/v1/invoices/sale-invoice-items/2/
{"quantity": 48}

# deleted_items
{
  "quantity": 2,  // الكمية المحذوفة فقط
  "sub_total": "395.16",  // سعر 2 وحدة فقط
  "timestamp": "..."
}
# ✅ العنصر يبقى في items بالكمية الجديدة
```

---

## حسابات Sub_Total | Sub_Total Calculations

### لفواتير البيع | Sale Invoices

```python
# العنصر الأصلي
item.selling_price = 197.58
item.quantity = 50

# عند التقليل إلى 48
old_quantity = 50
new_quantity = 48
reduced_quantity = 2

# deleted_item
deleted_item.quantity = 2
deleted_item.selling_price = 197.58  // نفس السعر
deleted_item.sub_total = 197.58 × 2 = 395.16  // ✅ فقط للكمية المحذوفة
```

### لفواتير الشراء | Purchase Invoices

```python
# العنصر الأصلي
item.purchase_price = 187.59
item.quantity = 50

# عند التقليل إلى 48
reduced_quantity = 2

# deleted_item
deleted_item.quantity = 2
deleted_item.purchase_price = 187.59
deleted_item.sub_total = 187.59 × 2 = 375.18  // ✅ يستخدم purchase_price
```

---

## الاستخدام في API | API Usage

### تحديث الكمية | Update Quantity

```bash
# Request
PATCH /api/v1/invoices/sale-invoice-items/2/
Content-Type: application/json

{
  "quantity": 48
}

# Response
{
  "id": 2,
  "quantity": 48,
  "remaining_quantity": 50,
  "sub_total": "9483.84",
  ...
}
```

### عرض deleted_items

```bash
# Request
GET /api/v1/invoices/sale/1/

# Response
{
  "id": 1,
  "items": [
    {
      "id": 2,
      "quantity": 48,
      "sub_total": "9483.84"
    }
  ],
  "deleted_items": [
    {
      "id": 10,
      "product": {...},
      "quantity": 2,  // الكمية المقللة
      "sub_total": "395.16",  // 197.58 × 2
      "timestamp": "2025-10-09T17:30:00Z"
    },
    {
      "id": 1,
      "product": {...},
      "quantity": 20,  // صنف محذوف بالكامل
      "sub_total": "198.00",
      "timestamp": "2025-10-09T16:57:09Z"
    }
  ]
}
```

---

## التحكم في الميزة | Feature Control

### تعطيل التتبع | Disable Tracking

يمكنك تعطيل تتبع الكميات المقللة عن طريق parameter:

```python
from invoices.utils import update_sale_invoice_item

# مع التتبع (default)
update_sale_invoice_item(item, data, track_quantity_reduction=True)

# بدون تتبع
update_sale_invoice_item(item, data, track_quantity_reduction=False)
```

---

## الفوائد | Benefits

### 1. **التدقيق والمراجعة** | Audit Trail
- تتبع كامل لجميع التغييرات في الكميات
- معرفة من قلل الكمية ومتى
- إمكانية المراجعة والتحليل

### 2. **الشفافية** | Transparency
- وضوح في التغييرات التي حدثت على الفاتورة
- معرفة الكميات المحذوفة بدقة

### 3. **التقارير** | Reporting
- تحليل الكميات المحذوفة عبر الزمن
- معرفة أسباب التغييرات في الفواتير
- تتبع الهدر أو الأخطاء

### 4. **المحاسبة** | Accounting
- حساب دقيق للفروقات
- تتبع المبالغ المسترجعة أو المعدلة

---

## الحالات الخاصة | Edge Cases

### 1. تقليل الكمية إلى صفر

```python
# الحالة الأولية
item.quantity = 10

# تحديث إلى صفر
PATCH {"quantity": 0}

# النتيجة
items[0].quantity = 0  // ✅ لا يزال موجود
deleted_items[0].quantity = 10  // ✅ تم تسجيل الكمية المحذوفة

# ملاحظة: الصنف يبقى في items حتى يتم حذفه بشكل صريح
```

### 2. تغييرات متعددة في نفس الوقت

```python
# تحديث الكمية والسعر معاً
PATCH {
  "quantity": 45,
  "selling_discount_percentage": 12.00
}

# النتيجة
items[0].quantity = 45
items[0].selling_discount_percentage = 12.00
items[0].selling_price = 195.36  // محدث

deleted_items[0].quantity = 5  // الكمية المحذوفة
deleted_items[0].selling_price = 197.58  // السعر القديم! ✅
```

### 3. تقليل ثم حذف كامل

```python
# الحالة الأولية
item.quantity = 50

# التقليل
PATCH {"quantity": 48}
# deleted_items[0].quantity = 2

# الحذف الكامل
DELETE /api/v1/invoices/sale-invoice-items/2/
# deleted_items[1].quantity = 48  // الكمية المتبقية

# النتيجة النهائية
deleted_items = [
  {"quantity": 2, "timestamp": "10:00"},  // التقليل
  {"quantity": 48, "timestamp": "10:05"}  // الحذف الكامل
]
```

---

## ملاحظات مهمة | Important Notes

### 1. **التوقيت** | Timing
- يتم إنشاء سجل deleted_item **قبل** حفظ العنصر الأصلي
- يحتوي على **البيانات القديمة** للعنصر (السعر القديم، الخصم القديم، إلخ)

### 2. **الحسابات** | Calculations
- `sub_total` يُحسب فقط للكمية المحذوفة
- يتم استخدام `selling_price` القديم (قبل التحديث)

### 3. **الأداء** | Performance
- عملية خفيفة، تنفذ query إضافي واحد فقط
- لا يؤثر على الأداء بشكل ملحوظ

### 4. **قاعدة البيانات** | Database
- لا حاجة لـ migration جديد
- يستخدم نفس جدول `deleted_items` الموجود

---

## الملفات المعدلة | Modified Files

### 1. **invoices/managers.py**
```python
class SaleInvoiceDeletedItemManager:
    def create_for_quantity_reduction(self, instance, reduced_quantity):
        # إنشاء سجل للكمية المحذوفة فقط
        ...

class PurchaseInvoiceDeletedItemManager:
    def create_for_quantity_reduction(self, instance, reduced_quantity):
        # نفس الشيء لفواتير الشراء
        ...
```

### 2. **invoices/utils.py**
```python
def update_sale_invoice_item(item, data, track_quantity_reduction=True):
    # إضافة منطق تتبع تقليل الكمية
    if track_quantity_reduction and old_quantity > new_quantity:
        SaleInvoiceDeletedItem.objects.create_for_quantity_reduction(...)

def update_purchase_invoice_item(item, data, track_quantity_reduction=True):
    # نفس الشيء لفواتير الشراء
    ...
```

---

## الأسئلة الشائعة | FAQ

### Q1: هل يتم تسجيل زيادة الكمية؟
**A:** لا، يتم تسجيل التقليل فقط (`old_quantity > new_quantity`).

### Q2: ماذا لو قللت الكمية أكثر من مرة؟
**A:** يتم إنشاء سجل جديد في `deleted_items` لكل تقليل. يمكنك رؤية جميع التغييرات عبر `timestamp`.

### Q3: هل يمكن تعطيل هذه الميزة؟
**A:** نعم، عن طريق `track_quantity_reduction=False` عند استدعاء دالة التحديث.

### Q4: هل تؤثر على الفواتير القديمة؟
**A:** لا، الميزة تعمل فقط على التحديثات الجديدة من الآن فصاعداً.

### Q5: كيف أميز بين الحذف الكامل وتقليل الكمية؟
**A:** 
- الحذف الكامل: العنصر غير موجود في `items`
- التقليل: العنصر موجود في `items` بكمية أقل

### Q6: هل يتم تحديث `total_price` للفاتورة؟
**A:** نعم، يتم تحديثها تلقائياً عبر `affect_invoice()`.

---

## الإصدار | Version

- **التاريخ**: 2025-10-09
- **الإصدار**: 1.0
- **الحالة**: ✅ جاهز للإنتاج

---

## المراجع | References

- [Django Model Managers](https://docs.djangoproject.com/en/stable/topics/db/managers/)
- [Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Decimal Precision](https://docs.python.org/3/library/decimal.html)

