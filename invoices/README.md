# تطبيق الفواتير | Invoices Application

## 📋 نظرة عامة | Overview

تطبيق Django لإدارة فواتير الشراء والبيع للصيدليات، مع حساب تلقائي للخصومات والأرباح.

A Django application for managing purchase and sale invoices for pharmacies, with automatic discount and profit calculations.

---

## 🆕 آخر التحديثات | Latest Updates

### الإصدار 1.1.0 (2025-10-10)

#### ✨ ميزات جديدة | New Features

1. **متوسط خصم فاتورة الشراء**
   - `total_public_price` - إجمالي السعر قبل الخصم
   - `average_purchase_discount_percentage` - متوسط نسبة خصم الشراء المرجح

2. **إصلاحات**
   - 🐛 إصلاح خطأ 500 عند إغلاق فاتورة لمستخدم بدون حساب مالي
   - يتم الآن إنشاء الحساب المالي تلقائياً

#### 📚 توثيق جديد

- [PURCHASE_DISCOUNT_DOCUMENTATION.md](./PURCHASE_DISCOUNT_DOCUMENTATION.md) - توثيق متوسط خصم الشراء
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - مرجع سريع
- [EXAMPLES.md](./EXAMPLES.md) - أمثلة عملية

---

## 📦 المميزات | Features

### فواتير الشراء | Purchase Invoices

- ✅ إنشاء فواتير شراء من الموردين
- ✅ حساب تلقائي لمتوسط خصم الشراء
- ✅ حساب إجمالي السعر قبل وبعد الخصم
- ✅ تتبع حالة العناصر (موضوعة، مستلمة، مرفوضة)
- ✅ ربط بالعروض (Offers)
- ✅ تسجيل معاملات مالية عند الإغلاق

### فواتير البيع | Sale Invoices

- ✅ إنشاء فواتير بيع للصيدليات
- ✅ حساب تلقائي للأرباح
- ✅ حساب متوسط خصم البيع
- ✅ ربط بعناصر فواتير الشراء
- ✅ تتبع الكميات المتبقية
- ✅ إدارة العناصر المحذوفة والمرتجعة

### حسابات مالية | Financial Accounts

- ✅ إنشاء تلقائي للحسابات المالية
- ✅ تسجيل المعاملات المالية
- ✅ تتبع الرصيد والحد الائتماني
- ✅ ربط المعاملات بالفواتير والمدفوعات

---

## 🚀 البدء السريع | Quick Start

### 1. إنشاء فاتورة شراء | Create Purchase Invoice

```http
POST /invoices/purchase-invoices/create/
Content-Type: application/json

{
  "user": 5,
  "items": [
    {
      "product": 10,
      "quantity": 100,
      "purchase_discount_percentage": 10.00,
      "selling_discount_percentage": 5.00
    }
  ]
}
```

### 2. عرض تفاصيل الفاتورة | View Invoice Details

```http
GET /invoices/purchase-invoices/1/
```

**الحقول المهمة:**
- `total_public_price` - السعر قبل الخصم
- `total_price` - السعر بعد الخصم
- `average_purchase_discount_percentage` - متوسط الخصم

### 3. إغلاق الفاتورة | Close Invoice

```http
PUT /invoices/purchase-invoices/1/change-state/

{
  "supplier_invoice_number": "SUP-2025-001",
  "status": "closed"
}
```

---

## 📊 الحقول المحسوبة | Calculated Fields

### فاتورة الشراء | Purchase Invoice

| الحقل | الوصف | الصيغة |
|-------|-------|--------|
| `total_public_price` | السعر قبل الخصم | `Sum(qty × public_price)` |
| `total_price` | السعر بعد الخصم | `Sum(qty × purchase_price)` |
| `average_purchase_discount_percentage` | متوسط خصم الشراء | `(discount / public_price) × 100` |

### فاتورة البيع | Sale Invoice

| الحقل | الوصف | الصيغة |
|-------|-------|--------|
| `total_public_price` | السعر قبل الخصم | `Sum(qty × public_price)` |
| `total_price` | السعر بعد الخصم | `Sum(qty × selling_price)` |
| `total_purchase_cost` | تكلفة الشراء | `Sum(qty × purchase_price)` |
| `total_profit` | الربح | `total_price - total_purchase_cost` |
| `average_discount_percentage` | متوسط خصم البيع | `(discount / public_price) × 100` |

---

## 📖 التوثيق الكامل | Full Documentation

### للمستخدمين | For Users

1. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - مرجع سريع
   - الحقول المتاحة
   - الحسابات الأساسية
   - API Endpoints

2. **[EXAMPLES.md](./EXAMPLES.md)** - أمثلة عملية
   - دورة حياة الفاتورة
   - مقارنة الموردين
   - تقارير شهرية

3. **[PURCHASE_DISCOUNT_DOCUMENTATION.md](./PURCHASE_DISCOUNT_DOCUMENTATION.md)**
   - شرح متوسط خصم الشراء
   - أمثلة حسابية مفصلة
   - حالات خاصة

4. **[AVERAGE_DISCOUNT_DOCUMENTATION.md](./AVERAGE_DISCOUNT_DOCUMENTATION.md)**
   - شرح متوسط خصم البيع
   - الفرق بين خصم الشراء والبيع

### للمطورين | For Developers

1. **[CHANGELOG.md](./CHANGELOG.md)** - سجل التغييرات
2. **[CALCULATED_FIELDS_README.md](./CALCULATED_FIELDS_README.md)** - الحقول المحسوبة
3. **[QUANTITY_REDUCTION_TRACKING.md](./QUANTITY_REDUCTION_TRACKING.md)** - تتبع تقليل الكميات
4. **[PDF_FIXES_DOCUMENTATION.md](./PDF_FIXES_DOCUMENTATION.md)** - إصلاحات PDF

---

## 🔗 API Endpoints

### فواتير الشراء | Purchase Invoices

```
GET    /invoices/purchase-invoices/                  قائمة الفواتير
POST   /invoices/purchase-invoices/create/           إنشاء فاتورة
GET    /invoices/purchase-invoices/{id}/             تفاصيل فاتورة
PUT    /invoices/purchase-invoices/{id}/change-state/ تغيير الحالة
```

### عناصر فاتورة الشراء | Purchase Invoice Items

```
GET    /invoices/purchase-invoice-items/             قائمة العناصر
POST   /invoices/purchase-invoice-items/create/      إضافة عنصر
PUT    /invoices/purchase-invoice-items/{id}/change-state/ تغيير حالة عنصر
DELETE /invoices/purchase-invoice-items/{id}/destroy/ حذف عنصر
```

### فواتير البيع | Sale Invoices

```
GET    /invoices/sale-invoices/                      قائمة الفواتير
POST   /invoices/sale-invoices/create/               إنشاء فاتورة
GET    /invoices/sale-invoices/{id}/                 تفاصيل فاتورة
PUT    /invoices/sale-invoices/{id}/change-state/    تغيير الحالة
```

---

## 🎯 حالات الاستخدام | Use Cases

### 1. تحليل تكلفة الشراء

```python
invoice = get_invoice(1)
saved = invoice["total_public_price"] - invoice["total_price"]
print(f"وفرت: {saved} جنيه ({invoice['average_purchase_discount_percentage']}%)")
```

### 2. مقارنة الموردين

```python
supplier_a = {"average_purchase_discount_percentage": 12.50}
supplier_b = {"average_purchase_discount_percentage": 15.00}

if supplier_b["average_purchase_discount_percentage"] > supplier_a["average_purchase_discount_percentage"]:
    print("المورد B أفضل ✅")
```

### 3. حساب الربحية

```python
sale = get_sale_invoice(1)
profit_margin = (sale["total_profit"] / sale["total_price"]) * 100
print(f"هامش الربح: {profit_margin:.2f}%")
```

---

## ⚙️ التكوين | Configuration

### Models

- `PurchaseInvoice` - فاتورة الشراء
- `PurchaseInvoiceItem` - عنصر فاتورة الشراء
- `SaleInvoice` - فاتورة البيع
- `SaleInvoiceItem` - عنصر فاتورة البيع
- `PurchaseReturnInvoice` - فاتورة مرتجع شراء
- `SaleReturnInvoice` - فاتورة مرتجع بيع

### Serializers

- `PurchaseInvoiceReadSerializer` - عرض فاتورة الشراء
- `PurchaseInvoiceCreateSerializer` - إنشاء فاتورة الشراء
- `SaleInvoiceReadSerializer` - عرض فاتورة البيع
- `SaleInvoiceCreateSerializer` - إنشاء فاتورة البيع

### Views

- `PurchaseInvoiceListView` - قائمة فواتير الشراء
- `PurchaseInvoiceStateUpdateAPIView` - تحديث حالة فاتورة الشراء
- `SaleInvoiceListAPIView` - قائمة فواتير البيع

---

## 🔍 البحث والفلترة | Search & Filtering

### فواتير الشراء

```http
GET /invoices/purchase-invoices/?status=closed
GET /invoices/purchase-invoices/?search=SUP-001
GET /invoices/purchase-invoices/?o=-created_at
```

### فواتير البيع

```http
GET /invoices/sale-invoices/?status=placed
GET /invoices/sale-invoices/?user=5
GET /invoices/sale-invoices/?p=2&ps=20
```

---

## 🛡️ الصلاحيات | Permissions

### فواتير الشراء

- **القراءة**: Sales, Manager, Area Manager
- **الإنشاء**: Sales
- **التعديل**: Sales (صاحب الفاتورة)

### فواتير البيع

- **القراءة**: Sales, Manager, Area Manager
- **الإنشاء**: Sales
- **التعديل**: Sales (صاحب الفاتورة)

---

## ⚠️ ملاحظات هامة | Important Notes

### 1. إنشاء الحساب المالي

- يتم إنشاء الحساب المالي تلقائياً عند الحاجة
- لا حاجة لإنشاء الحساب يدوياً

### 2. إغلاق الفاتورة

- يجب أن تكون جميع العناصر في حالة `received`
- يجب إدخال `supplier_invoice_number`
- لا يمكن التراجع بعد الإغلاق

### 3. الحسابات

- جميع الحسابات تستخدم `Decimal` للدقة
- النتائج مقربة لـ 2 منزلة عشرية
- المتوسطات مرجحة (weighted average)

---

## 🐛 إصلاح المشاكل | Troubleshooting

### خطأ 500 عند إغلاق الفاتورة

**السبب**: المستخدم ليس لديه حساب مالي  
**الحل**: ✅ تم الإصلاح! يتم إنشاء الحساب تلقائياً

### خطأ "Cannot close invoice with pending action items"

**السبب**: هناك عناصر لم يتم استلامها  
**الحل**: حدّث حالة جميع العناصر إلى `received`

### خطأ "This field is required" (supplier_invoice_number)

**السبب**: لم يتم إرسال رقم فاتورة المورد  
**الحل**: أضف `supplier_invoice_number` في الطلب

---

## 📞 الدعم | Support

للمساعدة:
1. راجع التوثيق المناسب من القائمة أعلاه
2. تحقق من الأمثلة في [EXAMPLES.md](./EXAMPLES.md)
3. اتصل بفريق التطوير

---

## 📝 الترخيص | License

هذا المشروع مملوك لـ [اسم الشركة]

---

## 👥 المساهمون | Contributors

- المطور الرئيسي: [الاسم]
- آخر تحديث: 2025-10-10
- الإصدار: 1.1.0

---

## 🗺️ خارطة الطريق | Roadmap

### قيد التطوير | In Progress

- [ ] تقارير تفصيلية للموردين
- [ ] تنبيهات تاريخ انتهاء الصلاحية
- [ ] تكامل مع نظام المخزون

### مخطط مستقبلي | Future Plans

- [ ] واجهة مستخدم للتقارير
- [ ] تصدير إلى Excel/PDF
- [ ] إشعارات البريد الإلكتروني
- [ ] API للتكامل مع أنظمة خارجية

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.1.0  
**الحالة**: ✅ مستقر ومختبر

