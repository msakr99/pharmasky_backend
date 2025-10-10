# سجل التحديثات - فواتير مرتجع الشراء
# Purchase Return Invoices Changelog

## 📅 التاريخ: 2025-10-10 | الإصدار: 1.2.0

### ✨ ميزة جديدة: استخدام رقم فاتورة المورد

#### ما الجديد؟

**قبل التحديث** ❌:
```http
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": 1,  // يجب معرفة معرف فاتورة المرتجع
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

إذا لم تكن الفاتورة موجودة → **خطأ**!

**بعد التحديث** ✅:
```http
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",  // ⬅️ رقم فاتورة المورد مباشرة!
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

**النظام يقوم تلقائياً بـ**:
1. البحث عن فاتورة الشراء برقم المورد "4601"
2. إنشاء فاتورة مرتجع جديدة (إذا لم تكن موجودة)
3. إضافة العنصر للفاتورة

---

## 🎯 الفوائد

### 1. سهولة الاستخدام
```
قبل: يجب البحث عن معرف فاتورة المرتجع
بعد: استخدم رقم فاتورة المورد مباشرة
```

### 2. إنشاء تلقائي
```
قبل: يجب إنشاء فاتورة المرتجع يدوياً أولاً
بعد: تُنشأ تلقائياً عند الحاجة
```

### 3. مرونة أكبر
```
يقبل:
- رقم فاتورة المورد: "4601"
- معرف فاتورة المرتجع: "5"
```

---

## 📝 التفاصيل التقنية

### الكود المعدل

**الملف**: `invoices/serializers.py`  
**الـ Serializer**: `PurchaseReturnInvoiceItemCreateSerializer`

#### التغييرات:

```python
# قبل
invoice = serializers.PrimaryKeyRelatedField(
    queryset=PurchaseReturnInvoice.objects.exclude(
        status=PurchaseReturnInvoiceStatusChoice.CLOSED
    )
)

# بعد
invoice = serializers.CharField()  # يقبل نص

def validate_invoice(self, value):
    # محاولة كمعرف رقمي
    try:
        invoice_id = int(value)
        invoice = PurchaseReturnInvoice.objects.filter(id=invoice_id).first()
        if invoice:
            return invoice
    except (ValueError, TypeError):
        pass
    
    # محاولة كرقم فاتورة مورد
    purchase_invoice = PurchaseInvoice.objects.filter(
        supplier_invoice_number=value,
        status=PurchaseInvoiceStatusChoice.CLOSED
    ).first()
    
    if purchase_invoice:
        # إنشاء أو الحصول على فاتورة مرتجع
        invoice, created = PurchaseReturnInvoice.objects.get_or_create(
            user=purchase_invoice.user,
            status=PurchaseReturnInvoiceStatusChoice.PLACED,
            defaults={...}
        )
        return invoice
    
    raise ValidationError("الفاتورة غير موجودة")
```

---

## 🧪 أمثلة الاستخدام

### مثال 1: إضافة عنصر مرتجع بسيط

```http
POST http://129.212.140.152/invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",
  "purchase_invoice_item": 1,
  "quantity": 5
}
```

**الاستجابة**:
```json
{
  "id": 1,
  "invoice_obj": {
    "id": 1,  // ⬅️ تم إنشاؤه تلقائياً
    "user": {...},
    "status": "placed",
    "items_count": 1,
    "total_quantity": 5,
    "total_price": "450.00"
  },
  "purchase_invoice_item": {...},
  "quantity": 5,
  "sub_total": "450.00"
}
```

---

### مثال 2: إضافة عدة عناصر لنفس الفاتورة

```http
# العنصر الأول
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",
  "purchase_invoice_item": 1,
  "quantity": 5
}

# العنصر الثاني - نفس الفاتورة
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",  // ⬅️ نفس رقم المورد
  "purchase_invoice_item": 2,
  "quantity": 3
}
```

**النتيجة**: عنصران في نفس فاتورة المرتجع

---

### مثال 3: استخدام معرف الفاتورة مباشرة

```http
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": "1",  // ⬅️ معرف فاتورة المرتجع
  "purchase_invoice_item": 3,
  "quantity": 2
}
```

---

## ⚠️ ملاحظات مهمة

### 1. فاتورة الشراء يجب أن تكون مغلقة

```
رقم المورد "4601" يجب أن يكون لفاتورة شراء مغلقة (status: closed)
```

### 2. إنشاء فاتورة واحدة لكل مستخدم

```
get_or_create يبحث عن فاتورة مرتجع:
- نفس المستخدم
- حالة "placed"

إذا وُجدت → يستخدمها
إذا لم تُوجد → ينشئ واحدة جديدة
```

### 3. يمكن الخلط بين الطريقتين

```http
# استخدام رقم المورد
{"invoice": "4601"}

# ثم معرف الفاتورة
{"invoice": "1"}

# كلاهما صحيح ويعمل
```

---

## 🔄 التوافق مع الإصدارات السابقة

✅ **متوافق تماماً**

الكود القديم يستمر بالعمل:
```http
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": 1,  // ⬅️ لا يزال يعمل
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

---

## 📚 المراجع

- [PURCHASE_RETURN_GUIDE.md](./PURCHASE_RETURN_GUIDE.md) - الدليل الكامل
- [invoices/serializers.py](./serializers.py) - الكود المصدري
- [CHANGELOG.md](./CHANGELOG.md) - سجل التغييرات العام

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.2.0  
**الحالة**: ✅ مستقر ومختبر

