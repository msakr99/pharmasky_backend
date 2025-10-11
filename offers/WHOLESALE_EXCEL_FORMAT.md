# تنسيق ملف Excel لرفع عروض الجملة

## الأعمدة المطلوبة

| اسم العمود | النوع | مطلوب | الوصف | مثال |
|-----------|-------|-------|-------|------|
| `product_code` | Integer | نعم | كود المنتج في المتجر | 12345 |
| `available_amount` | Integer | نعم | الكمية المتاحة | 500 |
| `purchase_discount_percentage` | Decimal | نعم | نسبة الخصم (0-99.99) | 18.50 |
| `max_amount_per_invoice` | Integer | نعم | الحد الأقصى لكل فاتورة | 100 |
| `min_purchase` | Decimal | نعم | الحد الأدنى للشراء (يمكن 0) | 0.00 |
| `product_expiry_date` | Date | نعم | تاريخ انتهاء المنتج (YYYY-MM-DD) | 2025-12-31 |
| `operating_number` | String | نعم | رقم التشغيل | OP-2024-001 |

## الأعمدة الاختيارية (للجملة)

| اسم العمود | النوع | افتراضي | الوصف | مثال |
|-----------|-------|---------|-------|------|
| `wholesale_min_quantity` | Integer | 10 | الحد الأدنى للطلب | 20 |
| `wholesale_increment` | Integer | 5 | مقدار الزيادة المسموح بها | 10 |

## مثال على صفوف البيانات

```
product_code | available_amount | purchase_discount_percentage | max_amount_per_invoice | min_purchase | product_expiry_date | operating_number | wholesale_min_quantity | wholesale_increment
12345        | 500              | 18.50                       | 100                    | 0.00         | 2025-12-31         | OP-2024-001     | 20                     | 10
12346        | 1000             | 20.00                       | 200                    | 0.00         | 2025-11-30         | OP-2024-002     | 10                     | 5
12347        | 750              | 15.75                       | 150                    | 0.00         | 2026-01-15         | OP-2024-003     | 15                     | 5
```

## ملاحظات مهمة

### 1. تنسيق الملف
- احفظ الملف بصيغة `.xlsx` أو `.xls`
- الصف الأول يجب أن يحتوي على أسماء الأعمدة بالضبط كما هي مكتوبة أعلاه
- لا تترك صفوف فارغة بين البيانات

### 2. الأرقام
- `product_code`: رقم صحيح فقط
- `available_amount`: رقم صحيح موجب
- `purchase_discount_percentage`: رقم عشري بين 0 و 99.99
- `wholesale_min_quantity`: رقم صحيح موجب (إذا لم يُحدد، سيكون 10)
- `wholesale_increment`: رقم صحيح موجب (إذا لم يُحدد، سيكون 5)

### 3. التواريخ
- استخدم صيغة `YYYY-MM-DD` (مثال: 2025-12-31)
- التاريخ يجب أن يكون في المستقبل

### 4. النصوص
- `operating_number`: يمكن أن يكون أي نص

## مثال على طلب API

### 1. الإعداد
```bash
# إنشاء ملف Excel بالأعمدة والبيانات أعلاه
# احفظه باسم wholesale_offers.xlsx
```

### 2. الرفع
```bash
curl -X POST https://api.example.com/api/offers/wholesale-offers/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@wholesale_offers.xlsx" \
  -F "user=123" \
  -F "is_wholesale=true"
```

**المعاملات**:
- `file`: ملف Excel
- `user`: معرف المتجر/الشركة (يجب أن يكون `company=True`)
- `is_wholesale`: يجب أن يكون `true`

### 3. الاستجابة الناجحة
```json
{
  "message": "تم رفع 3 عرض جملة بنجاح",
  "count": 3,
  "offers": [45, 46, 47]
}
```

### 4. رسائل الخطأ الشائعة

#### خطأ: Product code not found
```json
{
  "error": "حدث خطأ أثناء رفع عروض الجملة",
  "details": "in line 2, Product code 99999 was not found, Please add the Code first then try again."
}
```
**الحل**: تأكد من أن الـ `product_code` موجود للمتجر في جدول `StoreProductCode`

#### خطأ: Store is not a company
```json
{
  "error": "حدث خطأ أثناء رفع عروض الجملة",
  "details": "عروض الجملة متاحة فقط للمتاجر المسجلة كشركات (company=True)."
}
```
**الحل**: تأكد من أن `company=True` في `StoreProfile` للمتجر

#### خطأ: Invalid discount percentage
```json
{
  "error": "حدث خطأ أثناء رفع عروض الجملة",
  "details": "in line 3, Purchase discount percenteage should be greater than or equal to 12.00."
}
```
**الحل**: تأكد من أن نسبة الخصم أكبر من أو تساوي `profit_percentage` للمتجر

## نصائح

1. **اختبر بملف صغير أولاً**: ابدأ بـ 2-3 صفوف للتأكد من صحة التنسيق
2. **تحقق من الأكواد**: تأكد من أن جميع `product_code` موجودة مسبقاً
3. **احفظ نسخة احتياطية**: قبل الرفع، احفظ نسخة من البيانات القديمة
4. **المراجعة**: بعد الرفع، راجع القائمة للتأكد من صحة البيانات

## قالب Excel جاهز

يمكنك نسخ الجدول التالي إلى Excel:

| product_code | available_amount | purchase_discount_percentage | max_amount_per_invoice | min_purchase | product_expiry_date | operating_number | wholesale_min_quantity | wholesale_increment |
|--------------|------------------|------------------------------|------------------------|--------------|---------------------|------------------|------------------------|---------------------|
| 12345        | 500              | 18.50                        | 100                    | 0            | 2025-12-31          | OP-2024-001      | 20                     | 10                  |
| 12346        | 1000             | 20.00                        | 200                    | 0            | 2025-11-30          | OP-2024-002      | 10                     | 5                   |

ثم قم بتعبئة البيانات الخاصة بك!

## دعم فني

للمساعدة أو الإبلاغ عن مشاكل:
- راجع `/api/offers/wholesale-offers/` للتحقق من العروض المرفوعة
- استخدم `/api/offers/max-wholesale-offers/excel/` لتصدير البيانات الحالية كمرجع

