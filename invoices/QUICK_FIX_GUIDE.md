# إصلاح سريع - Endpoint الإغلاق
# Quick Fix - Close Endpoint

## ❌ المشكلة | The Problem

```bash
# هذا خطأ ❌
POST http://129.212.140.152/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}
```

**الخطأ:**
- Method خطأ: استخدام `POST` بدلاً من `PATCH`
- `UpdateAPIView` يتطلب `PATCH` أو `PUT`

---

## ✅ الحل | The Solution

```bash
# استخدم PATCH ✅
PATCH http://129.212.140.152/invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}
```

---

## 📋 أمثلة صحيحة | Correct Examples

### استخدام cURL:
```bash
curl -X PATCH http://129.212.140.152/invoices/sale-invoices/1/change-state/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status": "closed"}'
```

### استخدام JavaScript/Fetch:
```javascript
fetch('http://129.212.140.152/invoices/sale-invoices/1/change-state/', {
  method: 'PATCH',  // ✅ PATCH وليس POST
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({status: 'closed'})
})
```

### استخدام Postman:
```
Method: PATCH  ✅
URL: http://129.212.140.152/invoices/sale-invoices/1/change-state/
Body (JSON):
{
  "status": "closed"
}
```

### استخدام HTTPie:
```bash
http PATCH http://129.212.140.152/invoices/sale-invoices/1/change-state/ \
  status=closed
```

---

## 🔍 جميع Endpoints الصحيحة | All Correct Endpoints

| العملية | Method | URL |
|---------|--------|-----|
| فحص إمكانية الإغلاق | `GET` | `/sale-invoices/1/check-closeability/` |
| إغلاق الفاتورة | `PATCH` | `/sale-invoices/1/change-state/` ✅ |
| فتح فاتورة مغلقة | `PATCH` | `/sale-invoices/1/change-state/` |
| تحديث عنصر | `PATCH` | `/sale-invoice-items/2/` |
| تحديث حالة عنصر | `PATCH` | `/sale-invoice-items/2/change-state/` |

---

## ⚠️ HTTP Methods المطلوبة | Required HTTP Methods

### UpdateAPIView:
- ✅ `PATCH` - تحديث جزئي (Partial Update)
- ✅ `PUT` - تحديث كامل (Full Update)
- ❌ `POST` - **غير مدعوم!**

### CreateAPIView:
- ✅ `POST` - إنشاء
- ❌ `PATCH` - غير مدعوم

---

## 🎯 الطريقة الصحيحة | Correct Way

```bash
# 1. فحص أولاً (GET)
GET /invoices/sale-invoices/1/check-closeability/

# Response: {"can_close": true}

# 2. أغلق (PATCH) ✅
PATCH /invoices/sale-invoices/1/change-state/
{
  "status": "closed"
}
```

---

## 💡 نصيحة | Tip

استخدم دائماً:
- `GET` للقراءة
- `POST` للإنشاء
- `PATCH` للتحديث الجزئي
- `PUT` للتحديث الكامل
- `DELETE` للحذف

---

**جرب الآن مع PATCH بدلاً من POST!** 🚀

