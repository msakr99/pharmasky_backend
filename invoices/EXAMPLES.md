# أمثلة عملية - فواتير الشراء والبيع
# Practical Examples - Purchase & Sale Invoices

## مثال كامل: دورة حياة فاتورة الشراء
## Complete Example: Purchase Invoice Lifecycle

### 1. إنشاء فاتورة شراء | Create Purchase Invoice

**Request:**
```http
POST /invoices/purchase-invoices/create/
Authorization: Token your-token-here
Content-Type: application/json

{
  "user": 5,
  "items": [
    {
      "product": 10,
      "quantity": 100,
      "purchase_discount_percentage": 10.00,
      "selling_discount_percentage": 5.00,
      "product_expiry_date": "2026-12-31",
      "operating_number": "BATCH-001"
    },
    {
      "product": 20,
      "quantity": 50,
      "purchase_discount_percentage": 15.00,
      "selling_discount_percentage": 8.00,
      "product_expiry_date": "2027-06-30",
      "operating_number": "BATCH-002"
    }
  ]
}
```

**Response:**
```json
{
  "id": 123,
  "user": {
    "id": 5,
    "name": "صيدلية النور",
    "username": "+201234567890"
  },
  "supplier_invoice_number": "",
  "items_count": 2,
  "total_quantity": 150,
  "total_price": "13500.00",
  "total_public_price": "15000.00",
  "average_purchase_discount_percentage": "11.67",
  "status": "placed",
  "status_label": "Placed",
  "created_at": "2025-10-10T14:30:00Z",
  "items": [
    {
      "id": 501,
      "product": {
        "id": 10,
        "name": "Paracetamol 500mg",
        "public_price": "100.00"
      },
      "quantity": 100,
      "purchase_discount_percentage": "10.00",
      "purchase_price": "90.00",
      "selling_discount_percentage": "5.00",
      "selling_price": "95.00",
      "sub_total": "9000.00",
      "product_expiry_date": "2026-12-31",
      "operating_number": "BATCH-001",
      "status": "placed"
    },
    {
      "id": 502,
      "product": {
        "id": 20,
        "name": "Ibuprofen 400mg",
        "public_price": "200.00"
      },
      "quantity": 50,
      "purchase_discount_percentage": "15.00",
      "purchase_price": "170.00",
      "selling_discount_percentage": "8.00",
      "selling_price": "184.00",
      "sub_total": "8500.00",
      "product_expiry_date": "2027-06-30",
      "operating_number": "BATCH-002",
      "status": "placed"
    }
  ]
}
```

### 2. تحليل التكلفة | Cost Analysis

```python
# حساب التوفير من المورد
total_public = 15000.00  # السعر قبل الخصم
total_price = 13500.00   # السعر بعد الخصم
discount_avg = 11.67     # متوسط الخصم %

saved_amount = total_public - total_price  # 1500.00 جنيه
print(f"وفرت من المورد: {saved_amount} جنيه")
print(f"متوسط خصم الشراء: {discount_avg}%")

# التفصيل حسب المنتج
product_a_saved = (100 * 100) * 0.10  # 1000.00
product_b_saved = (50 * 200) * 0.15   # 1500.00
total_saved = product_a_saved + product_b_saved  # 2500.00 ❌ خطأ!

# الطريقة الصحيحة (متوسط مرجح)
# Product A: 10000 * 10% = 1000
# Product B: 10000 * 15% = 1500
# Total: (1000 + 1500) / (10000 + 10000) * 100 = 12.5% ❌

# لماذا 11.67%؟
# لأن السعر الفعلي للشراء مختلف:
# Product A: 100 × 90 = 9000 (وفر 1000)
# Product B: 50 × 170 = 8500 (وفر 1500)
# Total saved: 1500, Total public: 15000
# Average: (1500 / 15000) * 100 = 10% ✅
```

### 3. إغلاق الفاتورة | Close Invoice

**Request:**
```http
PUT /invoices/purchase-invoices/123/change-state/
Authorization: Token your-token-here
Content-Type: application/json

{
  "supplier_invoice_number": "SUP-2025-001",
  "status": "closed"
}
```

**Response:**
```json
{
  "supplier_invoice_number": "SUP-2025-001",
  "status": "closed",
  "status_label": "Closed"
}
```

**ماذا يحدث عند الإغلاق؟**
1. ✅ يتم التحقق من أن جميع العناصر في حالة `received`
2. ✅ يتم إنشاء حساب مالي للمستخدم (إذا لم يكن موجودًا)
3. ✅ يتم تسجيل معاملة مالية بمبلغ 13500 جنيه
4. ✅ يتم تحديث رصيد الحساب
5. ✅ لا يمكن تعديل الفاتورة بعد الإغلاق

---

## مثال: مقارنة موردين | Example: Compare Suppliers

### السيناريو | Scenario
لديك نفس الطلب من مورّدين مختلفين. أيهما أفضل؟

### المورد A | Supplier A
```json
{
  "id": 100,
  "total_public_price": "20000.00",
  "total_price": "17000.00",
  "average_purchase_discount_percentage": "15.00"
}
```

### المورد B | Supplier B
```json
{
  "id": 101,
  "total_public_price": "20000.00",
  "total_price": "16500.00",
  "average_purchase_discount_percentage": "17.50"
}
```

### التحليل | Analysis
```python
supplier_a = {
    "total_public": 20000.00,
    "total_price": 17000.00,
    "discount": 15.00,
    "saved": 3000.00
}

supplier_b = {
    "total_public": 20000.00,
    "total_price": 16500.00,
    "discount": 17.50,
    "saved": 3500.00
}

# المقارنة
diff = supplier_b["saved"] - supplier_a["saved"]  # 500.00
print(f"المورد B يوفر {diff} جنيه إضافي")
print(f"فرق الخصم: {supplier_b['discount'] - supplier_a['discount']}%")

# القرار
print("اختر المورد B ✅")
```

---

## مثال: تقرير شهري | Example: Monthly Report

### جمع البيانات | Collect Data

```python
from django.db.models import Sum, Avg
from invoices.models import PurchaseInvoice
from datetime import datetime

# فواتير شهر أكتوبر 2025
invoices = PurchaseInvoice.objects.filter(
    created_at__year=2025,
    created_at__month=10,
    status='closed'
)

# الإحصائيات
stats = {
    "count": invoices.count(),
    "total_quantity": invoices.aggregate(Sum('total_quantity'))['total_quantity__sum'],
    "total_price": invoices.aggregate(Sum('total_price'))['total_price__sum'],
}

print(f"عدد الفواتير: {stats['count']}")
print(f"إجمالي الكميات: {stats['total_quantity']}")
print(f"إجمالي المبلغ: {stats['total_price']} جنيه")
```

### حساب متوسط الخصم الشهري

```python
from invoices.serializers import PurchaseInvoiceReadSerializer

total_discount_percentage = 0
for invoice in invoices:
    serializer = PurchaseInvoiceReadSerializer(invoice)
    total_discount_percentage += float(
        serializer.data['average_purchase_discount_percentage']
    )

monthly_avg_discount = total_discount_percentage / invoices.count()
print(f"متوسط خصم الشراء للشهر: {monthly_avg_discount:.2f}%")
```

### التقرير الكامل

```python
report = {
    "month": "أكتوبر 2025",
    "invoices_count": 50,
    "total_items": 5000,
    "total_public_price": 500000.00,
    "total_price": 425000.00,
    "total_saved": 75000.00,
    "average_discount": 15.00,
    "top_supplier": "شركة الشفاء للأدوية",
    "top_product": "Paracetamol 500mg"
}

print("=" * 50)
print(f"📊 تقرير شراء {report['month']}")
print("=" * 50)
print(f"عدد الفواتير: {report['invoices_count']}")
print(f"إجمالي الأصناف: {report['total_items']}")
print(f"المبلغ قبل الخصم: {report['total_public_price']:,.2f} جنيه")
print(f"المبلغ المدفوع: {report['total_price']:,.2f} جنيه")
print(f"إجمالي التوفير: {report['total_saved']:,.2f} جنيه")
print(f"متوسط الخصم: {report['average_discount']}%")
print("=" * 50)
```

---

## مثال: من الشراء إلى البيع | Example: Purchase to Sale

### 1. شراء المنتج | Purchase Product

```json
// POST /invoices/purchase-invoices/create/
{
  "product": 10,
  "quantity": 100,
  "purchase_discount_percentage": 10.00,  // خصم من المورد
  "selling_discount_percentage": 5.00     // خصم للصيدلية
}

// Response
{
  "purchase_price": 90.00,   // اشتريت بـ 90 بدلاً من 100
  "selling_price": 95.00     // ستبيع بـ 95 بدلاً من 100
}
```

### 2. بيع المنتج | Sell Product

```json
// POST /invoices/sale-invoices/create/
{
  "items": [
    {
      "purchase_invoice_item": 501,  // العنصر من فاتورة الشراء
      "quantity": 50
    }
  ]
}

// Response - Sale Invoice
{
  "total_price": 4750.00,           // 50 × 95
  "total_public_price": 5000.00,    // 50 × 100
  "total_purchase_cost": 4500.00,   // 50 × 90
  "total_profit": 250.00,           // 4750 - 4500
  "average_discount_percentage": 5.00
}
```

### 3. تحليل الربحية | Profitability Analysis

```python
# البيانات
purchase = {
    "quantity": 100,
    "purchase_price": 90.00,
    "total_cost": 9000.00,
    "purchase_discount": "10.00%"
}

sale = {
    "quantity": 50,
    "selling_price": 95.00,
    "total_revenue": 4750.00,
    "selling_discount": "5.00%"
}

# الحسابات
profit_per_unit = 95.00 - 90.00  # 5.00 جنيه
total_profit = sale["total_revenue"] - (50 * 90.00)  # 250.00 جنيه
profit_margin = (250.00 / 4750.00) * 100  # 5.26%

# المتبقي في المخزون
remaining = purchase["quantity"] - sale["quantity"]  # 50 وحدة
remaining_value = remaining * 90.00  # 4500 جنيه

print(f"الربح لكل وحدة: {profit_per_unit} جنيه")
print(f"إجمالي الربح: {total_profit} جنيه")
print(f"هامش الربح: {profit_margin:.2f}%")
print(f"متبقي في المخزون: {remaining} وحدة ({remaining_value} جنيه)")
```

---

## مثال: معالجة الأخطاء | Example: Error Handling

### خطأ: إغلاق فاتورة بدون رقم مورد

**Request:**
```http
PUT /invoices/purchase-invoices/123/change-state/
{
  "status": "closed"
  // ❌ لم يتم إرسال supplier_invoice_number
}
```

**Response (400 Bad Request):**
```json
{
  "supplier_invoice_number": [
    "This field is required."
  ]
}
```

### خطأ: تغيير الحالة إلى نفس القيمة

**Request:**
```http
PUT /invoices/purchase-invoices/123/change-state/
{
  "supplier_invoice_number": "SUP-001",
  "status": "placed"  // ❌ الحالة الحالية already placed
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Status is already set to this value."
}
```

### خطأ: إغلاق فاتورة مع عناصر غير مستلمة

**Request:**
```http
PUT /invoices/purchase-invoices/123/change-state/
{
  "supplier_invoice_number": "SUP-001",
  "status": "closed"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Cannot close invoice with pending action items."
}
```

**الحل:**
```http
// أولاً: تحديث حالة جميع العناصر
PUT /invoices/purchase-invoice-items/501/change-state/
{
  "status": "received"
}

PUT /invoices/purchase-invoice-items/502/change-state/
{
  "status": "received"
}

// ثانياً: إغلاق الفاتورة
PUT /invoices/purchase-invoices/123/change-state/
{
  "supplier_invoice_number": "SUP-001",
  "status": "closed"
}
// ✅ Success!
```

---

## نصائح وأفضل الممارسات | Tips & Best Practices

### 1. احفظ رقم المورد دائماً
```python
# ✅ جيد
{
  "supplier_invoice_number": "SUP-2025-001",
  "status": "closed"
}

# ❌ سيء
{
  "supplier_invoice_number": "",  # فارغ!
  "status": "closed"
}
```

### 2. تحقق من الحالة قبل التعديل
```python
invoice = get_invoice(123)
if invoice["status"] == "closed":
    print("لا يمكن تعديل فاتورة مغلقة!")
```

### 3. استخدم المتوسط المرجح للمقارنة
```python
# ❌ خطأ: متوسط بسيط
avg = (discount_a + discount_b) / 2

# ✅ صحيح: متوسط مرجح
avg = (total_discount / total_public_price) * 100
```

### 4. راجع الفاتورة قبل الإغلاق
```python
def validate_before_close(invoice_id):
    invoice = get_invoice(invoice_id)
    
    # تحقق من العناصر
    pending = [item for item in invoice["items"] 
               if item["status"] != "received"]
    
    if pending:
        print(f"⚠️ {len(pending)} عنصر لم يُستلم بعد!")
        return False
    
    # تحقق من رقم المورد
    if not invoice["supplier_invoice_number"]:
        print("⚠️ يجب إدخال رقم فاتورة المورد!")
        return False
    
    return True

if validate_before_close(123):
    close_invoice(123)
```

---

## الأسئلة الشائعة | FAQ

### س: لماذا يختلف `average_purchase_discount_percentage` عن متوسط الخصومات؟

**ج**: لأنه متوسط مرجح، يأخذ في الاعتبار كمية وسعر كل منتج.

**مثال:**
- منتج A: 1 وحدة × 1000 جنيه × 10% خصم = 100 جنيه توفير
- منتج B: 100 وحدة × 10 جنيه × 50% خصم = 500 جنيه توفير

المتوسط البسيط = (10% + 50%) / 2 = **30%** ❌  
المتوسط المرجح = (100 + 500) / (1000 + 1000) × 100 = **30%** ✅

(في هذا المثال تصادف أن يكون نفسه، لكن غالباً يختلف!)

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.1.0

