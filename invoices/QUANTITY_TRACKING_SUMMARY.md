# ملخص: تتبع تقليل الكميات
# Summary: Quantity Reduction Tracking

## 🎯 الميزة الجديدة | New Feature

عندما يتم **تقليل كمية** صنف في الفاتورة، يتم تسجيل الكمية المحذوفة تلقائياً في `deleted_items`.

When an item's **quantity is reduced** in an invoice, the removed quantity is automatically recorded in `deleted_items`.

---

## 📋 مثال سريع | Quick Example

### قبل | Before
```json
{
  "items": [{"id": 2, "quantity": 50}],
  "deleted_items": []
}
```

### بعد تقليل الكمية من 50 إلى 48 | After reducing from 50 to 48
```json
{
  "items": [{"id": 2, "quantity": 48}],
  "deleted_items": [
    {
      "quantity": 2,           // الكمية المحذوفة
      "sub_total": "395.16",   // السعر للكمية المحذوفة فقط
      "timestamp": "2025-10-09T17:30:00Z"
    }
  ]
}
```

---

## ✅ الحالات المتتبعة | Tracked Cases

| الحالة | مثال | النتيجة |
|-------|------|---------|
| تقليل الكمية | 50 → 48 | ✅ يتم التسجيل في deleted_items (quantity: 2) |
| حذف كامل | DELETE item | ✅ يتم التسجيل في deleted_items (quantity: 50) |
| زيادة الكمية | 48 → 50 | ❌ لا يتم التسجيل |
| تقليل متعدد | 50 → 48 → 45 | ✅ سجلان منفصلان (2, 3) |

---

## 💡 الفوائد | Benefits

1. **🔍 تتبع كامل**: معرفة جميع التغييرات في الكميات
2. **📊 تقارير دقيقة**: تحليل الكميات المحذوفة والأسباب
3. **✔️ شفافية**: وضوح في التغييرات على الفواتير
4. **📝 تدقيق**: سجل كامل للمراجعة والمحاسبة

---

## 🔧 كيف تعمل | How It Works

```
1. المستخدم يقلل الكمية من 50 إلى 48
                    ↓
2. النظام يحسب الفرق: 50 - 48 = 2
                    ↓
3. إنشاء سجل في deleted_items:
   - quantity: 2
   - sub_total: selling_price × 2
   - timestamp: now()
                    ↓
4. تحديث العنصر الأصلي إلى quantity: 48
```

---

## 📁 الملفات المعدلة | Modified Files

- ✅ `invoices/managers.py` - إضافة `create_for_quantity_reduction()`
- ✅ `invoices/utils.py` - تحديث `update_sale_invoice_item()` و `update_purchase_invoice_item()`
- ✅ `invoices/QUANTITY_REDUCTION_TRACKING.md` - توثيق كامل

---

## 🚀 الاستخدام | Usage

### تحديث الكمية
```bash
PATCH /api/v1/invoices/sale-invoice-items/2/
{
  "quantity": 48  # كانت 50
}
```

### عرض النتيجة
```bash
GET /api/v1/invoices/sale/1/

# deleted_items سيحتوي على:
{
  "quantity": 2,
  "sub_total": "395.16",
  "timestamp": "..."
}
```

---

## ⚙️ التحكم | Control

```python
# مع التتبع (افتراضي)
update_sale_invoice_item(item, data)

# بدون تتبع
update_sale_invoice_item(item, data, track_quantity_reduction=False)
```

---

## 📖 التوثيق الكامل | Full Documentation

للتفاصيل الكاملة، راجع: [QUANTITY_REDUCTION_TRACKING.md](./QUANTITY_REDUCTION_TRACKING.md)

---

**الحالة**: ✅ جاهز للاستخدام  
**التاريخ**: 2025-10-09  
**الإصدار**: 1.0

