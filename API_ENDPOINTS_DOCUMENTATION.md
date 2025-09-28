# 🔌 PharmasSky API Endpoints Documentation

دليل شامل لجميع نقاط النهاية في نظام PharmasSky لاستخدامها مع الفرونت إند

## 🔐 Authentication

جميع APIs تتطلب Token Authentication عبر Header:
```
Authorization: Token your_token_here
```

## Base URL
```
http://129.212.140.152/
```

---

## 📋 فهرس النقاط النهائية

- [🔑 Authentication](#-authentication-endpoints)
- [👤 Accounts](#-accounts-endpoints) 
- [🏪 Market](#-market-endpoints)
- [📦 Inventory](#-inventory-endpoints)
- [📄 Invoices](#-invoices-endpoints)
- [💰 Finance](#-finance-endpoints)
- [🎯 Offers](#-offers-endpoints)
- [👥 Profiles](#-profiles-endpoints)
- [🛒 Shop](#-shop-endpoints)
- [📢 Ads](#-ads-endpoints)
- [🔔 Push Notifications](#-push-notifications)

---

## 🔑 Authentication Endpoints

### POST `/accounts/login/`
**الوصف:** تسجيل الدخول والحصول على Token  
**المطلوب:** لا يتطلب Authentication  
**Request Body:**
```json
{
    "username": "01234567890",  // رقم الهاتف
    "password": "your_password"
}
```
**Response:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "role": "PHARMACY", // أو SALES, MANAGER, etc.
    "new_login": true   // true إذا كان token جديد
}
```

### POST `/accounts/whoami/`
**الوصف:** الحصول على بيانات المستخدم الحالي  
**المطلوب:** Authentication مطلوب  
**Response:**
```json
{
    "id": 1,
    "username": "+201234567890",
    "name": "اسم المستخدم",
    "e_name": "English Name",
    "area": 1,
    "role": "PHARMACY",
    "role_label": "صيدلية",
    "is_superuser": false
}
```

---

## 👤 Accounts Endpoints

### GET `/accounts/users/`
**الوصف:** قائمة جميع المستخدمين (للمديرين)  
**المطلوب:** Staff Role Authentication  
**Query Parameters:**
- `page`: رقم الصفحة
- `page_size`: عدد العناصر في الصفحة

### GET `/accounts/users/{id}/`
**الوصف:** تفاصيل مستخدم معين  
**المطلوب:** Staff Role Authentication

### GET `/accounts/simple-users/`
**الوصف:** قائمة مبسطة للمستخدمين  
**المطلوب:** Authentication مطلوب

### POST `/accounts/register/pharmacy/`
**الوصف:** تسجيل صيدلية جديدة  
**المطلوب:** لا يتطلب Authentication  
**Request Body:**
```json
{
    "username": "01234567890",
    "password": "secure_password",
    "name": "اسم الصيدلية",
    "e_name": "Pharmacy English Name",
    "area": 1
}
```

---

## 🏪 Market Endpoints

### المنتجات (Products)

#### GET `/market/products/`
**الوصف:** قائمة جميع المنتجات  
**Query Parameters:**
- `search`: البحث في اسم المنتج
- `company`: فلتر حسب الشركة
- `category`: فلتر حسب الفئة
- `page`: رقم الصفحة
- `page_size`: عدد العناصر في الصفحة

#### POST `/market/products/create/`
**الوصف:** إضافة منتج جديد  
**المطلوب:** Staff Role Authentication
**Request Body:**
```json
{
    "name": "اسم المنتج",
    "e_name": "Product English Name",
    "company": 1,
    "category": 1,
    "active_ingredient": "المادة الفعالة",
    "description": "وصف المنتج",
    "image": "base64_image_or_url"
}
```

#### GET `/market/products/{id}/`
**الوصف:** تفاصيل منتج معين

#### PUT `/market/products/{id}/change/`
**الوصف:** تحديث منتج  
**المطلوب:** Staff Role Authentication

#### GET `/market/products/object/{id}/product-alternatives/list`
**الوصف:** قائمة البدائل للمنتج

#### GET `/market/products/object/{id}/product-instances/list`
**الوصف:** قائمة نسخ المنتج في المخازن المختلفة

### الشركات والفئات

#### GET `/market/companies/list`
**الوصف:** قائمة جميع الشركات

#### GET `/market/categories/list`
**الوصف:** قائمة جميع فئات المنتجات

### أكواد المنتجات

#### GET `/market/product-codes/`
**الوصف:** قائمة أكواد المنتجات (Barcodes)

### قائمة الرغبات

#### GET `/market/user/product-wishlist/`
**الوصف:** قائمة رغبات المستخدم الحالي

#### POST `/market/user/product-wishlist/create/`
**الوصف:** إضافة منتج لقائمة الرغبات
**Request Body:**
```json
{
    "product": 1,
    "notes": "ملاحظات اختيارية"
}
```

### فلاتر المنتجات

#### GET `/market/filters/products/company`
**الوصف:** فلتر المنتجات حسب الشركة
**Query Parameters:** `company_id`

#### GET `/market/filters/products/category`
**الوصف:** فلتر المنتجات حسب الفئة
**Query Parameters:** `category_id`

#### GET `/market/filters/products/letter`
**الوصف:** فلتر المنتجات حسب الحرف الأول
**Query Parameters:** `letter`

#### GET `/market/filters/products/shape`
**الوصف:** فلتر المنتجات حسب الشكل
**Query Parameters:** `shape`

---

## 📦 Inventory Endpoints

### المخازن (Inventories)

#### GET `/inventory/inventories/`
**الوصف:** قائمة جميع المخازن

#### POST `/inventory/inventories/create/`
**الوصف:** إنشاء مخزن جديد
**Request Body:**
```json
{
    "name": "اسم المخزن",
    "location": "موقع المخزن",
    "description": "وصف المخزن"
}
```

#### GET `/inventory/inventories/{id}/`
**الوصف:** تفاصيل مخزن معين

#### PUT `/inventory/inventories/{id}/change/`
**الوصف:** تحديث بيانات المخزن

### عناصر المخزون (Inventory Items)

#### GET `/inventory/inventory-items/`
**الوصف:** قائمة جميع عناصر المخزون
**Query Parameters:**
- `inventory`: فلتر حسب المخزن
- `product`: فلتر حسب المنتج
- `low_stock`: عرض المنتجات قليلة المخزون

#### POST `/inventory/inventory-items/create/`
**الوصف:** إضافة منتج للمخزن
**Request Body:**
```json
{
    "inventory": 1,
    "product": 1,
    "quantity": 100,
    "unit_price": 50.00,
    "expiry_date": "2025-12-31",
    "batch_number": "BATCH001"
}
```

#### GET `/inventory/inventory-items/{id}/`
**الوصف:** تفاصيل عنصر مخزون معين

#### PUT `/inventory/inventory-items/{id}/change/`
**الوصف:** تحديث عنصر المخزون

#### PUT `/inventory/inventory-items/{id}/change-inventory/`
**الوصف:** نقل منتج من مخزن لآخر

#### DELETE `/inventory/inventory-items/{id}/destroy/`
**الوصف:** حذف عنصر من المخزون

---

## 📄 Invoices Endpoints

### فواتير الشراء (Purchase Invoices)

#### GET `/invoices/purchase-invoices/`
**الوصف:** قائمة فواتير الشراء
**Query Parameters:**
- `status`: فلتر حسب الحالة
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ
- `supplier`: فلتر حسب المورد

#### POST `/invoices/purchase-invoices/create/`
**الوصف:** إنشاء فاتورة شراء جديدة
**Request Body:**
```json
{
    "supplier": 1,
    "invoice_number": "INV001",
    "total_amount": 1000.00,
    "notes": "ملاحظات",
    "items": [
        {
            "product": 1,
            "quantity": 10,
            "unit_price": 50.00,
            "total_price": 500.00
        }
    ]
}
```

#### GET `/invoices/purchase-invoices/{id}/`
**الوصف:** تفاصيل فاتورة شراء

#### PUT `/invoices/purchase-invoices/{id}/change-state/`
**الوصف:** تغيير حالة فاتورة الشراء
**Request Body:**
```json
{
    "status": "APPROVED" // PENDING, APPROVED, REJECTED
}
```

### عناصر فاتورة الشراء

#### GET `/invoices/purchase-invoice-items/`
**الوصف:** قائمة عناصر فواتير الشراء

#### POST `/invoices/purchase-invoice-items/create/`
**الوصف:** إضافة عنصر لفاتورة شراء

#### PUT `/invoices/purchase-invoice-items/{id}/change-state/`
**الوصف:** تغيير حالة عنصر فاتورة

#### PUT `/invoices/purchase-invoice-items/change-state/`
**الوصف:** تغيير حالة عدة عناصر مرة واحدة

#### DELETE `/invoices/purchase-invoice-items/{id}/destroy/`
**الوصف:** حذف عنصر من الفاتورة

### فواتير مرتجع الشراء

#### GET `/invoices/purchase-return-invoices/`
**الوصف:** قائمة فواتير مرتجع الشراء

#### POST `/invoices/purchase-return-invoices/create/`
**الوصف:** إنشاء فاتورة مرتجع شراء

#### GET `/invoices/purchase-return-invoices/{id}/`
**الوصف:** تفاصيل فاتورة مرتجع

#### PUT `/invoices/purchase-return-invoices/{id}/change-state/`
**الوصف:** تغيير حالة فاتورة المرتجع

### فواتير البيع (Sale Invoices)

#### GET `/invoices/sale-invoices/`
**الوصف:** قائمة فواتير البيع
**Query Parameters:**
- `status`: فلتر حسب الحالة  
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ
- `customer`: فلتر حسب العميل

#### POST `/invoices/sale-invoices/create/`
**الوصف:** إنشاء فاتورة بيع جديدة
**Request Body:**
```json
{
    "customer": 1,
    "invoice_number": "SALE001",
    "total_amount": 500.00,
    "discount_amount": 50.00,
    "final_amount": 450.00,
    "items": [
        {
            "product": 1,
            "quantity": 5,
            "unit_price": 100.00,
            "total_price": 500.00
        }
    ]
}
```

#### GET `/invoices/sale-invoices/{id}/`
**الوصف:** تفاصيل فاتورة بيع

#### GET `/invoices/sale-invoices/{id}/download/`
**الوصف:** تحميل فاتورة البيع كـ PDF

#### PUT `/invoices/sale-invoices/{id}/change-state/`
**الوصف:** تغيير حالة فاتورة البيع

### عناصر فاتورة البيع

#### GET `/invoices/sale-invoice-items/`
**الوصف:** قائمة عناصر فواتير البيع

#### POST `/invoices/sale-invoice-items/create/`
**الوصف:** إضافة عنصر لفاتورة بيع

#### PUT `/invoices/sale-invoice-items/{id}/change/`
**الوصف:** تحديث عنصر فاتورة

#### PUT `/invoices/sale-invoice-items/{id}/change-state/`
**الوصف:** تغيير حالة عنصر

#### PUT `/invoices/sale-invoice-items/change-state/`
**الوصف:** تغيير حالة عدة عناصر

#### DELETE `/invoices/sale-invoice-items/{id}/destroy/`
**الوصف:** حذف عنصر من الفاتورة

### فواتير مرتجع البيع

#### GET `/invoices/sale-return-invoices/`
**الوصف:** قائمة فواتير مرتجع البيع

#### POST `/invoices/sale-return-invoices/create/`
**الوصف:** إنشاء فاتورة مرتجع بيع

#### GET `/invoices/sale-return-invoices/{id}/`
**الوصف:** تفاصيل فاتورة مرتجع البيع

#### PUT `/invoices/sale-return-invoices/{id}/change-state/`
**الوصف:** تغيير حالة فاتورة المرتجع

---

## 💰 Finance Endpoints

### الحسابات المالية

#### PUT `/finance/accounts/{id}/change/`
**الوصف:** تحديث بيانات حساب مالي

#### GET `/finance/account-transactions/`
**الوصف:** قائمة حركات الحسابات المالية
**Query Parameters:**
- `account`: فلتر حسب الحساب
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ
- `transaction_type`: نوع العملية

### مدفوعات الشراء

#### GET `/finance/purchase-payments/`
**الوصف:** قائمة مدفوعات الشراء

#### POST `/finance/purchase-payments/create/`
**الوصف:** إنشاء دفع شراء جديد
**Request Body:**
```json
{
    "invoice": 1,
    "amount": 500.00,
    "payment_method": "CASH", // CASH, BANK_TRANSFER, CHECK
    "notes": "ملاحظات الدفع",
    "payment_date": "2024-12-20"
}
```

#### PUT `/finance/purchase-payments/{id}/change/`
**الوصف:** تحديث دفع شراء

#### DELETE `/finance/purchase-payments/{id}/destroy/`
**الوصف:** حذف دفع شراء

### مدفوعات البيع

#### GET `/finance/sale-payments/`
**الوصف:** قائمة مدفوعات البيع

#### POST `/finance/sale-payments/create/`
**الوصف:** إنشاء دفع بيع جديد

#### PUT `/finance/sale-payments/{id}/change/`
**الوصف:** تحديث دفع بيع

#### DELETE `/finance/sale-payments/{id}/destroy/`
**الوصف:** حذف دفع بيع

### معاملات الخزينة

#### GET `/finance/safe-transactions/`
**الوصف:** قائمة معاملات الخزينة

#### POST `/finance/safe-transactions/create/`
**الوصف:** إنشاء معاملة خزينة جديدة
**Request Body:**
```json
{
    "transaction_type": "DEPOSIT", // DEPOSIT, WITHDRAWAL
    "amount": 1000.00,
    "description": "وصف المعاملة",
    "reference_number": "REF001"
}
```

#### GET `/finance/safe/`
**الوصف:** بيانات الخزينة الحالية

---

## 🎯 Offers Endpoints

### العروض

#### GET `/offers/offers/`
**الوصف:** قائمة جميع العروض
**Query Parameters:**
- `active`: عرض العروض النشطة فقط
- `product`: فلتر حسب المنتج
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ

#### POST `/offers/offers/create/`
**الوصف:** إنشاء عرض جديد
**Request Body:**
```json
{
    "product": 1,
    "offer_price": 45.00,
    "original_price": 50.00,
    "discount_percentage": 10.0,
    "start_date": "2024-12-20",
    "end_date": "2024-12-31",
    "description": "وصف العرض"
}
```

#### PUT `/offers/offers/{id}/change/`
**الوصف:** تحديث عرض

#### DELETE `/offers/offers/{id}/destroy/`
**الوصف:** حذف عرض

### أفضل العروض

#### GET `/offers/max-offers/`
**الوصف:** قائمة أفضل العروض الحالية

#### GET `/offers/max-offers/excel/`
**الوصف:** تحميل أفضل العروض كملف Excel

### رفع العروض

#### POST `/offers/offers/upload/`
**الوصف:** رفع العروض من ملف Excel
**Request Body:** `multipart/form-data`
```
file: excel_file.xlsx
```

### عروض المستخدم

#### GET `/offers/user/offers/`
**الوصف:** قائمة عروض المستخدم الحالي

#### POST `/offers/user/offers/create/`
**الوصف:** إنشاء عرض من المستخدم

---

## 👥 Profiles Endpoints

### الملفات الشخصية

#### POST `/profiles/user-profiles/create/`
**الوصف:** إنشاء ملف شخصي للمستخدم
**Request Body:**
```json
{
    "pharmacy_name": "اسم الصيدلية",
    "pharmacy_license": "رقم الترخيص",
    "area": 1,
    "city": 1,
    "address": "العنوان التفصيلي",
    "phone": "01234567890"
}
```

#### PUT `/profiles/user-profiles/{id}/change/`
**الوصف:** تحديث الملف الشخصي

#### GET `/profiles/user-profile/`
**الوصف:** الحصول على الملف الشخصي للمستخدم الحالي

### البيانات المرجعية

#### GET `/profiles/areas/`
**الوصف:** قائمة المناطق

#### GET `/profiles/countries/`
**الوصف:** قائمة الدول

#### GET `/profiles/cities/`
**الوصف:** قائمة المدن
**Query Parameters:**
- `country`: فلتر حسب الدولة

#### GET `/profiles/payment-periods/`
**الوصف:** قائمة فترات السداد

### الشكاوى

#### GET `/profiles/complaints/`
**الوصف:** قائمة الشكاوى

#### POST `/profiles/complaints/create/`
**الوصف:** إنشاء شكوى جديدة
**Request Body:**
```json
{
    "title": "عنوان الشكوى",
    "description": "وصف مفصل للشكوى",
    "priority": "HIGH", // LOW, MEDIUM, HIGH
    "category": "TECHNICAL" // TECHNICAL, BILLING, OTHER
}
```

---

## 🛒 Shop Endpoints

### عربة التسوق

#### GET `/shop/carts/{id}/`
**الوصف:** تفاصيل عربة تسوق معينة

#### GET `/shop/user/cart/`
**الوصف:** عربة التسوق للمستخدم الحالي

#### POST `/shop/user/cart/checkout/`
**الوصف:** إتمام عملية الشراء من العربة
**Request Body:**
```json
{
    "payment_method": "CASH",
    "delivery_address": "عنوان التسليم",
    "notes": "ملاحظات الطلب"
}
```

### عناصر عربة التسوق

#### POST `/shop/user/cart-items/create/`
**الوصف:** إضافة منتج لعربة التسوق
**Request Body:**
```json
{
    "product": 1,
    "quantity": 2
}
```

#### PUT `/shop/user/cart-items/{id}/change/`
**الوصف:** تحديث كمية منتج في العربة
**Request Body:**
```json
{
    "quantity": 5
}
```

#### DELETE `/shop/user/cart-items/{id}/destroy/`
**الوصف:** إزالة منتج من العربة

---

## 📢 Ads Endpoints

#### GET `/ads/`
**الوصف:** قائمة جميع الإعلانات النشطة

---

## 🔔 Push Notifications

### تسجيل الجهاز

#### POST `/push-notifications/devices/fcm/register/`
**الوصف:** تسجيل جهاز لاستقبال الإشعارات
**Request Body:**
```json
{
    "registration_id": "fcm_token_here",
    "type": "android" // أو "ios"
}
```

#### DELETE `/push-notifications/devices/fcm/unregister/`
**الوصف:** إلغاء تسجيل الجهاز

---

## 📊 API Schema Documentation

للحصول على وثائق تفاعلية كاملة:

- **Swagger UI:** `/api/schema/swagger/`
- **ReDoc:** `/api/schema/redoc/`
- **OpenAPI Schema:** `/api/schema/`

---

## 🔧 HTTP Response Codes

- **200 OK:** نجح الطلب
- **201 Created:** تم إنشاء المورد بنجاح
- **400 Bad Request:** خطأ في البيانات المرسلة
- **401 Unauthorized:** غير مصرح بالوصول
- **403 Forbidden:** ممنوع الوصول
- **404 Not Found:** المورد غير موجود
- **500 Internal Server Error:** خطأ في الخادم

---

## 💡 نصائح للتطوير

1. **استخدم Token Authentication** في جميع الطلبات
2. **تعامل مع Pagination** في القوائم الطويلة
3. **استخدم Query Parameters** للفلترة والبحث
4. **تأكد من معالجة الأخطاء** بطريقة صحيحة
5. **اختبر APIs** باستخدام Swagger UI أولاً

---

**تم إنشاء هذا الملف في:** `2024-12-20`  
**إصدار API:** `v1.0`  
**المطور:** Mohamed Sakr
