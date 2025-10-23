# Token Authentication Guide

## 🔐 نظرة عامة

تم تحديث الـ FastAPI AI Agent ليدعم المصادقة باستخدام التوكن (Token Authentication) بدلاً من الاعتماد على `user_id` فقط.

## 🚀 المميزات الجديدة

### ✅ **دعم التوكن:**
- **JWT Token** - دعم كامل لـ JWT tokens
- **API Token** - دعم للـ API tokens
- **Bearer Authentication** - دعم لـ Authorization header
- **Fallback Support** - دعم للـ user_id كبديل

### ✅ **الأمان:**
- **Token Validation** - التحقق من صحة التوكن
- **User Authentication** - مصادقة المستخدم
- **Permission Checking** - فحص الصلاحيات
- **Secure Headers** - رؤوس آمنة

## 📡 **API Endpoints المحدثة**

### 1. **Chat API مع التوكن:**
```http
POST /agent/chat
Content-Type: application/json
Authorization: Bearer your_jwt_token

{
  "message": "صباح الخير",
  "session_id": 123,
  "token": "your_jwt_token"
}
```

### 2. **Voice API مع التوكن:**
```http
POST /agent/voice
Content-Type: application/json
Authorization: Bearer your_jwt_token

{
  "audio_base64": "base64_encoded_audio",
  "session_id": 123,
  "token": "your_jwt_token"
}
```

### 3. **Call API مع التوكن:**
```http
POST /agent/call
Content-Type: application/json
Authorization: Bearer your_jwt_token

{
  "audio_chunk_base64": "base64_encoded_audio_chunk",
  "session_id": 123,
  "token": "your_jwt_token"
}
```

### 4. **Process API مع التوكن:**
```http
POST /agent/process
Content-Type: application/json
Authorization: Bearer your_jwt_token

{
  "query": "عايز 10 علب باراسيتامول",
  "session_id": "session_123",
  "token": "your_jwt_token"
}
```

### 5. **Function APIs مع التوكن:**
```http
POST /agent/check-availability
Content-Type: application/json
Authorization: Bearer your_jwt_token

{
  "medicine_name": "باراسيتامول",
  "token": "your_jwt_token"
}
```

### 6. **Token Verification:**
```http
POST /agent/verify-token
Content-Type: application/json

{
  "token": "your_jwt_token"
}
```

## 🔧 **طرق المصادقة**

### **الطريقة الأولى: Authorization Header**
```javascript
fetch('http://129.212.140.152:8001/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_jwt_token'
  },
  body: JSON.stringify({
    message: "صباح الخير"
  })
})
```

### **الطريقة الثانية: Token في Body**
```javascript
fetch('http://129.212.140.152:8001/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "صباح الخير",
    token: "your_jwt_token"
  })
})
```

### **الطريقة الثالثة: Fallback (user_id)**
```javascript
fetch('http://129.212.140.152:8001/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "صباح الخير",
    context: {
      user_id: 5
    }
  })
})
```

## 🛡️ **الأمان والحماية**

### **Middleware Protection:**
- جميع الـ `/agent/*` endpoints محمية
- التحقق التلقائي من التوكن
- رفض الطلبات غير المصرح بها

### **Endpoints غير المحمية:**
- `/health` - فحص الحالة
- `/docs` - التوثيق
- `/openapi.json` - OpenAPI schema
- `/agent/verify-token` - التحقق من التوكن

## 📝 **أمثلة الاستخدام**

### **JavaScript/TypeScript:**
```javascript
// استخدام Authorization header
const apiCall = async (message, token) => {
  const response = await fetch('http://129.212.140.152:8001/agent/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: message
    })
  });
  return response.json();
};

// استخدام token في body
const apiCallWithToken = async (message, token) => {
  const response = await fetch('http://129.212.140.152:8001/agent/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      token: token
    })
  });
  return response.json();
};
```

### **Python:**
```python
import httpx

# استخدام Authorization header
async def chat_with_auth(message, token):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://129.212.140.152:8001/agent/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={"message": message}
        )
        return response.json()

# استخدام token في body
async def chat_with_token(message, token):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://129.212.140.152:8001/agent/chat",
            headers={"Content-Type": "application/json"},
            json={
                "message": message,
                "token": token
            }
        )
        return response.json()
```

### **cURL:**
```bash
# Authorization header
curl -X POST http://129.212.140.152:8001/agent/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"message": "صباح الخير"}'

# Token في body
curl -X POST http://129.212.140.152:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "صباح الخير", "token": "your_jwt_token"}'
```

## 🔄 **التوافق مع الإصدارات السابقة**

### **دعم user_id:**
- لا يزال يعمل مع `context.user_id`
- يعمل كـ fallback عند عدم وجود token
- يحافظ على التوافق مع الكود القديم

### **Migration Path:**
```javascript
// الكود القديم (لا يزال يعمل)
{
  "message": "صباح الخير",
  "context": {
    "user_id": 5
  }
}

// الكود الجديد (مستحسن)
{
  "message": "صباح الخير",
  "token": "jwt_token"
}
```

## 🚨 **رسائل الخطأ**

### **401 Unauthorized:**
```json
{
  "detail": "Authentication required",
  "error": "Missing token"
}
```

### **401 Invalid Token:**
```json
{
  "detail": "Authentication failed",
  "error": "Invalid token"
}
```

### **400 Missing Auth:**
```json
{
  "detail": "Either token or user_id in context is required"
}
```

## 🎯 **الخلاصة**

الآن يمكنك استخدام الـ agent مع:

1. **JWT Tokens** - للمصادقة الآمنة
2. **API Tokens** - للوصول المبرمج
3. **Authorization Headers** - للمعايير القياسية
4. **Fallback Support** - للتوافق مع الكود القديم

**جميع الـ endpoints تدعم التوكن الآن!** 🎉
