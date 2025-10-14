# تسجيل دخول الصيدلية - Pharmacy Login

## URL الخاص بالصيدليات / Pharmacy-Specific URL

```
POST /accounts/pharmacy-login/
```

هذا الـ URL مخصص **فقط** للمستخدمين الذين لديهم `role=PHARMACY`

This URL is **only** for users with `role=PHARMACY`

---

## الفرق بين /login/ و /pharmacy-login/

### `/accounts/login/` - تسجيل دخول عام
- يقبل جميع أنواع المستخدمين (Admin, Pharmacy, Sales, etc.)
- Accepts all user types

### `/accounts/pharmacy-login/` - تسجيل دخول خاص بالصيدليات ✓
- يقبل فقط المستخدمين الذين `role=PHARMACY`
- يرفض أي مستخدم آخر برسالة خطأ
- Only accepts users with `role=PHARMACY`
- Rejects all other users with error message

---

## الاستخدام / Usage

### Request Example

```bash
curl -X POST http://localhost:8000/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "+201234567890",
    "password": "your-password"
  }'
```

### Response - نجاح (Pharmacy User)

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "role": "PHARMACY",
  "new_login": true,
  "user_id": 123,
  "name": "صيدلية النور"
}
```

### Response - خطأ (Non-Pharmacy User)

إذا حاول مستخدم ليس صيدلية تسجيل الدخول:

```json
{
  "error": "هذا الحساب ليس حساب صيدلية / This account is not a pharmacy account"
}
```

**Status Code:** `403 Forbidden`

---

## أمثلة الاستخدام / Usage Examples

### Python

```python
import requests

url = "http://localhost:8000/accounts/pharmacy-login/"
data = {
    "username": "+201234567890",
    "password": "SecurePass123"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    token = result['token']
    print(f"تسجيل دخول ناجح! Token: {token}")
    print(f"اسم الصيدلية: {result['name']}")
elif response.status_code == 403:
    print("خطأ: هذا الحساب ليس حساب صيدلية")
else:
    print(f"خطأ: {response.json()}")
```

### JavaScript

```javascript
const url = 'http://localhost:8000/accounts/pharmacy-login/';
const data = {
  username: '+201234567890',
  password: 'SecurePass123'
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
.then(response => {
  if (response.status === 403) {
    throw new Error('هذا الحساب ليس حساب صيدلية');
  }
  return response.json();
})
.then(result => {
  console.log('Token:', result.token);
  console.log('اسم الصيدلية:', result.name);
  
  // حفظ التوكن
  localStorage.setItem('authToken', result.token);
})
.catch(error => {
  console.error('خطأ:', error);
});
```

### cURL

```bash
# تسجيل دخول صيدلية
curl -X POST http://localhost:8000/accounts/pharmacy-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "+201234567890", "password": "password123"}'
```

---

## HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>تسجيل دخول الصيدلية</title>
</head>
<body>
    <h2>تسجيل دخول الصيدلية</h2>
    <form id="pharmacyLoginForm">
        <input type="tel" id="username" placeholder="رقم الهاتف +201234567890" required>
        <input type="password" id="password" placeholder="كلمة المرور" required>
        <button type="submit">تسجيل الدخول</button>
    </form>
    <div id="message"></div>

    <script>
        document.getElementById('pharmacyLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('http://localhost:8000/accounts/pharmacy-login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('message').innerHTML = 
                        `<p style="color: green;">مرحباً ${data.name}!</p>`;
                    localStorage.setItem('authToken', data.token);
                } else if (response.status === 403) {
                    document.getElementById('message').innerHTML = 
                        `<p style="color: red;">${data.error}</p>`;
                } else {
                    document.getElementById('message').innerHTML = 
                        `<p style="color: red;">خطأ في تسجيل الدخول</p>`;
                }
            } catch (error) {
                document.getElementById('message').innerHTML = 
                    `<p style="color: red;">خطأ في الاتصال: ${error}</p>`;
            }
        });
    </script>
</body>
</html>
```

---

## الحقول المطلوبة / Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | String (Phone) | Yes | رقم الهاتف مع رمز الدولة |
| password | String | Yes | كلمة المرور |

---

## الحقول في الاستجابة / Response Fields

### نجاح / Success Response

| Field | Type | Description |
|-------|------|-------------|
| token | String | رمز المصادقة للاستخدام في الطلبات القادمة |
| role | String | دائماً "PHARMACY" |
| new_login | Boolean | هل هذا تسجيل دخول جديد؟ |
| user_id | Integer | معرف المستخدم |
| name | String | اسم الصيدلية |

### خطأ / Error Response

| Field | Type | Description |
|-------|------|-------------|
| error | String | رسالة الخطأ |

---

## رموز الحالة / Status Codes

- `200 OK` - تسجيل دخول ناجح
- `400 Bad Request` - بيانات خاطئة أو ناقصة
- `401 Unauthorized` - اسم المستخدم أو كلمة المرور خاطئة
- `403 Forbidden` - المستخدم ليس صيدلية

---

## ملاحظات أمنية / Security Notes

1. استخدم HTTPS في بيئة الإنتاج
2. لا تشارك التوكن مع أي شخص
3. احفظ التوكن بشكل آمن (localStorage أو sessionStorage)
4. استخدم كلمة مرور قوية (8 أحرف على الأقل)

---

## استخدام التوكن بعد تسجيل الدخول

بعد الحصول على التوكن، استخدمه في جميع الطلبات:

```bash
curl -X POST http://localhost:8000/accounts/whoami/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

```javascript
fetch('http://localhost:8000/accounts/whoami/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token YOUR_TOKEN_HERE'
  }
})
```

---

## الخلاصة / Summary

✅ **استخدم** `/accounts/pharmacy-login/` لتطبيقات الصيدليات
- أكثر أماناً
- يمنع المستخدمين غير الصيدليات من الدخول
- يعطي معلومات إضافية (user_id, name)

❌ **لا تستخدم** `/accounts/login/` للصيدليات إذا أردت التأكد من أن المستخدم صيدلية

---

## الدعم / Support

للمزيد من المعلومات:
- API Documentation: http://localhost:8000/api/schema/swagger/
- تسجيل صيدلية جديدة: POST /accounts/register/pharmacy/

