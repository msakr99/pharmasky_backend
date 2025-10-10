# دليل نظام المخزون
# Inventory System Guide

## 📦 قائمة الأصناف في المخزن

### الحقول المتاحة

عند طلب قائمة المخزون، ستحصل على جميع المعلومات التالية لكل صنف:

| الحقل | الوصف | مثال |
|-------|-------|------|
| **product.name** | اسم الصنف | Paracetamol 500mg |
| **product.public_price** | السعر العام | 100.00 |
| **purchase_price** | سعر الشراء | 90.00 |
| **selling_price** | سعر البيع | 95.00 |
| **purchase_discount_percentage** | نسبة خصم الشراء | 10% |
| **selling_discount_percentage** | نسبة خصم البيع | 5% |
| **quantity** | الكمية الأصلية | 100 |
| **remaining_quantity** | الكمية المتبقية | 85 |
| **supplier_name** | اسم المورد | تاج |
| **supplier_invoice_number** | رقم فاتورة المورد | 4601 |
| **purchase_date** | تاريخ الشراء | 2025-10-09 |
| **product_expiry_date** | تاريخ انتهاء الصلاحية | 2026-12-31 |
| **operating_number** | رقم التشغيل | BATCH-001 |

---

## 🔍 طلب قائمة المخزون

### الطلب الأساسي

```http
GET http://129.212.140.152/inventory/inventory-items/
Authorization: Token your-token-here
```

### الاستجابة

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "inventory": {
        "id": 1,
        "name": "Auto created Main Inventory",
        "type": "main"
      },
      "product": {
        "id": 10,
        "name": "Paracetamol 500mg",
        "public_price": "100.00"
      },
      "product_expiry_date": "2026-12-31",
      "operating_number": "BATCH-001",
      
      // أسعار وخصومات الشراء
      "purchase_discount_percentage": "10.00",
      "purchase_price": "90.00",
      
      // أسعار وخصومات البيع
      "selling_discount_percentage": "5.00",
      "selling_price": "95.00",
      
      // الكميات
      "quantity": 100,
      "remaining_quantity": 85,
      
      // الإجماليات
      "purchase_sub_total": "7650.00",  // 85 × 90
      "selling_sub_total": "8075.00",   // 85 × 95
      
      // معلومات المورد والفاتورة ⭐ جديد
      "supplier_name": "تاج",
      "supplier_invoice_number": "4601",
      "purchase_date": "2025-10-09T10:16:12.988007Z"
    },
    {
      "id": 2,
      "product": {
        "name": "Ibuprofen 400mg",
        "public_price": "200.00"
      },
      "purchase_price": "170.00",
      "selling_price": "184.00",
      "purchase_discount_percentage": "15.00",
      "selling_discount_percentage": "8.00",
      "quantity": 50,
      "remaining_quantity": 47,
      "supplier_name": "تاج",
      "supplier_invoice_number": "4601",
      "purchase_date": "2025-10-09T10:16:12.988007Z"
    }
  ]
}
```

---

## 🔎 البحث والفلترة

### البحث بالاسم

```http
GET /inventory/inventory-items/?search=paracetamol
```

### الفلترة حسب المخزن

```http
GET /inventory/inventory-items/?inventory=1
```

### الفلترة حسب المنتج

```http
GET /inventory/inventory-items/?product=10
```

### الترتيب

```http
# ترتيب حسب الاسم
GET /inventory/inventory-items/?o=product__name

# ترتيب حسب السعر
GET /inventory/inventory-items/?o=purchase_price

# ترتيب حسب الكمية المتبقية (الأقل أولاً)
GET /inventory/inventory-items/?o=remaining_quantity

# ترتيب حسب تاريخ انتهاء الصلاحية
GET /inventory/inventory-items/?o=product_expiry_date
```

---

## 📊 تقرير شامل للمخزون

### مثال: تقرير Excel

يمكنك استخدام البيانات لإنشاء تقرير Excel:

| الصنف | السعر | خصم الشراء % | الكمية | المورد | رقم الفاتورة | تاريخ الشراء |
|-------|-------|-------------|--------|---------|-------------|-------------|
| Paracetamol 500mg | 90.00 | 10% | 85 | تاج | 4601 | 2025-10-09 |
| Ibuprofen 400mg | 170.00 | 15% | 47 | تاج | 4601 | 2025-10-09 |
| Aspirin 100mg | 45.00 | 12% | 200 | النور | 4602 | 2025-10-08 |

---

## 💡 حالات الاستخدام

### 1. تقرير الأصناف المنتهية الصلاحية قريباً

```python
from datetime import datetime, timedelta
from inventory.models import InventoryItem

# الأصناف التي ستنتهي صلاحيتها خلال 30 يوم
thirty_days = datetime.now() + timedelta(days=30)
expiring_soon = InventoryItem.objects.filter(
    product_expiry_date__lte=thirty_days,
    remaining_quantity__gt=0
).select_related('product', 'purchase_invoice_item__invoice__user')

for item in expiring_soon:
    print(f"{item.product.name} - ينتهي في {item.product_expiry_date}")
    print(f"المورد: {item.purchase_invoice_item.invoice.user.name}")
    print(f"الكمية المتبقية: {item.remaining_quantity}")
```

### 2. تقرير حسب المورد

```python
# جميع الأصناف من مورد معين
supplier_items = InventoryItem.objects.filter(
    purchase_invoice_item__invoice__user__name="تاج"
).select_related('product', 'purchase_invoice_item__invoice')

total_value = sum(item.purchase_sub_total for item in supplier_items)
print(f"إجمالي المشتريات من تاج: {total_value} جنيه")
```

### 3. الأصناف الأقل في المخزون

```http
GET /inventory/inventory-items/?o=remaining_quantity&ps=10
```

---

## 📱 استخدام في التطبيق

### مثال React/JavaScript

```javascript
// جلب قائمة المخزون
const fetchInventory = async () => {
  const response = await fetch(
    'http://129.212.140.152/inventory/inventory-items/',
    {
      headers: {
        'Authorization': 'Token your-token-here'
      }
    }
  );
  
  const data = await response.json();
  
  // عرض في جدول
  data.results.forEach(item => {
    console.log(`
      الصنف: ${item.product.name}
      السعر: ${item.purchase_price} جنيه
      الخصم: ${item.purchase_discount_percentage}%
      الكمية: ${item.remaining_quantity}
      المورد: ${item.supplier_name}
      رقم الفاتورة: ${item.supplier_invoice_number}
      تاريخ الشراء: ${new Date(item.purchase_date).toLocaleDateString('ar-EG')}
    `);
  });
};
```

---

## 🎨 عرض في واجهة المستخدم

### جدول HTML

```html
<table>
  <thead>
    <tr>
      <th>الصنف</th>
      <th>السعر</th>
      <th>الخصم</th>
      <th>الكمية</th>
      <th>المورد</th>
      <th>رقم الفاتورة</th>
      <th>تاريخ الشراء</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Paracetamol 500mg</td>
      <td>90.00 جنيه</td>
      <td>10%</td>
      <td>85</td>
      <td>تاج</td>
      <td>4601</td>
      <td>2025-10-09</td>
    </tr>
  </tbody>
</table>
```

---

## 📈 إحصائيات المخزن

### عرض ملخص المخزن

```http
GET /inventory/inventories/
```

```json
{
  "results": [
    {
      "id": 1,
      "name": "Auto created Main Inventory",
      "type": "main",
      "type_label": "Main",
      "total_items": 5,           // عدد الأصناف
      "total_quantity": 485,      // الكمية الإجمالية
      "total_purchase_price": 43650.00,  // قيمة الشراء
      "total_selling_price": 46075.00    // قيمة البيع المتوقعة
    }
  ]
}
```

---

## 🔗 الربط مع الأنظمة الأخرى

### الحصول على عناصر فاتورة شراء معينة

```http
# عرض الفاتورة
GET /invoices/purchase-invoices/1/

# عرض عناصر المخزن المرتبطة بها
GET /inventory/inventory-items/?purchase_invoice_item__invoice=1
```

---

## ⚠️ ملاحظات مهمة

### 1. الحقول الجديدة قد تكون null

إذا كان العنصر مُضاف يدوياً (ليس من فاتورة شراء):
```json
{
  "supplier_name": null,
  "supplier_invoice_number": null,
  "purchase_date": null
}
```

### 2. الأداء

لتحسين الأداء، استخدم pagination:
```http
GET /inventory/inventory-items/?p=1&ps=50
```

### 3. الصلاحيات

الوصول للمخزون محمي حسب الدور:
- **Sales**: قراءة فقط
- **Data Entry**: قراءة فقط
- **Manager**: قراءة + كتابة

---

## 📋 الخلاصة

الآن لديك **تقرير كامل** لكل صنف في المخزن يحتوي على:

✅ **اسم الصنف** - `product.name`  
✅ **السعر** - `purchase_price`, `selling_price`  
✅ **الخصم** - `purchase_discount_percentage`  
✅ **الكمية** - `remaining_quantity`  
✅ **المورد** - `supplier_name`  
✅ **رقم فاتورة المورد** - `supplier_invoice_number`  
✅ **تاريخ الشراء** - `purchase_date`  

---

**جاهز للاستخدام!** 🎉

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.3.0

