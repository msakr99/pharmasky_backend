# توثيق متوسط خصم فاتورة الشراء | Purchase Invoice Average Discount Documentation

## نظرة عامة | Overview

### بالعربية
تم إضافة حقلين جديدين لـ **فاتورة الشراء** (`PurchaseInvoice`) لحساب:
1. **`total_public_price`**: إجمالي سعر الجمهور (قبل الخصم) لجميع عناصر الفاتورة
2. **`average_purchase_discount_percentage`**: متوسط نسبة خصم الشراء المرجح لجميع عناصر الفاتورة

### In English
Two new fields have been added to **Purchase Invoice** (`PurchaseInvoice`) to calculate:
1. **`total_public_price`**: Total public price (before discount) for all items
2. **`average_purchase_discount_percentage`**: Weighted average purchase discount percentage for all items

---

## الحقول المحسوبة | Calculated Fields

### 1. إجمالي سعر الجمهور | Total Public Price

**الصيغة | Formula:**
```
total_public_price = Sum(quantity × public_price)
```

**مثال | Example:**

فاتورة تحتوي على:
- 10 وحدات من منتج A (سعر الجمهور: 100 جنيه)
- 5 وحدات من منتج B (سعر الجمهور: 200 جنيه)

```
total_public_price = (10 × 100) + (5 × 200)
                   = 1000 + 1000
                   = 2000.00 EGP
```

---

### 2. متوسط نسبة خصم الشراء | Average Purchase Discount Percentage

**الصيغة | Formula:**
```
average_purchase_discount_percentage = 
    (Sum(quantity × purchase_discount_percentage × public_price) / Sum(quantity × public_price)) × 100
```

**كيفية الحساب | Calculation Steps:**

1. لكل عنصر في الفاتورة:
   - `quantity_price` = الكمية × سعر الجمهور
   - `quantity_discount` = quantity_price × (نسبة خصم الشراء / 100)

2. جمع القيم:
   - `total_public_price` = مجموع كل quantity_price
   - `total_discount` = مجموع كل quantity_discount

3. حساب المتوسط:
   - `average_discount` = (total_discount / total_public_price) × 100

**مثال عملي | Practical Example:**

| المنتج | الكمية | سعر الجمهور | خصم الشراء% | سعر الشراء |
|--------|--------|-------------|-------------|------------|
| A      | 10     | 100         | 10%         | 90         |
| B      | 5      | 200         | 15%         | 170        |

**الحسابات:**
```
المنتج A:
  quantity_price = 10 × 100 = 1000
  quantity_discount = 1000 × (10/100) = 100

المنتج B:
  quantity_price = 5 × 200 = 1000
  quantity_discount = 1000 × (15/100) = 150

الإجمالي:
  total_public_price = 1000 + 1000 = 2000
  total_discount = 100 + 150 = 250
  
متوسط الخصم:
  average_discount = (250 / 2000) × 100 = 12.50%
```

---

## استخدام API | API Usage

### طلب فاتورة شراء | Get Purchase Invoice

**Request:**
```http
GET /invoices/purchase-invoices/1/
Authorization: Token your-token-here
```

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "name": "صيدلية النور",
    "username": "+201234567890"
  },
  "supplier_invoice_number": "4601",
  "items_count": 2,
  "total_quantity": 15,
  "total_price": "1350.00",
  "total_public_price": "2000.00",
  "average_purchase_discount_percentage": "12.50",
  "status": "placed",
  "status_label": "Placed",
  "created_at": "2025-10-10T12:00:00Z",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 10,
        "name": "Paracetamol 500mg",
        "public_price": "100.00"
      },
      "quantity": 10,
      "purchase_discount_percentage": "10.00",
      "purchase_price": "90.00",
      "sub_total": "900.00"
    },
    {
      "id": 2,
      "product": {
        "id": 20,
        "name": "Ibuprofen 400mg",
        "public_price": "200.00"
      },
      "quantity": 5,
      "purchase_discount_percentage": "15.00",
      "purchase_price": "170.00",
      "sub_total": "850.00"
    }
  ]
}
```

---

## الفرق بين خصم الشراء وخصم البيع | Purchase vs Selling Discount

### خصم الشراء (Purchase Discount)
- **الاستخدام**: عند شراء المنتجات من المورد
- **الحقل**: `purchase_discount_percentage`
- **التأثير**: يخفض سعر الشراء من المورد
- **المتوسط**: `average_purchase_discount_percentage`

### خصم البيع (Selling Discount)
- **الاستخدام**: عند بيع المنتجات للصيدليات
- **الحقل**: `selling_discount_percentage`
- **التأثير**: يخفض سعر البيع للعميل
- **المتوسط**: `average_discount_percentage` (في فواتير البيع)

---

## حالات خاصة | Special Cases

### 1. فاتورة فارغة | Empty Invoice
```json
{
  "total_public_price": "0.00",
  "average_purchase_discount_percentage": "0.00"
}
```

### 2. بدون خصم | No Discount
إذا كانت جميع العناصر بدون خصم (0%):
```json
{
  "total_public_price": "2000.00",
  "average_purchase_discount_percentage": "0.00"
}
```

### 3. خصم كامل | Full Discount
إذا كانت جميع العناصر بخصم 100%:
```json
{
  "total_public_price": "2000.00",
  "average_purchase_discount_percentage": "100.00",
  "total_price": "0.00"
}
```

---

## استخدامات عملية | Practical Use Cases

### 1. تحليل تكلفة الشراء
```python
# حساب مبلغ الخصم الفعلي
discount_amount = total_public_price - total_price
print(f"وفرت من الموردين: {discount_amount} جنيه")
print(f"متوسط نسبة التوفير: {average_purchase_discount_percentage}%")
```

### 2. مقارنة الموردين
```python
# مقارنة خصومات موردين مختلفين
supplier_a_discount = 12.50  # %
supplier_b_discount = 15.00  # %

if supplier_b_discount > supplier_a_discount:
    print("المورد B يقدم خصم أفضل")
```

### 3. تقارير الشراء الشهرية
```python
# حساب متوسط الخصم لجميع فواتير الشهر
invoices = PurchaseInvoice.objects.filter(
    created_at__month=10,
    status='closed'
)

total_discount = sum(i.average_purchase_discount_percentage for i in invoices)
monthly_avg = total_discount / invoices.count()
print(f"متوسط خصم الشراء للشهر: {monthly_avg}%")
```

---

## ملاحظات هامة | Important Notes

1. **الأداء | Performance**: 
   - الحقول محسوبة عند الطلب (SerializerMethodField)
   - لا يتم حفظها في قاعدة البيانات
   - تستخدم `select_related('product')` لتحسين الأداء

2. **الدقة | Precision**:
   - جميع الحسابات تستخدم `Decimal` لتجنب أخطاء الفاصلة العائمة
   - النتيجة مقربة لـ 2 منزلة عشرية

3. **التوافقية | Compatibility**:
   - متوافق مع النظام الحالي
   - لا يؤثر على الفواتير القديمة
   - يعمل مع جميع حالات الفاتورة (placed, locked, closed)

---

## الأسئلة الشائعة | FAQ

### س1: لماذا يختلف `total_price` عن `total_public_price`؟
**ج**: `total_public_price` هو السعر قبل الخصم، بينما `total_price` هو السعر بعد تطبيق الخصم.

### س2: هل يمكن أن يكون متوسط الخصم سالبًا؟
**ج**: لا، جميع نسب الخصم يجب أن تكون بين 0 و 100.

### س3: ماذا يحدث إذا كان `total_public_price = 0`؟
**ج**: يتم إرجاع `0.00` لتجنب القسمة على صفر.

---

## التحديثات | Updates

**تاريخ الإضافة**: 2025-10-10
**الإصدار**: 1.0.0
**الحالة**: ✅ مفعّل ومختبر

---

## للمطورين | For Developers

### الكود المصدري | Source Code
```python
# في invoices/serializers.py
class PurchaseInvoiceReadSerializer(BaseModelSerializer):
    average_purchase_discount_percentage = serializers.SerializerMethodField()
    total_public_price = serializers.SerializerMethodField()
    
    def get_average_purchase_discount_percentage(self, instance):
        # انظر الكود الكامل في invoices/serializers.py
        pass
```

### الاختبار | Testing
```python
# اختبار الحساب
invoice = PurchaseInvoice.objects.get(pk=1)
serializer = PurchaseInvoiceReadSerializer(invoice)
data = serializer.data

assert data['total_public_price'] == "2000.00"
assert data['average_purchase_discount_percentage'] == "12.50"
```

---

## المراجع | References

- [AVERAGE_DISCOUNT_DOCUMENTATION.md](./AVERAGE_DISCOUNT_DOCUMENTATION.md) - توثيق خصم البيع
- [CALCULATED_FIELDS_README.md](./CALCULATED_FIELDS_README.md) - الحقول المحسوبة الأخرى
- [API Documentation](../schema.yml) - مخطط API الكامل

