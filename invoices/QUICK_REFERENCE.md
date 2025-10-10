# مرجع سريع - فواتير الشراء والبيع
# Quick Reference - Purchase & Sale Invoices

## فواتير الشراء | Purchase Invoices

### الحقول المتاحة | Available Fields

```json
{
  "id": 1,
  "user": { ... },
  "supplier_invoice_number": "4601",
  "items_count": 2,
  "total_quantity": 15,
  "total_price": "1750.00",              // السعر النهائي بعد الخصم
  "total_public_price": "2000.00",       // ⭐ جديد: السعر قبل الخصم
  "average_purchase_discount_percentage": "12.50",  // ⭐ جديد: متوسط خصم الشراء
  "status": "placed",
  "status_label": "Placed",
  "created_at": "2025-10-10T12:00:00Z",
  "items": [ ... ]
}
```

### الحسابات | Calculations

| الحساب | الصيغة | مثال |
|--------|--------|------|
| السعر قبل الخصم | `Sum(quantity × public_price)` | 2000.00 |
| مبلغ الخصم | `total_public_price - total_price` | 250.00 |
| متوسط خصم الشراء | `(total_discount / total_public_price) × 100` | 12.50% |

---

## فواتير البيع | Sale Invoices

### الحقول المتاحة | Available Fields

```json
{
  "id": 1,
  "user": { ... },
  "items_count": 3,
  "total_quantity": 25,
  "total_price": "2550.00",              // السعر النهائي بعد الخصم
  "total_public_price": "3000.00",       // السعر قبل الخصم
  "total_purchase_cost": "2200.00",      // تكلفة الشراء
  "total_profit": "350.00",              // الربح
  "average_discount_percentage": "15.00", // متوسط خصم البيع
  "status": "placed",
  "items": [ ... ]
}
```

### الحسابات | Calculations

| الحساب | الصيغة | مثال |
|--------|--------|------|
| السعر قبل الخصم | `Sum(quantity × public_price)` | 3000.00 |
| تكلفة الشراء | `Sum(quantity × purchase_price)` | 2200.00 |
| الربح | `total_price - total_purchase_cost` | 350.00 |
| متوسط خصم البيع | `(total_discount / total_public_price) × 100` | 15.00% |

---

## الفرق بين خصم الشراء والبيع
## Difference: Purchase vs Selling Discount

| الجانب | خصم الشراء | خصم البيع |
|-------|------------|-----------|
| **الفاتورة** | Purchase Invoice | Sale Invoice |
| **الحقل** | `purchase_discount_percentage` | `selling_discount_percentage` |
| **من؟** | خصم من المورد | خصم للصيدلية |
| **يؤثر على** | سعر الشراء | سعر البيع |
| **المتوسط** | `average_purchase_discount_percentage` | `average_discount_percentage` |

---

## أمثلة استخدام | Usage Examples

### 1. حساب التوفير من المورد

```python
# GET /invoices/purchase-invoices/1/
response = {
    "total_public_price": "2000.00",
    "total_price": "1750.00",
    "average_purchase_discount_percentage": "12.50"
}

saved_amount = 2000.00 - 1750.00  # 250.00
print(f"وفرت: {saved_amount} جنيه ({response['average_purchase_discount_percentage']}%)")
```

### 2. مقارنة فواتير شراء

```python
invoice_a = {"average_purchase_discount_percentage": "12.50"}
invoice_b = {"average_purchase_discount_percentage": "15.00"}

if float(invoice_b["average_purchase_discount_percentage"]) > float(invoice_a["average_purchase_discount_percentage"]):
    print("الفاتورة B حصلت على خصم أفضل")
```

### 3. تحليل الربحية

```python
# Sale Invoice
sale = {
    "total_price": "2550.00",           # سعر البيع
    "total_purchase_cost": "2200.00",   # تكلفة الشراء
    "total_profit": "350.00"            # الربح
}

profit_margin = (350.00 / 2550.00) * 100  # 13.73%
print(f"هامش الربح: {profit_margin:.2f}%")
```

---

## API Endpoints

### فواتير الشراء | Purchase Invoices

```http
# قائمة الفواتير
GET /invoices/purchase-invoices/

# تفاصيل فاتورة
GET /invoices/purchase-invoices/{id}/

# إنشاء فاتورة
POST /invoices/purchase-invoices/create/

# تغيير حالة الفاتورة
PUT /invoices/purchase-invoices/{id}/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}
```

### فواتير البيع | Sale Invoices

```http
# قائمة الفواتير
GET /invoices/sale-invoices/

# تفاصيل فاتورة
GET /invoices/sale-invoices/{id}/

# إنشاء فاتورة
POST /invoices/sale-invoices/create/

# تغيير حالة الفاتورة
PUT /invoices/sale-invoices/{id}/change-state/
{
  "status": "closed"
}
```

---

## حالات الفاتورة | Invoice States

### فواتير الشراء

- **`placed`** (موضوعة): الحالة الافتراضية
- **`locked`** (مقفلة): جاهزة للإغلاق
- **`closed`** (مغلقة): تم الإغلاق وتسجيل المعاملة المالية

### فواتير البيع

- **`placed`** (موضوعة): الحالة الافتراضية
- **`closed`** (مغلقة): تم الإغلاق

---

## ملاحظات هامة | Important Notes

### ✅ الميزات الجديدة (2025-10-10)

1. **متوسط خصم فاتورة الشراء**
   - `total_public_price`
   - `average_purchase_discount_percentage`

2. **إصلاح خطأ 500**
   - تم إصلاح مشكلة إغلاق الفاتورة عندما لا يوجد حساب مالي للمستخدم
   - الآن يتم إنشاء الحساب تلقائياً

### 📚 التوثيق الكامل

- **فواتير الشراء**: [PURCHASE_DISCOUNT_DOCUMENTATION.md](./PURCHASE_DISCOUNT_DOCUMENTATION.md)
- **فواتير البيع**: [AVERAGE_DISCOUNT_DOCUMENTATION.md](./AVERAGE_DISCOUNT_DOCUMENTATION.md)
- **الحقول المحسوبة**: [CALCULATED_FIELDS_README.md](./CALCULATED_FIELDS_README.md)
- **سجل التغييرات**: [CHANGELOG.md](./CHANGELOG.md)

---

## للدعم | Support

إذا كان لديك أي أسئلة أو مشاكل:
1. راجع التوثيق الكامل
2. تحقق من سجل التغييرات
3. اتصل بفريق التطوير

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.1.0

