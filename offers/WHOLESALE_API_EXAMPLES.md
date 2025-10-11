# أمثلة API لعروض الجملة

## المحتويات
1. [إنشاء عرض جملة](#1-إنشاء-عرض-جملة)
2. [عرض أفضل عروض الجملة](#2-عرض-أفضل-عروض-الجملة)
3. [قائمة جميع عروض الجملة](#3-قائمة-جميع-عروض-الجملة)
4. [رفع عروض من Excel](#4-رفع-عروض-من-excel)
5. [تحديث عرض جملة](#5-تحديث-عرض-جملة)
6. [حذف عرض جملة](#6-حذف-عرض-جملة)
7. [تصدير إلى Excel](#7-تصدير-إلى-excel)
8. [البحث والفلترة](#8-البحث-والفلترة)

---

## 1. إنشاء عرض جملة

### Request
```http
POST /api/offers/wholesale-offers/create/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "product_code": 12345,
  "available_amount": 500,
  "purchase_discount_percentage": 18.50,
  "is_wholesale": true,
  "wholesale_min_quantity": 20,
  "wholesale_increment": 10,
  "min_purchase": 0,
  "operating_number": "OP-2024-W001",
  "product_expiry_date": "2025-12-31",
  "max_amount_per_invoice": 100
}
```

### Response (Success)
```json
{
  "id": 123,
  "product": {
    "id": 456,
    "name": "أسبرين 100 مجم",
    "public_price": "50.00"
  },
  "user": {
    "id": 789,
    "name": "شركة الأدوية المتحدة",
    "username": "united_pharma"
  },
  "available_amount": 500,
  "remaining_amount": 500,
  "purchase_discount_percentage": "18.50",
  "selling_discount_percentage": "15.50",
  "selling_price": "42.25",
  "is_wholesale": true,
  "wholesale_min_quantity": 20,
  "wholesale_increment": 10,
  "is_max_wholesale": true
}
```

### Response (Error - Not a company)
```json
{
  "is_wholesale": ["عروض الجملة متاحة فقط للمتاجر المسجلة كشركات (company=True)."]
}
```

---

## 2. عرض أفضل عروض الجملة

### Request
```http
GET /api/offers/max-wholesale-offers/
Authorization: Bearer YOUR_TOKEN
```

### Response
```json
{
  "count": 150,
  "next": "http://api.example.com/api/offers/max-wholesale-offers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "product": {
        "id": 456,
        "name": "أسبرين 100 مجم",
        "public_price": "50.00"
      },
      "user": {
        "id": 789,
        "name": "شركة الأدوية المتحدة"
      },
      "selling_price": "42.25",
      "selling_discount_percentage": "15.50",
      "actual_discount_precentage": "14.50",
      "actual_offer_price": "42.75",
      "wholesale_min_quantity": 20,
      "wholesale_increment": 10,
      "is_max_wholesale": true,
      "remaining_amount": 500
    }
  ]
}
```

---

## 3. قائمة جميع عروض الجملة

### Request
```http
GET /api/offers/wholesale-offers/
Authorization: Bearer YOUR_TOKEN
```

### مع الترتيب
```http
GET /api/offers/wholesale-offers/?ordering=-selling_discount_percentage
Authorization: Bearer YOUR_TOKEN
```

---

## 4. رفع عروض من Excel

### Request (cURL)
```bash
curl -X POST 'http://api.example.com/api/offers/wholesale-offers/upload/' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'file=@wholesale_offers.xlsx' \
  -F 'user=789' \
  -F 'is_wholesale=true'
```

### Request (Python)
```python
import requests

url = 'http://api.example.com/api/offers/wholesale-offers/upload/'
headers = {'Authorization': 'Bearer YOUR_TOKEN'}
files = {'file': open('wholesale_offers.xlsx', 'rb')}
data = {
    'user': 789,
    'is_wholesale': True
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### Response
```json
{
  "message": "تم رفع 25 عرض جملة بنجاح",
  "count": 25,
  "offers": [123, 124, 125, ...]
}
```

---

## 5. تحديث عرض جملة

### Request
```http
PATCH /api/offers/wholesale-offers/123/change/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "available_amount": 600,
  "wholesale_min_quantity": 25,
  "purchase_discount_percentage": 19.00
}
```

### Response
```json
{
  "id": 123,
  "available_amount": 600,
  "remaining_amount": 600,
  "wholesale_min_quantity": 25,
  "purchase_discount_percentage": "19.00",
  "selling_discount_percentage": "16.00",
  "is_max_wholesale": true
}
```

---

## 6. حذف عرض جملة

### Request
```http
DELETE /api/offers/wholesale-offers/123/destroy/
Authorization: Bearer YOUR_TOKEN
```

### Response
```http
HTTP/1.1 204 No Content
```

---

## 7. تصدير إلى Excel

### Request
```http
GET /api/offers/max-wholesale-offers/excel/
Authorization: Bearer YOUR_TOKEN
```

### مع فلتر payment_period
```http
GET /api/offers/max-wholesale-offers/excel/?payment_period=5
Authorization: Bearer YOUR_TOKEN
```

### Response
يتم تحميل ملف Excel بعنوان:
```
Pharmasky Wholesale offers report - 11-10-2025-15-30-45.xlsx
```

---

## 8. البحث والفلترة

### البحث بالاسم
```http
GET /api/offers/max-wholesale-offers/?search=aspirin
Authorization: Bearer YOUR_TOKEN
```

### فلترة حسب المتجر
```http
GET /api/offers/max-wholesale-offers/?user=789
Authorization: Bearer YOUR_TOKEN
```

### فلترة حسب المنتج
```http
GET /api/offers/max-wholesale-offers/?product=456
Authorization: Bearer YOUR_TOKEN
```

### فلترة حسب الحد الأدنى
```http
GET /api/offers/max-wholesale-offers/?wholesale_min_quantity=20
Authorization: Bearer YOUR_TOKEN
```

### فلترة حسب نطاق الحد الأدنى
```http
GET /api/offers/max-wholesale-offers/?wholesale_min_quantity__gte=10&wholesale_min_quantity__lte=50
Authorization: Bearer YOUR_TOKEN
```

### فلترة حسب الحاجة (needed)
```http
GET /api/offers/max-wholesale-offers/?needed=true
Authorization: Bearer YOUR_TOKEN
```

### جمع عدة فلاتر
```http
GET /api/offers/max-wholesale-offers/?user=789&needed=true&wholesale_min_quantity__lte=20
Authorization: Bearer YOUR_TOKEN
```

### الترتيب
```http
# ترتيب تصاعدي حسب السعر
GET /api/offers/max-wholesale-offers/?ordering=selling_price

# ترتيب تنازلي حسب الخصم
GET /api/offers/max-wholesale-offers/?ordering=-selling_discount_percentage

# ترتيب حسب اسم المنتج
GET /api/offers/max-wholesale-offers/?ordering=product__name

# ترتيب حسب الحد الأدنى
GET /api/offers/max-wholesale-offers/?ordering=wholesale_min_quantity
```

---

## أمثلة متقدمة

### مثال 1: الحصول على عروض جملة لشركة معينة مع حد أدنى معين
```http
GET /api/offers/wholesale-offers/?user=789&wholesale_min_quantity=20&ordering=-selling_discount_percentage
Authorization: Bearer YOUR_TOKEN
```

### مثال 2: البحث عن منتج في عروض الجملة
```http
GET /api/offers/max-wholesale-offers/?search=paracetamol&wholesale_min_quantity__lte=15
Authorization: Bearer YOUR_TOKEN
```

### مثال 3: الحصول على أفضل 10 عروض جملة
```http
GET /api/offers/max-wholesale-offers/?page_size=10&ordering=-selling_discount_percentage
Authorization: Bearer YOUR_TOKEN
```

---

## كود JavaScript/TypeScript

### مثال React/Next.js
```typescript
// الحصول على أفضل عروض الجملة
async function getMaxWholesaleOffers(searchTerm?: string) {
  const url = new URL('/api/offers/max-wholesale-offers/', 'http://api.example.com');
  
  if (searchTerm) {
    url.searchParams.append('search', searchTerm);
  }
  
  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return response.json();
}

// إنشاء عرض جملة
async function createWholesaleOffer(data: WholesaleOfferData) {
  const response = await fetch('/api/offers/wholesale-offers/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      ...data,
      is_wholesale: true,
    }),
  });
  
  return response.json();
}

// رفع ملف Excel
async function uploadWholesaleOffers(file: File, userId: number) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user', userId.toString());
  formData.append('is_wholesale', 'true');
  
  const response = await fetch('/api/offers/wholesale-offers/upload/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });
  
  return response.json();
}
```

---

## الملاحظات

1. **التوكن**: استبدل `YOUR_TOKEN` بالتوكن الفعلي للمصادقة
2. **الترميز**: تأكد من استخدام `Content-Type: application/json` للطلبات JSON
3. **الملفات**: استخدم `multipart/form-data` عند رفع الملفات
4. **الأخطاء**: تحقق من رمز الحالة HTTP ورسائل الخطأ في الاستجابة
5. **الصلاحيات**: تأكد من أن المستخدم لديه الصلاحيات المناسبة

---

## رموز حالة HTTP الشائعة

- `200 OK`: نجح الطلب
- `201 Created`: تم إنشاء المورد بنجاح
- `204 No Content`: تم الحذف بنجاح
- `400 Bad Request`: خطأ في البيانات المرسلة
- `401 Unauthorized`: غير مصرح
- `403 Forbidden`: ممنوع (لا توجد صلاحيات)
- `404 Not Found`: المورد غير موجود
- `500 Internal Server Error`: خطأ في الخادم

