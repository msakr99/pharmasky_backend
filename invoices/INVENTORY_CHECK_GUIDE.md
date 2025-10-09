# دليل التحقق من المخزون
# Inventory Check Guide

## 🎯 الهدف | Purpose

أداة للتحقق من توفر الكميات في المخزون قبل إغلاق فواتير البيع.

Tool to check inventory availability before closing sale invoices.

---

## 🚀 طرق الاستخدام | Usage Methods

### 1️⃣ Django Management Command (الأسهل)

#### فحص فاتورة معينة
```bash
python manage.py check_invoice_inventory 1
```

#### عرض ملخص المخزون الكامل
```bash
python manage.py check_invoice_inventory --summary
```

#### الحصول على النتائج بصيغة JSON
```bash
python manage.py check_invoice_inventory 1 --json
```

---

### 2️⃣ Django Shell

```python
python manage.py shell

# استيراد الدوال
from invoices.check_inventory import *

# فحص فاتورة معينة
check_invoice(1)

# أو
print_inventory_report(1)

# عرض ملخص المخزون
print_inventory_summary()

# الحصول على البيانات كـ dictionary
report = check_invoice_inventory_availability(1)
print(report['can_close'])  # True or False
```

---

### 3️⃣ Python Script

```python
from invoices.check_inventory import check_invoice_inventory_availability

# فحص الفاتورة
report = check_invoice_inventory_availability(invoice_id=1)

# التحقق إذا كانت يمكن إغلاقها
if report['can_close']:
    print("✅ يمكن إغلاق الفاتورة")
else:
    print("❌ لا يمكن إغلاق الفاتورة")
    for error in report['errors']:
        print(error)
```

---

## 📊 مثال على التقرير | Report Example

```
================================================================================
📋 تقرير المخزون لفاتورة البيع رقم: 1
📊 حالة الفاتورة: placed
📦 عدد الأصناف: 4
================================================================================

📊 تفاصيل الأصناف:
--------------------------------------------------------------------------------

✅ الصنف: ايه اي جي ايزوميبرازول 40مجم 21 كبسولة
   ID: 22 | حالة العنصر: accepted
   المطلوب: 48 وحدة
   المتوفر: 100 وحدة
   ✓ متوفر (الفائض: 52)

❌ الصنف: هاينوتون 10 اكياس
   ID: 25 | حالة العنصر: accepted
   المطلوب: 25 وحدة
   المتوفر: 10 وحدة
   ✗ غير كافي (النقص: 15)

--------------------------------------------------------------------------------

❌ أخطاء (يجب حلها قبل الإغلاق):
   ❌ هاينوتون 10 اكياس: يحتاج 25 لكن متوفر فقط 10 (نقص: 15)

================================================================================
❌ لا يمكن إغلاق الفاتورة - هناك نقص في المخزون
================================================================================
```

---

## 📋 هيكل التقرير | Report Structure

```python
{
    "invoice_id": 1,
    "invoice_status": "placed",
    "total_items": 4,
    "can_close": False,  # هل يمكن إغلاق الفاتورة
    "items": [
        {
            "item_id": 2,
            "product_id": 22,
            "product_name": "ايه اي جي ايزوميبرازول",
            "product_e_name": "aig esomeprazole",
            "required_quantity": 48,
            "available_quantity": 100,
            "is_sufficient": True,
            "difference": 52,
            "status": "accepted"
        }
    ],
    "warnings": [
        "⚠️ Product X: الكمية المتبقية قليلة"
    ],
    "errors": [
        "❌ Product Y: نقص في المخزون"
    ]
}
```

---

## 🔍 حالات الاستخدام | Use Cases

### 1. قبل إغلاق الفاتورة
```bash
# فحص المخزون أولاً
python manage.py check_invoice_inventory 1

# إذا كان can_close = True
# يمكنك إغلاق الفاتورة بأمان
```

### 2. معرفة النقص في المخزون
```python
from invoices.check_inventory import check_invoice_inventory_availability

report = check_invoice_inventory_availability(1)

# عرض الأصناف الناقصة فقط
for item in report['items']:
    if not item['is_sufficient']:
        print(f"نقص في: {item['product_name']}")
        print(f"المطلوب: {item['required_quantity']}")
        print(f"المتوفر: {item['available_quantity']}")
        print(f"النقص: {abs(item['difference'])}\n")
```

### 3. فحص متعدد للفواتير
```python
from invoices.check_inventory import check_invoice_inventory_availability

invoice_ids = [1, 2, 3, 4, 5]

for invoice_id in invoice_ids:
    report = check_invoice_inventory_availability(invoice_id)
    status = "✅" if report['can_close'] else "❌"
    print(f"{status} Invoice {invoice_id}: {len(report['errors'])} errors")
```

---

## ⚠️ ملاحظات مهمة | Important Notes

### 1. يتم الفحص على المخزون الرئيسي فقط
المخزون الافتراضي هو المخزون الرئيسي (Main Inventory).

### 2. الترتيب حسب نسبة الخصم
عند خصم الكميات، يتم البدء بالأصناف ذات خصم البيع الأعلى.

### 3. الحالة المطلوبة للإغلاق
جميع عناصر الفاتورة يجب أن تكون في حالة `RECEIVED` قبل الإغلاق.

---

## 🔧 إصلاح النقص في المخزون | Fixing Inventory Shortage

إذا كان هناك نقص:

### الخيار 1: إضافة للمخزون
```python
from inventory.utils import create_inventory_item

# إضافة كمية للمخزون
data = {
    "inventory": main_inventory,
    "product": product,
    "quantity": 50,
    "remaining_quantity": 50,
    # ... باقي البيانات
}
create_inventory_item(data)
```

### الخيار 2: تقليل كمية الفاتورة
```bash
PATCH /api/v1/invoices/sale-invoice-items/6/
{
  "quantity": 10  # بدلاً من 25
}
```

### الخيار 3: حذف الصنف من الفاتورة
```bash
DELETE /api/v1/invoices/sale-invoice-items/6/
```

---

## 📈 مثال كامل | Complete Example

```bash
# 1. فحص المخزون
python manage.py check_invoice_inventory 1

# إذا كانت النتيجة:
# ❌ لا يمكن إغلاق الفاتورة - هناك نقص في المخزون
#    ❌ هاينوتون: يحتاج 25 لكن متوفر 10 (نقص: 15)

# 2. خيارات الحل:

# أ. تقليل الكمية المطلوبة
curl -X PATCH http://129.212.140.152/invoices/sale-invoice-items/6/ \
  -H "Content-Type: application/json" \
  -d '{"quantity": 10}'

# ب. أو حذف الصنف
curl -X DELETE http://129.212.140.152/invoices/sale-invoice-items/6/

# 3. فحص مرة أخرى
python manage.py check_invoice_inventory 1

# النتيجة:
# ✅ يمكن إغلاق الفاتورة - جميع الكميات متوفرة

# 4. تحديث حالة العناصر
curl -X PATCH http://129.212.140.152/invoices/sale-invoice-items/2/change-state/ \
  -d '{"status": "received"}'

# 5. إغلاق الفاتورة
curl -X POST http://129.212.140.152/invoices/sale-invoices/1/change-state/ \
  -d '{"status": "closed"}'
```

---

## 📞 استكشاف الأخطاء | Troubleshooting

### المشكلة: "Invoice not found"
**الحل**: تأكد من أن معرف الفاتورة صحيح.

### المشكلة: المخزون فارغ
**الحل**: أضف أصناف للمخزون عبر فواتير الشراء أو يدوياً.

### المشكلة: الكميات غير صحيحة
**الحل**: تحقق من `remaining_quantity` في جدول `inventory_items`.

---

## 🎯 الملفات ذات الصلة | Related Files

- `invoices/check_inventory.py` - الكود الأساسي
- `invoices/management/commands/check_invoice_inventory.py` - Django command
- `invoices/utils.py` - دالة `close_sale_invoice()`
- `inventory/utils.py` - دالة `deduct_product_amount()`

---

**التاريخ**: 2025-10-09  
**الإصدار**: 1.0  
**الحالة**: ✅ جاهز للاستخدام

