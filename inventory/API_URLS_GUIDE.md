# دليل URLs نظام المخزون
# Inventory API URLs Guide

## 📦 قائمة أصناف المخزون

### 🔗 الـ URL الأساسي

```
GET http://129.212.140.152/inventory/inventory-items/
```

---

## 🔍 البحث (Search)

### البحث بالاسم

```http
# بحث عن أصناف تبدأ بـ "para"
GET http://129.212.140.152/inventory/inventory-items/?search=para

# بحث عن "ibuprofen"
GET http://129.212.140.152/inventory/inventory-items/?search=ibuprofen

# بحث عن "aspirin"
GET http://129.212.140.152/inventory/inventory-items/?search=aspirin
```

**ملاحظة**: البحث يبحث في **اسم المنتج** فقط ويبدأ من أول الاسم (`^product__name`)

---

## 🎯 الفلترة (Filtering)

### 1. حسب المخزن

```http
# أصناف المخزن رقم 1
GET http://129.212.140.152/inventory/inventory-items/?inventory=1

# أصناف عدة مخازن
GET http://129.212.140.152/inventory/inventory-items/?inventory=1,2,3
```

---

### 2. حسب المنتج

```http
# جميع عناصر المنتج رقم 10
GET http://129.212.140.152/inventory/inventory-items/?product=10

# عدة منتجات
GET http://129.212.140.152/inventory/inventory-items/?product=10,20,30
```

**فائدة**: تعرف كل دفعات (batches) نفس المنتج في المخزن

---

## 📊 الترتيب (Ordering)

### حسب الاسم

```http
# ترتيب أبجدي (A → Z)
GET http://129.212.140.152/inventory/inventory-items/?o=product__name

# عكسي (Z → A)
GET http://129.212.140.152/inventory/inventory-items/?o=-product__name
```

---

### حسب السعر

```http
# الأرخص أولاً
GET http://129.212.140.152/inventory/inventory-items/?o=purchase_price

# الأغلى أولاً
GET http://129.212.140.152/inventory/inventory-items/?o=-purchase_price

# ترتيب حسب سعر البيع
GET http://129.212.140.152/inventory/inventory-items/?o=selling_price
```

---

### حسب الكمية

```http
# الأقل كمية أولاً (اللي على وشك الخلاص)
GET http://129.212.140.152/inventory/inventory-items/?o=remaining_quantity

# الأكثر كمية أولاً
GET http://129.212.140.152/inventory/inventory-items/?o=-remaining_quantity

# ترتيب حسب الكمية الأصلية
GET http://129.212.140.152/inventory/inventory-items/?o=quantity
```

---

### حسب الخصم

```http
# أقل خصم شراء
GET http://129.212.140.152/inventory/inventory-items/?o=purchase_discount_percentage

# أعلى خصم شراء
GET http://129.212.140.152/inventory/inventory-items/?o=-purchase_discount_percentage

# أعلى خصم بيع
GET http://129.212.140.152/inventory/inventory-items/?o=-selling_discount_percentage
```

---

### حسب تاريخ انتهاء الصلاحية

```http
# الأقرب انتهاء أولاً
GET http://129.212.140.152/inventory/inventory-items/?o=product_expiry_date

# الأبعد انتهاء أولاً
GET http://129.212.140.152/inventory/inventory-items/?o=-product_expiry_date
```

---

### حسب رقم التشغيل

```http
GET http://129.212.140.152/inventory/inventory-items/?o=operating_number
```

---

## 🔢 Pagination

### تحديد عدد النتائج

```http
# عرض 20 نتيجة في الصفحة
GET http://129.212.140.152/inventory/inventory-items/?ps=20

# عرض 50 نتيجة
GET http://129.212.140.152/inventory/inventory-items/?ps=50

# عرض 100 نتيجة
GET http://129.212.140.152/inventory/inventory-items/?ps=100
```

---

### الانتقال بين الصفحات

```http
# الصفحة الأولى
GET http://129.212.140.152/inventory/inventory-items/?p=1

# الصفحة الثانية
GET http://129.212.140.152/inventory/inventory-items/?p=2

# الصفحة 3 مع 50 نتيجة في كل صفحة
GET http://129.212.140.152/inventory/inventory-items/?p=3&ps=50
```

---

## 🎨 دمج البحث والفلترة والترتيب

### مثال 1: بحث + ترتيب

```http
# ابحث عن "para" ورتب حسب الكمية الأقل
GET http://129.212.140.152/inventory/inventory-items/?search=para&o=remaining_quantity
```

---

### مثال 2: فلترة + ترتيب + pagination

```http
# منتج رقم 10، مرتب حسب تاريخ الصلاحية، 20 نتيجة
GET http://129.212.140.152/inventory/inventory-items/?product=10&o=product_expiry_date&ps=20
```

---

### مثال 3: بحث + فلترة + ترتيب

```http
# بحث عن "ibuprofen" في المخزن رقم 1، مرتب حسب السعر
GET http://129.212.140.152/inventory/inventory-items/?search=ibu&inventory=1&o=purchase_price
```

---

## 🎯 أمثلة حالات استخدام شائعة

### 1️⃣ الأصناف الأقل في المخزن (تحتاج طلب)

```http
GET http://129.212.140.152/inventory/inventory-items/?o=remaining_quantity&ps=10
```

الـ 10 أصناف الأقل كمية

---

### 2️⃣ الأصناف القريبة من انتهاء الصلاحية

```http
GET http://129.212.140.152/inventory/inventory-items/?o=product_expiry_date&ps=20
```

أول 20 صنف الأقرب لانتهاء الصلاحية

---

### 3️⃣ الأصناف الأغلى في المخزن

```http
GET http://129.212.140.152/inventory/inventory-items/?o=-purchase_price&ps=10
```

الـ 10 أصناف الأغلى سعر شراء

---

### 4️⃣ أصناف من مورد معين (عن طريق رقم فاتورة)

```http
# هذا يحتاج معرفة معرف عنصر فاتورة الشراء
# الطريقة الأفضل: البحث بالاسم أو المنتج
GET http://129.212.140.152/inventory/inventory-items/?search=para
```

---

### 5️⃣ جميع دفعات منتج معين

```http
# كل دفعات Paracetamol في المخزن
GET http://129.212.140.152/inventory/inventory-items/?product=10

# مرتبة حسب تاريخ الصلاحية
GET http://129.212.140.152/inventory/inventory-items/?product=10&o=product_expiry_date
```

---

## 📋 قائمة Parameters الكاملة

| Parameter | القيمة | الوصف | مثال |
|-----------|--------|-------|------|
| `search` | نص | بحث في اسم المنتج | `?search=para` |
| `inventory` | أرقام | فلترة حسب المخزن | `?inventory=1` أو `?inventory=1,2` |
| `product` | أرقام | فلترة حسب المنتج | `?product=10` أو `?product=10,20` |
| `o` | اسم حقل | ترتيب تصاعدي | `?o=purchase_price` |
| `o` | `-اسم_حقل` | ترتيب تنازلي | `?o=-remaining_quantity` |
| `p` | رقم | رقم الصفحة | `?p=2` |
| `ps` | رقم | عدد النتائج في الصفحة | `?ps=50` |

---

## 🎨 حقول الترتيب المتاحة

| الحقل | الوصف |
|-------|-------|
| `product__name` | اسم المنتج |
| `product__public_price` | سعر الجمهور |
| `product_expiry_date` | تاريخ انتهاء الصلاحية |
| `operating_number` | رقم التشغيل |
| `purchase_discount_percentage` | نسبة خصم الشراء |
| `purchase_price` | سعر الشراء |
| `selling_discount_percentage` | نسبة خصم البيع |
| `selling_price` | سعر البيع |
| `quantity` | الكمية الأصلية |
| `remaining_quantity` | الكمية المتبقية |

**لعكس الترتيب** أضف `-` قبل اسم الحقل: `?o=-remaining_quantity`

---

## 💡 أمثلة مفيدة جاهزة

### 📊 تقارير جاهزة

```http
# 1. الأصناف اللي على وشك الخلاص (أقل 10 كمية)
http://129.212.140.152/inventory/inventory-items/?o=remaining_quantity&ps=10

# 2. الأصناف اللي هتخلص صلاحيتها قريب (أقرب 20)
http://129.212.140.152/inventory/inventory-items/?o=product_expiry_date&ps=20

# 3. أغلى 10 أصناف في المخزن
http://129.212.140.152/inventory/inventory-items/?o=-purchase_price&ps=10

# 4. الأصناف بأعلى خصم شراء (أحسن صفقات)
http://129.212.140.152/inventory/inventory-items/?o=-purchase_discount_percentage&ps=10

# 5. جميع الأصناف مرتبة أبجدياً
http://129.212.140.152/inventory/inventory-items/?o=product__name

# 6. الصفحة الأولى (50 صنف)
http://129.212.140.152/inventory/inventory-items/?ps=50&p=1

# 7. بحث عن كل منتجات "paracetamol"
http://129.212.140.152/inventory/inventory-items/?search=paracetamol

# 8. جميع عناصر منتج رقم 10، مرتبة حسب الصلاحية
http://129.212.140.152/inventory/inventory-items/?product=10&o=product_expiry_date
```

---

## 🌐 URLs الأخرى (غير الفلترة)

### عرض تفاصيل صنف معين

```http
GET http://129.212.140.152/inventory/inventory-items/1/
```

---

### عرض معلومات المخزن

```http
GET http://129.212.140.152/inventory/inventories/
```

**الاستجابة:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Auto created Main Inventory",
      "type": "main",
      "total_items": 6,
      "total_quantity": 135,
      "total_purchase_price": 36177.60,
      "total_selling_price": 38500.00,
      "items_url": "http://129.212.140.152/inventory/inventory-items/?inventory=1"
    }
  ]
}
```

---

## 📱 أمثلة برمجية

### JavaScript/React

```javascript
const BASE_URL = "http://129.212.140.152";
const TOKEN = "your-token-here";

// 1. جميع الأصناف
const getAllItems = async () => {
  const response = await fetch(
    `${BASE_URL}/inventory/inventory-items/`,
    { headers: { 'Authorization': `Token ${TOKEN}` }}
  );
  return await response.json();
};

// 2. بحث بالاسم
const searchByName = async (name) => {
  const response = await fetch(
    `${BASE_URL}/inventory/inventory-items/?search=${name}`,
    { headers: { 'Authorization': `Token ${TOKEN}` }}
  );
  return await response.json();
};

// 3. الأصناف الأقل كمية
const getLowStockItems = async (limit = 10) => {
  const response = await fetch(
    `${BASE_URL}/inventory/inventory-items/?o=remaining_quantity&ps=${limit}`,
    { headers: { 'Authorization': `Token ${TOKEN}` }}
  );
  return await response.json();
};

// 4. أصناف منتج معين
const getProductBatches = async (productId) => {
  const response = await fetch(
    `${BASE_URL}/inventory/inventory-items/?product=${productId}`,
    { headers: { 'Authorization': `Token ${TOKEN}` }}
  );
  return await response.json();
};

// 5. فلترة متعددة
const getFilteredItems = async (filters) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${BASE_URL}/inventory/inventory-items/?${params}`,
    { headers: { 'Authorization': `Token ${TOKEN}` }}
  );
  return await response.json();
};

// مثال استخدام:
getFilteredItems({
  search: 'para',
  inventory: 1,
  o: 'remaining_quantity',
  ps: 20
});
```

---

### Python

```python
import requests

BASE_URL = "http://129.212.140.152"
TOKEN = "your-token-here"

headers = {"Authorization": f"Token {TOKEN}"}

# 1. جميع الأصناف
response = requests.get(f"{BASE_URL}/inventory/inventory-items/", headers=headers)
items = response.json()

# 2. بحث
response = requests.get(
    f"{BASE_URL}/inventory/inventory-items/",
    params={"search": "para"},
    headers=headers
)

# 3. فلترة وترتيب
response = requests.get(
    f"{BASE_URL}/inventory/inventory-items/",
    params={
        "product": 10,
        "o": "remaining_quantity",
        "ps": 20
    },
    headers=headers
)

# 4. الأصناف القليلة
response = requests.get(
    f"{BASE_URL}/inventory/inventory-items/",
    params={
        "o": "remaining_quantity",
        "ps": 10
    },
    headers=headers
)

for item in response.json()['results']:
    print(f"{item['product']['name']}: {item['remaining_quantity']} متبقي")
```

---

## 📝 ملخص سريع

### الـ URL الأساسي
```
http://129.212.140.152/inventory/inventory-items/
```

### أضف Parameters:

| الغرض | Parameter | مثال |
|-------|-----------|------|
| 🔍 **بحث** | `?search=` | `?search=para` |
| 🎯 **فلترة بالمخزن** | `?inventory=` | `?inventory=1` |
| 🎯 **فلترة بالمنتج** | `?product=` | `?product=10` |
| 📊 **ترتيب** | `?o=` | `?o=remaining_quantity` |
| 📄 **عدد النتائج** | `?ps=` | `?ps=50` |
| 📄 **الصفحة** | `?p=` | `?p=2` |

### دمج Parameters:

```
?search=para&inventory=1&o=remaining_quantity&ps=20&p=1
```

---

## 🎯 الأكثر استخداماً

قائمة جاهزة للنسخ:

```
# 1. كل الأصناف
/inventory/inventory-items/

# 2. بحث
/inventory/inventory-items/?search=paracetamol

# 3. أقل 10 كمية
/inventory/inventory-items/?o=remaining_quantity&ps=10

# 4. الأقرب صلاحية
/inventory/inventory-items/?o=product_expiry_date&ps=20

# 5. منتج معين
/inventory/inventory-items/?product=10

# 6. المخزن الرئيسي
/inventory/inventory-items/?inventory=1

# 7. بحث + ترتيب
/inventory/inventory-items/?search=ibu&o=remaining_quantity

# 8. الصفحة 2، 50 نتيجة
/inventory/inventory-items/?p=2&ps=50
```

---

**جاهز للاستخدام!** 📦✨

**آخر تحديث**: 2025-10-10

