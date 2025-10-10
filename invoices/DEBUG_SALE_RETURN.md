# حل مشكلة: فاتورة الإرجاع غير موجودة
# Fix: Sale Return Invoice Not Found

## 🔍 المشكلة | The Problem

```json
{
  "invoice": [
    "معرف العنصر \"1\" غير صالح - العنصر غير موجود."
  ]
}
```

**عند:**
```json
POST /invoices/sale-return-invoice-items/create/
{
  "invoice": 1,
  "sale_invoice_item": 2,
  "quantity": 8
}
```

---

## 📊 السبب المحتمل | Possible Causes

### 1. فاتورة الإرجاع غير موجودة
```python
# لا يوجد SaleReturnInvoice with id=1
```

### 2. فاتورة الإرجاع مغلقة
```python
# SaleReturnInvoice with id=1 has status='closed'
# والـ queryset يستبعد الفواتير المغلقة:
queryset=SaleReturnInvoice.objects.exclude(
    status=SaleReturnInvoiceStatusChoice.CLOSED
)
```

---

## ✅ الحل | Solution

### الخطوة 1: تحقق من وجود فاتورة الإرجاع

```bash
GET http://129.212.140.152/invoices/sale-return-invoices/1/
```

**إذا كانت موجودة:**
```json
{
  "id": 1,
  "status": "closed",  // ❌ مغلقة!
  ...
}
```

**إذا لم تكن موجودة:**
```json
{
  "detail": "Not found."
}
```

---

### الخطوة 2: الحلول حسب الحالة

#### الحالة أ: الفاتورة غير موجودة ❌

**الحل:** أنشئ فاتورة إرجاع أولاً:

```bash
POST http://129.212.140.152/invoices/sale-return-invoices/create/
{
  "user": 5,  // نفس المستخدم من فاتورة البيع
  "items": [
    {
      "sale_invoice_item": 2,
      "quantity": 8
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,  // ✅ فاتورة إرجاع جديدة
  "user": {...},
  "items": [...],
  "status": "placed"
}
```

---

#### الحالة ب: الفاتورة موجودة لكن مغلقة ❌

**الحل 1:** افتح الفاتورة المغلقة (إن أمكن):
```bash
PATCH http://129.212.140.152/invoices/sale-return-invoices/1/change-state/
{
  "status": "placed"
}
```

**الحل 2:** أنشئ فاتورة إرجاع جديدة:
```bash
POST http://129.212.140.152/invoices/sale-return-invoices/create/
{
  "user": 5,
  "items": [
    {
      "sale_invoice_item": 2,
      "quantity": 8
    }
  ]
}
```

---

#### الحالة ج: الفاتورة موجودة ومفتوحة ✅

**يمكنك إضافة العنصر مباشرة:**
```bash
POST http://129.212.140.152/invoices/sale-return-invoice-items/create/
{
  "invoice": 1,
  "sale_invoice_item": 2,
  "quantity": 8
}
```

---

## 🔍 كيف تتحقق | How to Check

### تحقق من الفواتير المتاحة:

```bash
GET http://129.212.140.152/invoices/sale-return-invoices/
```

**سيعرض لك:**
```json
{
  "results": [
    {
      "id": 1,
      "status": "placed",  // ✅ أو "closed" ❌
      "user": {...}
    }
  ]
}
```

---

### تحقق من فاتورة معينة:

```bash
GET http://129.212.140.152/invoices/sale-return-invoices/1/
```

---

## 📋 الطريقة الصحيحة | Correct Way

### السيناريو 1: إنشاء فاتورة إرجاع كاملة

```bash
POST /invoices/sale-return-invoices/create/
{
  "user": 5,
  "items": [
    {
      "sale_invoice_item": 2,
      "quantity": 8
    }
  ]
}
```

**الفوائد:**
- ✅ يتم إنشاء الفاتورة والعناصر معاً
- ✅ لا حاجة لمعرفة ID الفاتورة مسبقاً

---

### السيناريو 2: إضافة عنصر لفاتورة موجودة

```bash
# 1. تأكد من وجود فاتورة إرجاع مفتوحة
GET /invoices/sale-return-invoices/?user=5&status=placed

# 2. إذا وجدت فاتورة (مثلاً ID=1)
POST /invoices/sale-return-invoice-items/create/
{
  "invoice": 1,
  "sale_invoice_item": 2,
  "quantity": 8
}
```

---

## ⚠️ الشروط المطلوبة | Required Conditions

لإضافة عنصر لفاتورة إرجاع، يجب:

### 1. فاتورة الإرجاع:
- ✅ موجودة
- ✅ حالتها `placed` (ليست `closed`)
- ✅ لنفس المستخدم

### 2. عنصر فاتورة البيع:
- ✅ من فاتورة بيع مغلقة (`closed`)
- ✅ `remaining_quantity > 0`
- ✅ المنتج ليس من الثلاجة (`fridge=False`)

---

## 🎯 الحل السريع | Quick Fix

إذا لم تكن متأكداً، استخدم **طريقة الإنشاء الكاملة**:

```bash
POST http://129.212.140.152/invoices/sale-return-invoices/create/
{
  "user": 5,
  "items": [
    {
      "sale_invoice_item": 2,
      "quantity": 8
    }
  ]
}
```

**سيقوم بـ:**
1. ✅ إنشاء فاتورة إرجاع جديدة
2. ✅ إضافة العنصر إليها
3. ✅ إرجاع الفاتورة الكاملة مع العناصر

---

## 📝 ملاحظات | Notes

- فاتورة الإرجاع منفصلة عن فاتورة البيع
- يمكن أن يكون للمستخدم أكثر من فاتورة إرجاع
- فقط الفواتير المفتوحة (`placed`) يمكن إضافة عناصر لها

---

جرب الطريقة الكاملة أولاً! 🚀


