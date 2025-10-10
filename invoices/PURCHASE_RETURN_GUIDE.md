# دليل فواتير مرتجع الشراء
# Purchase Return Invoices Guide

## 🆕 ميزة جديدة: استخدام رقم فاتورة المورد!

الآن يمكنك إضافة عناصر مرتجع مباشرة **باستخدام رقم فاتورة المورد** بدلاً من معرف فاتورة المرتجع:

```http
POST /invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",  // ⬅️ رقم فاتورة المورد!
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

**ما يحدث تلقائياً**:
- ✅ يبحث عن فاتورة الشراء برقم المورد "4601"
- ✅ ينشئ فاتورة مرتجع جديدة (إذا لم تكن موجودة)
- ✅ يضيف العنصر للفاتورة

---

## ✅ الطرق الصحيحة

### ⭐ الطريقة الجديدة: استخدام رقم فاتورة المورد (الأسهل!)

```http
POST http://129.212.140.152/invoices/purchase-return-invoice-items/create/
{
  "invoice": "4601",  // ⬅️ رقم فاتورة المورد
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

**المميزات**:
- ✅ لا تحتاج معرفة رقم فاتورة المرتجع
- ✅ يُنشئ الفاتورة تلقائياً إذا لم تكن موجودة
- ✅ أسهل وأسرع للاستخدام

**يمكنك أيضاً استخدام معرف الفاتورة**:
```http
{
  "invoice": "5",  // ⬅️ أو معرف فاتورة المرتجع
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

---

### الطريقة 1: إنشاء فاتورة مرتجع كاملة

```http
POST http://129.212.140.152/invoices/purchase-return-invoices/create/
Content-Type: application/json

{
  "user": 1,
  "items": [
    {
      "purchase_invoice_item": 4,
      "quantity": 2
    },
    {
      "purchase_invoice_item": 5,
      "quantity": 3
    }
  ]
}
```

**هذا سيُنشئ تلقائياً**:
- ✅ فاتورة مرتجع شراء جديدة
- ✅ جميع العناصر المطلوبة
- ✅ حساب الإجماليات تلقائياً

**الاستجابة**:
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "name": "صيدلية النور"
  },
  "items_count": 2,
  "total_quantity": 5,
  "total_price": "850.00",
  "status": "placed",
  "items": [
    {
      "id": 1,
      "purchase_invoice_item": {
        "id": 4,
        "product": {
          "name": "Paracetamol 500mg"
        },
        "remaining_quantity": 98
      },
      "quantity": 2,
      "sub_total": "180.00"
    },
    {
      "id": 2,
      "purchase_invoice_item": {
        "id": 5,
        "product": {
          "name": "Ibuprofen 400mg"
        },
        "remaining_quantity": 47
      },
      "quantity": 3,
      "sub_total": "510.00"
    }
  ]
}
```

---

### الطريقة 2: التحقق من الفواتير الموجودة

إذا كنت تريد إضافة عنصر لفاتورة مرتجع **موجودة بالفعل**:

#### الخطوة 1: اعرض قائمة فواتير المرتجعات

```http
GET http://129.212.140.152/invoices/purchase-return-invoices/
```

**ستحصل على**:
```json
{
  "results": [
    {
      "id": 5,  // ⬅️ استخدم هذا الرقم
      "user": {...},
      "status": "placed",
      "items_count": 2
    }
  ]
}
```

#### الخطوة 2: أضف عنصر للفاتورة الموجودة

```http
POST http://129.212.140.152/invoices/purchase-return-invoice-items/create/
{
  "invoice": 5,  // ⬅️ رقم الفاتورة الموجودة
  "purchase_invoice_item": 4,
  "quantity": 2
}
```

---

## 📋 متطلبات إنشاء فاتورة المرتجع

### 1. عنصر فاتورة الشراء يجب أن يكون:

✅ **من فاتورة شراء مغلقة** (`status: closed`)
✅ **لديه كمية متبقية** (`remaining_quantity > 0`)

### 2. الكمية المرتجعة:

✅ **لا تتجاوز الكمية المتبقية**

---

## 🔍 كيف تتحقق من الشروط؟

### تحقق من حالة فاتورة الشراء

```http
GET http://129.212.140.152/invoices/purchase-invoices/1/
```

```json
{
  "id": 1,
  "status": "closed",  // ⬅️ يجب أن تكون closed
  "items": [
    {
      "id": 4,
      "product": {
        "name": "Paracetamol 500mg"
      },
      "quantity": 100,
      "remaining_quantity": 98,  // ⬅️ يمكن إرجاع 98 كحد أقصى
      "status": "received"
    }
  ]
}
```

---

## ⚠️ الأخطاء الشائعة

### خطأ 1: الفاتورة غير موجودة

```json
{
  "invoice": [
    "معرف العنصر \"1\" غير صالح - العنصر غير موجود."
  ]
}
```

**الحل**: استخدم رقم فاتورة مرتجع موجودة، أو أنشئ فاتورة جديدة.

---

### خطأ 2: عنصر فاتورة الشراء من فاتورة غير مغلقة

```json
{
  "purchase_invoice_item": [
    "العنصر يجب أن يكون من فاتورة مغلقة"
  ]
}
```

**الحل**: أغلق فاتورة الشراء أولاً:

```http
PUT http://129.212.140.152/invoices/purchase-invoices/1/change-state/
{
  "supplier_invoice_number": "4601",
  "status": "closed"
}
```

---

### خطأ 3: الكمية المرتجعة أكبر من المتبقية

```json
{
  "quantity": [
    "Quantity cannot exceed 98 for this item."
  ]
}
```

**الحل**: قلل الكمية المرتجعة.

```json
{
  "purchase_invoice_item": 4,
  "quantity": 50  // ⬅️ بدلاً من 200
}
```

---

## 🎯 مثال كامل خطوة بخطوة

### السيناريو:
اشتريت 100 وحدة من Paracetamol، بعت 2 منها، عايز ترجع 5 للمورد.

---

### الخطوة 1: تحقق من فاتورة الشراء

```http
GET http://129.212.140.152/invoices/purchase-invoices/1/
```

**الاستجابة**:
```json
{
  "id": 1,
  "status": "closed",
  "items": [
    {
      "id": 4,
      "product": {
        "name": "Paracetamol 500mg"
      },
      "quantity": 100,
      "remaining_quantity": 98,  // بعت 2، باقي 98
      "purchase_price": "90.00"
    }
  ]
}
```

✅ الفاتورة مغلقة  
✅ الكمية المتبقية 98 (أكبر من 5)

---

### الخطوة 2: أنشئ فاتورة المرتجع

```http
POST http://129.212.140.152/invoices/purchase-return-invoices/create/
{
  "user": 1,
  "items": [
    {
      "purchase_invoice_item": 4,
      "quantity": 5
    }
  ]
}
```

**الاستجابة**:
```json
{
  "id": 1,
  "user": {...},
  "items_count": 1,
  "total_quantity": 5,
  "total_price": "450.00",  // 5 × 90 = 450
  "status": "placed",
  "items": [
    {
      "id": 1,
      "purchase_invoice_item": {
        "id": 4,
        "remaining_quantity": 93  // 98 - 5 = 93
      },
      "quantity": 5,
      "sub_total": "450.00"
    }
  ]
}
```

✅ تم إنشاء الفاتورة  
✅ تم خصم الكمية من remaining_quantity

---

### الخطوة 3: أغلق فاتورة المرتجع

```http
PUT http://129.212.140.152/invoices/purchase-return-invoices/1/change-state/
{
  "status": "closed"
}
```

**الاستجابة**:
```json
{
  "status": "closed",
  "status_label": "Closed"
}
```

✅ تم إغلاق الفاتورة  
✅ تم تسجيل المعاملة المالية

---

## 📚 APIs المتاحة

### فواتير المرتجعات

| الطريقة | المسار | الوصف |
|---------|--------|-------|
| GET | `/invoices/purchase-return-invoices/` | قائمة الفواتير |
| POST | `/invoices/purchase-return-invoices/create/` | إنشاء فاتورة |
| GET | `/invoices/purchase-return-invoices/{id}/` | تفاصيل فاتورة |
| PUT | `/invoices/purchase-return-invoices/{id}/change-state/` | إغلاق الفاتورة |

### عناصر فواتير المرتجعات

| الطريقة | المسار | الوصف |
|---------|--------|-------|
| GET | `/invoices/purchase-return-invoice-items/` | قائمة العناصر |
| POST | `/invoices/purchase-return-invoice-items/create/` | إضافة عنصر |
| GET | `/invoices/purchase-return-invoice-items/{id}/` | تفاصيل عنصر |

---

## 💡 نصائح

1. ✅ **استخدم طريقة إنشاء الفاتورة الكاملة** (الطريقة 1) - أسهل وأسرع
2. ✅ **تأكد من أن فاتورة الشراء مغلقة** قبل إنشاء المرتجع
3. ✅ **تحقق من الكمية المتبقية** قبل إرجاع العناصر
4. ✅ **لا تنسى إغلاق فاتورة المرتجع** بعد الانتهاء

---

**آخر تحديث**: 2025-10-10  
**الإصدار**: 1.1.0

