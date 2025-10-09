# إصلاحات وتحسينات PDF الفاتورة
# Invoice PDF Fixes & Improvements

## 🎯 المشاكل المحلولة | Problems Fixed

### 1️⃣ مشكلة: PDF لا يفتح | PDF Won't Open

**السبب:**
- خطأ في حساب `average_discount_percentage` عندما يكون `total_public_price = 0` أو `None`
- Division by zero error

**الإصلاح:**
```python
# قبل
average_discount_percentage = aggregates["quantity_discount__sum"] / total_public_price
# ❌ يسبب خطأ إذا كان total_public_price = 0 أو None

# بعد
total_public_price = aggregates["quantity_price__sum"] or 0
total_discount = aggregates["quantity_discount__sum"] or 0

if total_public_price > 0:
    average_discount = total_discount / total_public_price
else:
    average_discount = 0
# ✅ آمن من أخطاء القسمة
```

---

### 2️⃣ تحسين: تسمية الملف باسم العميل والتاريخ | Customer Name & Date in Filename

**قبل:**
```python
# اسم ثابت
"Invoice No. {id}.pdf"
# مثال: "Invoice No. 1.pdf"
```

**بعد:**
```python
# اسم ديناميكي
"فاتورة_{customer_name}_{date}.pdf"
# مثال: "فاتورة_الشفاء_2025-10-09.pdf"
```

**المميزات:**
- ✅ يحتوي على اسم العميل
- ✅ يحتوي على تاريخ الفاتورة
- ✅ تنظيف اسم العميل من الأحرف غير المسموحة
- ✅ حد أقصى 50 حرف للاسم
- ✅ fallback إلى رقم الفاتورة عند وجود خطأ

---

### 3️⃣ إصلاح: تحويل النسبة المئوية | Percentage Conversion

**المشكلة:**
في `SaleInvoicePDFSerializer`، كان هناك خلط بين القيمة العشرية (0-1) والنسبة المئوية (0-100).

**الإصلاح:**
```python
# في get_average_discount_percentage()
average_discount_percentage = self.context.get("average_discount_percentage", 0)
# Convert from decimal (0-1) to percentage (0-100)
percentage = Decimal(average_discount_percentage) * 100
return percentage.quantize(Decimal("0.00"))

# في get_total_price()
# average_discount_percentage is already a decimal (0-1), not percentage
total_price = instance.quantity * instance.product.public_price * (1 - Decimal(average_discount_percentage))
```

---

## 📋 أمثلة | Examples

### مثال 1: تحميل PDF

```bash
GET /api/v1/invoices/sale/1/download/

# Response Headers
Content-Disposition: attachment; filename="فاتورة_الشفاء_2025-10-09.pdf"
Content-Type: application/pdf

# الملف سيتم تحميله بهذا الاسم
```

---

### مثال 2: اسم الملف حسب العميل

```python
# فاتورة رقم 1 للعميل "الشفاء" بتاريخ 2025-10-09
"فاتورة_الشفاء_2025-10-09.pdf"

# فاتورة رقم 2 للعميل "صيدلية النور" بتاريخ 2025-10-10
"فاتورة_صيدلية النور_2025-10-10.pdf"

# فاتورة رقم 3 للعميل باسم طويل جداً
"فاتورة_اسم_طويل_جدا_يتم_قصه_هنا_فقط_خمسون_حر_2025-10-11.pdf"
```

---

### مثال 3: أحرف خاصة في الاسم

```python
# اسم العميل: "صيدلية النور/الشفاء"
# بعد التنظيف: "صيدلية النورالشفاء"
"فاتورة_صيدلية النورالشفاء_2025-10-09.pdf"

# اسم العميل يحتوي على: < > : " / \ | ? *
# يتم إزالتها كلها
```

---

## 🔧 التفاصيل الفنية | Technical Details

### دالة get_filename()

```python
def get_filename(self, request=None, *args, **kwargs):
    from datetime import datetime
    
    # Get the invoice to access customer name and date
    invoice_id = self.kwargs.get(self.lookup_field)
    try:
        invoice = SaleInvoice.objects.select_related('user').get(id=invoice_id)
        customer_name = invoice.user.name
        invoice_date = invoice.created_at.strftime('%Y-%m-%d')
        
        # Clean customer name for filename (remove invalid characters)
        import re
        clean_name = re.sub(r'[<>:"/\\|?*]', '', customer_name)
        clean_name = clean_name.strip()[:50]  # Limit length
        
        filename = f"فاتورة_{clean_name}_{invoice_date}.pdf"
        return filename
    except:
        # Fallback to invoice number if something goes wrong
        return f"Invoice_{invoice_id}.pdf"
```

**الأحرف الممنوعة في أسماء الملفات (Windows):**
- `<` `>` `:` `"` `/` `\` `|` `?` `*`

يتم إزالتها تلقائياً.

---

### دالة get_serializer_context()

```python
def get_serializer_context(self):
    ctx = super().get_serializer_context()
    items = (
        SaleInvoiceItem.objects.select_related("product")
        .annotate(
            quantity_discount=models.F("quantity")
            * models.F("selling_discount_percentage")
            * models.F("product__public_price"),
            quantity_price=models.F("quantity") * models.F("product__public_price"),
        )
        .filter(invoice_id=self.kwargs.get(self.lookup_field))
    )
    aggregates = items.aggregate(
        models.Sum("quantity_discount"), 
        models.Sum("quantity_price")
    )
    
    # Safe calculation
    total_public_price = aggregates["quantity_price__sum"] or 0
    total_discount = aggregates["quantity_discount__sum"] or 0
    
    if total_public_price > 0:
        average_discount = total_discount / total_public_price
    else:
        average_discount = 0

    ctx.update({
        "items": items,
        "total_public_price": total_public_price,
        "average_discount_percentage": average_discount,  # 0-1 decimal
    })

    return ctx
```

---

## ⚠️ ملاحظات مهمة | Important Notes

### 1. تنسيق التاريخ
التاريخ بصيغة: `YYYY-MM-DD`
```
2025-10-09
```

### 2. طول اسم الملف
- الحد الأقصى لاسم العميل: **50 حرف**
- إذا كان أطول، يتم القص

### 3. Fallback
إذا حدث أي خطأ في الحصول على بيانات الفاتورة:
```python
return f"Invoice_{invoice_id}.pdf"
```

### 4. الترميز (Encoding)
- الأسماء العربية تعمل بشكل صحيح
- UTF-8 encoding

---

## 🎯 الفوائد | Benefits

### 1. **تنظيم أفضل**
- سهولة التعرف على الملف
- لا حاجة لفتح الملف لمعرفة العميل

### 2. **بحث أسهل**
- البحث باسم العميل في المجلد
- الترتيب حسب التاريخ

### 3. **احترافية**
- اسم الملف يحتوي على معلومات مفيدة
- يبدو أكثر احترافية للعميل

### 4. **أمان**
- حماية من division by zero
- معالجة الأسماء الخاصة
- fallback في حالة الأخطاء

---

## 📊 الاختبار | Testing

### اختبار 1: فاتورة عادية
```bash
GET /api/v1/invoices/sale/1/download/

# Expected filename
"فاتورة_الشفاء_2025-10-09.pdf"
```

### اختبار 2: اسم بأحرف خاصة
```python
# Customer name: "صيدلية/النور"
# Expected: "فاتورة_صيدليةالنور_2025-10-09.pdf"
```

### اختبار 3: اسم طويل
```python
# Customer name: "صيدلية طويلة جداً جداً جداً..." (100 chars)
# Expected: "فاتورة_صيدلية طويلة جداً جداً جداً..._2025-10-09.pdf" (50 chars)
```

### اختبار 4: فاتورة فارغة
```bash
# Invoice with no items
# Should not crash, returns PDF with 0 discount
```

---

## 📁 الملفات المعدلة | Modified Files

### 1. `invoices/views.py`
- ✅ إصلاح `get_serializer_context()` - منع division by zero
- ✅ تحسين `get_filename()` - اسم ديناميكي

### 2. `invoices/serializers.py`
- ✅ إصلاح `SaleInvoicePDFSerializer.get_average_discount_percentage()`
- ✅ إصلاح `SaleInvoiceItemubReadSerializer.get_total_price()`
- ✅ إصلاح `SaleInvoiceItemubReadSerializer.get_average_discount_percentage()`

---

## 🚀 الحالة | Status

✅ **جاهز للإنتاج** | Production Ready  
📅 **التاريخ**: 2025-10-09  
🔖 **الإصدار**: 1.0

---

## 🔗 روابط ذات صلة | Related Links

- [Django PDF Rendering](https://docs.djangoproject.com/)
- [Python datetime strftime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
- [Windows Filename Restrictions](https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file)

---

**ملاحظة**: الآن يمكن تحميل PDF بدون أخطاء واسم الملف يحتوي على معلومات مفيدة! 🎉

