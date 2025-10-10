# URLs المخزون - ملخص سريع
# Inventory URLs - Quick Summary

## 📋 قائمة الأصناف

### الأساسي
```
http://129.212.140.152/inventory/inventory-items/
```

---

## 🔍 بحث

```
# بحث بالاسم
?search=paracetamol
?search=ibuprofen
?search=aspirin
```

**مثال كامل:**
```
http://129.212.140.152/inventory/inventory-items/?search=para
```

---

## 🎯 فلترة

```
# حسب المخزن
?inventory=1

# حسب المنتج
?product=10

# عدة منتجات
?product=10,20,30
```

**مثال كامل:**
```
http://129.212.140.152/inventory/inventory-items/?product=10
```

---

## 📊 ترتيب

| الترتيب | الكود |
|---------|-------|
| الأقل كمية | `?o=remaining_quantity` |
| الأكثر كمية | `?o=-remaining_quantity` |
| الأرخص سعر | `?o=purchase_price` |
| الأغلى سعر | `?o=-purchase_price` |
| أبجدي A-Z | `?o=product__name` |
| أبجدي Z-A | `?o=-product__name` |
| الأقرب صلاحية | `?o=product_expiry_date` |
| أعلى خصم | `?o=-purchase_discount_percentage` |

**مثال كامل:**
```
http://129.212.140.152/inventory/inventory-items/?o=remaining_quantity
```

---

## 📄 Pagination

```
# 50 نتيجة في الصفحة
?ps=50

# الصفحة رقم 2
?p=2

# معاً
?ps=50&p=2
```

---

## 🎯 أمثلة شائعة جاهزة

### 1. أقل 10 أصناف كمية
```
http://129.212.140.152/inventory/inventory-items/?o=remaining_quantity&ps=10
```

### 2. بحث عن paracetamol
```
http://129.212.140.152/inventory/inventory-items/?search=paracetamol
```

### 3. جميع دفعات منتج رقم 10
```
http://129.212.140.152/inventory/inventory-items/?product=10
```

### 4. الأقرب انتهاء صلاحية (20 صنف)
```
http://129.212.140.152/inventory/inventory-items/?o=product_expiry_date&ps=20
```

### 5. أغلى 10 أصناف
```
http://129.212.140.152/inventory/inventory-items/?o=-purchase_price&ps=10
```

### 6. الصفحة الأولى، 50 صنف
```
http://129.212.140.152/inventory/inventory-items/?ps=50&p=1
```

---

## 📦 الحقول في الاستجابة

```json
{
  "count": 135,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": {
        "name": "Paracetamol 500mg",
        "public_price": "100.00"
      },
      "purchase_price": "90.00",
      "purchase_discount_percentage": "10.00",
      "selling_price": "95.00",
      "remaining_quantity": 85,
      "supplier_name": "تاج",
      "supplier_invoice_number": "4601",
      "purchase_date": "2025-10-09T10:16:12Z"
    }
  ]
}
```

---

## 🚀 جاهز للاستخدام

انسخ الـ URL والصقه مباشرة في المتصفح أو Postman! 📋

---

**للتفاصيل الكاملة**: راجع [API_URLS_GUIDE.md](./inventory/API_URLS_GUIDE.md)

