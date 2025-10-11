# مقارنة بين العروض العادية وعروض الجملة

## جدول المقارنة السريعة

| الميزة | العروض العادية | عروض الجملة |
|--------|----------------|--------------|
| **الحقل** | `is_max=True` | `is_max_wholesale=True` |
| **API** | `/max-offers/` | `/max-wholesale-offers/` |
| **الشرط** | أي متجر | `company=True` فقط |
| **الحد الأدنى** | `min_purchase` (مبلغ) | `wholesale_min_quantity` (عدد علب) |
| **الزيادة** | حرة | `wholesale_increment` (مثلاً 5 علب) |
| **الاستخدام** | الصيدليات العادية | الشركات والجملة |

---

## التفاصيل

### 1. العروض العادية (Regular Offers)

#### المميزات:
- ✅ متاح لجميع المتاجر
- ✅ الحد الأدنى بالمبلغ (`min_purchase`)
- ✅ لا يوجد قيود على الزيادة
- ✅ مناسب للصيدليات الصغيرة

#### الحقول:
```python
is_max = BooleanField()  # أفضل عرض عادي
min_purchase = DecimalField()  # الحد الأدنى بالمبلغ
```

#### API Endpoints:
```
GET /api/offers/offers/
GET /api/offers/max-offers/
POST /api/offers/offers/create/
POST /api/offers/offers/upload/
```

#### مثال:
```json
{
  "product_code": 12345,
  "available_amount": 100,
  "purchase_discount_percentage": 12.00,
  "min_purchase": 500.00,  // 500 جنيه حد أدنى
  "is_max": true
}
```

**السيناريو**: صيدلية تريد شراء 25 علبة، السعر 50 جنيه للعلبة
- إجمالي: 25 × 50 = 1250 جنيه
- الحد الأدنى: 500 جنيه ✅
- يمكن الشراء!

---

### 2. عروض الجملة (Wholesale Offers)

#### المميزات:
- ✅ للشركات فقط (`company=True`)
- ✅ الحد الأدنى بعدد العلب (`wholesale_min_quantity`)
- ✅ الزيادة محددة (`wholesale_increment`)
- ✅ مناسب للكميات الكبيرة

#### الحقول:
```python
is_wholesale = BooleanField()  # عرض جملة
is_max_wholesale = BooleanField()  # أفضل عرض جملة
wholesale_min_quantity = PositiveIntegerField(default=10)  # 10 علب
wholesale_increment = PositiveIntegerField(default=5)  # زيادة 5 علب
```

#### API Endpoints:
```
GET /api/offers/wholesale-offers/
GET /api/offers/max-wholesale-offers/
POST /api/offers/wholesale-offers/create/
POST /api/offers/wholesale-offers/upload/
```

#### مثال:
```json
{
  "product_code": 12345,
  "available_amount": 1000,
  "purchase_discount_percentage": 18.00,
  "is_wholesale": true,
  "wholesale_min_quantity": 20,  // 20 علبة حد أدنى
  "wholesale_increment": 10,  // زيادة 10 علب فقط
  "is_max_wholesale": true
}
```

**السيناريو**: شركة تريد شراء أدوية
- الحد الأدنى: 20 علبة
- يمكن طلب: 20, 30, 40, 50... (بزيادة 10)
- ❌ لا يمكن طلب: 25, 35, 45... (ليست مضاعفات الزيادة من الحد الأدنى)

---

## الانفصال التام

### ✅ الأمور المنفصلة:

1. **قواعد البيانات**:
   - `is_max` ≠ `is_max_wholesale`
   - منتج واحد يمكن أن يكون له عرضين: عادي وجملة

2. **APIs**:
   - `/max-offers/` ≠ `/max-wholesale-offers/`
   - كل واحد يعرض عروضه فقط

3. **الحسابات**:
   - `calculate_max_offer()` للعادي
   - `calculate_max_wholesale_offer()` للجملة

### 🔄 الأمور المشتركة:

1. **المنتج**: نفس المنتج يمكن أن يكون له عروض عادية وجملة
2. **المتجر**: المتجر الواحد يمكنه تقديم النوعين (إذا كان `company=True`)
3. **السعر**: نفس طريقة الحساب (خصم من السعر العام)

---

## أمثلة عملية

### مثال 1: متجر عادي (company=False)

```json
// ✅ يمكن إنشاء عرض عادي
POST /api/offers/offers/create/
{
  "product_code": 12345,
  "available_amount": 50,
  "purchase_discount_percentage": 10.00
}

// ❌ لا يمكن إنشاء عرض جملة
POST /api/offers/wholesale-offers/create/
{
  "product_code": 12345,
  "is_wholesale": true
}
// Response: "عروض الجملة متاحة فقط للمتاجر المسجلة كشركات"
```

---

### مثال 2: شركة (company=True)

```json
// ✅ يمكن إنشاء عرض عادي
POST /api/offers/offers/create/
{
  "product_code": 12345,
  "available_amount": 50,
  "purchase_discount_percentage": 10.00
}

// ✅ يمكن إنشاء عرض جملة
POST /api/offers/wholesale-offers/create/
{
  "product_code": 12345,
  "available_amount": 500,
  "purchase_discount_percentage": 15.00,
  "is_wholesale": true,
  "wholesale_min_quantity": 50
}
```

---

### مثال 3: نفس المنتج بعرضين

**المنتج**: Aspirin 100mg (ID: 456)

#### العرض العادي:
```json
{
  "id": 100,
  "product": {"id": 456, "name": "Aspirin 100mg"},
  "user": {"id": 10, "name": "صيدلية الشفاء"},
  "selling_discount_percentage": "12.00",
  "selling_price": "44.00",
  "is_max": true,
  "is_wholesale": false
}
```

#### عرض الجملة:
```json
{
  "id": 200,
  "product": {"id": 456, "name": "Aspirin 100mg"},
  "user": {"id": 20, "name": "شركة الأدوية المتحدة"},
  "selling_discount_percentage": "18.00",
  "selling_price": "41.00",
  "is_max": false,
  "is_wholesale": true,
  "is_max_wholesale": true,
  "wholesale_min_quantity": 50,
  "wholesale_increment": 10
}
```

**النتيجة**:
- الصيدليات الصغيرة تشتري من العرض العادي (12% خصم، بدون حد أدنى)
- الشركات تشتري من عرض الجملة (18% خصم، لكن بحد أدنى 50 علبة)

---

## متى تستخدم أيهما؟

### استخدم **العروض العادية** إذا:
- ✅ المتجر صغير وليس شركة
- ✅ الكميات صغيرة (مثلاً 10-50 علبة)
- ✅ تريد مرونة في الطلب
- ✅ الحد الأدنى بالمبلغ وليس العدد

### استخدم **عروض الجملة** إذا:
- ✅ المتجر شركة (`company=True`)
- ✅ الكميات كبيرة (مثلاً 100+ علبة)
- ✅ تريد التحكم في الزيادات المسموح بها
- ✅ تريد خصومات أكبر للكميات الكبيرة

---

## السيناريوهات الشائعة

### سيناريو 1: صيدلية صغيرة تريد شراء 20 علبة
```
المنتج: Paracetamol, السعر: 10 جنيه

العرض العادي:
- خصم: 10%
- السعر: 9 جنيه
- الحد الأدنى: 50 جنيه
- إجمالي: 20 × 9 = 180 جنيه ✅

عرض الجملة:
- خصم: 15%
- السعر: 8.5 جنيه
- الحد الأدنى: 50 علبة
- لا يمكن الشراء ❌ (أقل من 50 علبة)

✅ تستخدم العرض العادي
```

---

### سيناريو 2: شركة تريد شراء 100 علبة
```
المنتج: Paracetamol, السعر: 10 جنيه

العرض العادي:
- خصم: 10%
- السعر: 9 جنيه
- إجمالي: 100 × 9 = 900 جنيه

عرض الجملة:
- خصم: 15%
- السعر: 8.5 جنيه
- الحد الأدنى: 50 علبة ✅
- إجمالي: 100 × 8.5 = 850 جنيه

✅ تستخدم عرض الجملة (توفير 50 جنيه!)
```

---

## الخلاصة

| النقطة | العروض العادية | عروض الجملة |
|-------|----------------|--------------|
| **المستخدم** | أي متجر | شركات فقط |
| **الكمية** | صغيرة | كبيرة |
| **الخصم** | عادي (10-12%) | أكبر (15-20%) |
| **الحد الأدنى** | بالمبلغ | بعدد العلب |
| **المرونة** | عالية | محدودة (زيادات محددة) |
| **الاستخدام** | يومي | بالجملة |

---

**ملاحظة**: كلا النظامين يعملان بشكل مستقل تماماً، ويمكن للمنتج الواحد أن يكون له عروض في النظامين معاً!

