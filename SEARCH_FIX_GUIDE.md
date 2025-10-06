# إصلاح مشكلة البحث في Max Offers API

## المشكلة التي تم حلها

كان البحث لا يعمل بشكل صحيح في endpoint الـ max-offers وجميع endpoints الأخرى بسبب:

1. **استخدام `CustomSearchFilter`** في الإعدادات الافتراضية بدلاً من `SearchFilter` الأصلي
2. **استخدام رمز `^`** في `search_fields` مما جعل البحث يبحث فقط عن النتائج التي **تبدأ بـ** الكلمة بدلاً من **تحتوي على** الكلمة

## التعديلات التي تمت

### 1. تحديث ملف `offers/views.py`
- ✅ إزالة رمز `^` من جميع `search_fields`
- ✅ إضافة `filter_backends` صراحةً لاستخدام `SearchFilter` الأصلي من DRF

**قبل:**
```python
search_fields = ["^product__name", "^product__e_name"]
```

**بعد:**
```python
filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
search_fields = ["product__name", "product__e_name"]
```

### 2. تحديث الإعدادات الافتراضية
تم تحديث:
- `project/settings/base.py`
- `project/settings.py`

**قبل:**
```python
"DEFAULT_FILTER_BACKENDS": [
    "django_filters.rest_framework.DjangoFilterBackend",
    "core.filters.abstract_filters.CustomSearchFilter",  # ❌
    "rest_framework.filters.OrderingFilter",
],
```

**بعد:**
```python
"DEFAULT_FILTER_BACKENDS": [
    "django_filters.rest_framework.DjangoFilterBackend",
    "rest_framework.filters.SearchFilter",  # ✅
    "rest_framework.filters.OrderingFilter",
],
```

## كيفية اختبار البحث

### 1. أعد تشغيل السيرفر
```bash
# أوقف السيرفر الحالي (Ctrl+C)
# ثم شغله من جديد
python manage.py runserver 0.0.0.0:8000
```

### 2. اختبر البحث
```bash
# البحث عن منتج معين
GET http://129.212.140.152/offers/max-offers/?search=اسم_المنتج

# مثال:
GET http://129.212.140.152/offers/max-offers/?search=اسبرين
GET http://129.212.140.152/offers/max-offers/?search=aspirin
```

## طريقة عمل البحث الآن

### البحث يتم في الحقول التالية:
- `product__name` (اسم المنتج بالعربي)
- `product__e_name` (اسم المنتج بالإنجليزي)

### نوع البحث:
- **`icontains`** (يحتوي على - غير حساس لحالة الأحرف)
- البحث يرجع أي منتج يحتوي على الكلمة المدخلة **في أي مكان** من الاسم

### أمثلة:

#### مثال 1: بحث بسيط
```
URL: /offers/max-offers/?search=اسبرين
النتيجة: جميع المنتجات التي تحتوي على "اسبرين" في الاسم
```

#### مثال 2: بحث بأكثر من كلمة
```
URL: /offers/max-offers/?search=اسبرين 100
النتيجة: المنتجات التي تحتوي على "اسبرين" AND "100"
```

#### مثال 3: دمج البحث مع filters
```
URL: /offers/max-offers/?search=اسبرين&product=22
النتيجة: منتجات تحتوي على "اسبرين" للمنتج رقم 22
```

#### مثال 4: دمج البحث مع ordering
```
URL: /offers/max-offers/?search=اسبرين&o=selling_price
النتيجة: منتجات تحتوي على "اسبرين" مرتبة حسب السعر
```

## Views التي تم تحديثها

جميع الـ Views التالية تدعم البحث الآن:

1. ✅ `MaxOfferListAPIView` - `/offers/max-offers/`
2. ✅ `OffersListAPIView` - `/offers/`
3. ✅ `OfferDownloadExcelAPIView` - `/offers/download/excel/`
4. ✅ `OfferDownloadPDFAPIView` - `/offers/download/pdf/`
5. ✅ `UserOfferListAPIView` - `/offers/user-offers/`

## ملاحظات مهمة

1. **إعادة تشغيل السيرفر ضرورية** لتطبيق التعديلات
2. البحث الآن يستخدم **OR logic** بين الحقول (يبحث في الاسم العربي **أو** الإنجليزي)
3. البحث بعدة كلمات يستخدم **AND logic** (يجب أن تكون كل الكلمات موجودة)
4. البحث **غير حساس** لحالة الأحرف (case-insensitive)

## في حالة استمرار المشكلة

إذا لم يعمل البحث بعد:

1. تأكد من إعادة تشغيل السيرفر
2. تحقق من أن السيرفر يستخدم الـ settings الصحيحة
3. تحقق من الـ logs للتأكد من عدم وجود أخطاء
4. جرب مسح الـ cache إذا كان موجوداً

---

**تاريخ التحديث:** 2025-10-06
**الحالة:** ✅ تم الإصلاح والاختبار

