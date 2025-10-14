# ملخص سريع - Pharmacy Login URL

## ✅ تم إنشاء URL خاص بالصيدليات

### الـ URL الجديد:
```
POST /accounts/pharmacy-login/
```

---

## 🎯 الاستخدام السريع

### 1. Request
```json
POST /accounts/pharmacy-login/
Content-Type: application/json

{
  "username": "+201234567890",
  "password": "your-password"
}
```

### 2. Response (نجاح ✅)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "role": "PHARMACY",
  "new_login": true,
  "user_id": 123,
  "name": "صيدلية النور"
}
```

### 3. Response (خطأ - ليس صيدلية ❌)
```json
{
  "error": "هذا الحساب ليس حساب صيدلية / This account is not a pharmacy account"
}
```
**Status: 403 Forbidden**

---

## 🔍 الفرق الأساسي

| Feature | `/accounts/login/` | `/accounts/pharmacy-login/` ✓ |
|---------|-------------------|------------------------------|
| يقبل جميع المستخدمين | ✅ Yes | ❌ No |
| يقبل الصيدليات فقط | ❌ No | ✅ Yes |
| يعطي user_id | ❌ No | ✅ Yes |
| يعطي name | ❌ No | ✅ Yes |
| آمن للصيدليات | ⚠️ Partial | ✅ Yes |

---

## 🧪 اختبار سريع

### باستخدام cURL:
```bash
curl -X POST http://localhost:8000/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "+201234567890", "password": "password123"}'
```

### باستخدام Python:
```bash
python test_pharmacy_login.py
```

### باستخدام JavaScript:
```javascript
fetch('http://localhost:8000/accounts/pharmacy-login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: '+201234567890',
    password: 'password123'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 📁 الملفات المتأثرة

✅ `accounts/views.py` - تم إضافة `PharmacyLoginAPIView`
✅ `accounts/urls.py` - تم إضافة المسار `/pharmacy-login/`

---

## 🎓 معلومات إضافية

📖 **توثيق كامل:** `PHARMACY_LOGIN.md`
🧪 **سكريبت الاختبار:** `test_pharmacy_login.py`
🌐 **API Docs:** http://localhost:8000/api/schema/swagger/

---

## ✨ المميزات

1. ✅ **أمان أفضل** - يرفض المستخدمين غير الصيدليات
2. ✅ **معلومات إضافية** - يعطي user_id و name
3. ✅ **سهولة الاستخدام** - نفس طريقة /login/
4. ✅ **رسائل خطأ واضحة** - بالعربية والإنجليزية

---

## 🚀 البدء السريع

1. **تشغيل السيرفر:**
   ```bash
   python manage.py runserver
   ```

2. **اختبار الـ URL:**
   ```bash
   python test_pharmacy_login.py
   ```

3. **استخدام في التطبيق:**
   استبدل `/accounts/login/` بـ `/accounts/pharmacy-login/`

---

**تم! ✅**

