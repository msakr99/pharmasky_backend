# 🤖 AI Agent Setup Guide

## المشاكل اللي تم إصلاحها ✅

### 1. التطبيق مش مفعّل
تم إضافة `ai_agent` في `INSTALLED_APPS` في `project/settings/base.py`

### 2. إعدادات OpenAI ناقصة
تم إضافة `DIGITALOCEAN_AGENT_URL` في Settings

---

## 🔧 خطوات التفعيل على السيرفر

### 1️⃣ إعداد Environment Variables

قم بإضافة المتغيرات التالية في ملف `.env` على السيرفر:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-api-key-here

# DigitalOcean AI Gateway URL (optional - if using DigitalOcean)
DIGITALOCEAN_AGENT_URL=https://api.openai.com/v1
```

> **ملحوظة:** إذا كنت تستخدم DigitalOcean AI Gateway، استبدل الـ URL بالـ endpoint الخاص بك.

---

### 2️⃣ تشغيل Migrations على السيرفر

```bash
# على السيرفر
cd /path/to/sky
source venv/bin/activate  # أو activate في Windows

# إنشاء migrations
python manage.py makemigrations ai_agent

# تطبيق migrations
python manage.py migrate

# إعادة تشغيل الـ server
sudo systemctl restart gunicorn  # أو pm2 restart أو docker-compose restart
```

---

### 3️⃣ الـ URLs الصحيحة للـ API

#### ❌ خطأ:
```
http://129.212.140.152//api/ai-agent/chat/
```

#### ✅ صح:
```
http://129.212.140.152/ai-agent/chat/
```

---

## 📡 API Endpoints المتاحة

### 1. Chat (محادثة نصية)
```http
POST /ai-agent/chat/
Content-Type: application/json
Authorization: Bearer <your-token>

{
    "message": "عايز باراسيتامول",
    "session_id": 123  # اختياري
}
```

**Response:**
```json
{
    "message": "أهلاً! باراسيتامول متوفر عندنا 🎉 حضرتك عايز كام علبة؟",
    "session_id": 123
}
```

---

### 2. Voice (محادثة صوتية)
```http
POST /ai-agent/voice/
Content-Type: application/json
Authorization: Bearer <your-token>

{
    "audio_base64": "base64_encoded_audio_data",
    "session_id": 123  # اختياري
}
```

**Response:**
```json
{
    "text": "رد الـ AI",
    "audio_base64": "base64_encoded_audio_response",
    "session_id": 123,
    "transcription": "ما قاله المستخدم"
}
```

---

### 3. Call (مكالمة صوتية real-time)
```http
POST /ai-agent/call/
Content-Type: application/json
Authorization: Bearer <your-token>

{
    "audio_chunk_base64": "base64_encoded_audio_chunk",
    "session_id": 123
}
```

**Response:**
```json
{
    "audio_response_base64": "...",
    "text_response": "...",
    "is_final": true,
    "session_id": 123
}
```

---

### 4. Session History (سجل المحادثات)
```http
GET /ai-agent/session/123/
Authorization: Bearer <your-token>
```

**Response:**
```json
{
    "session_id": 123,
    "messages": [
        {
            "id": 1,
            "role": "user",
            "content": "عايز باراسيتامول",
            "created_at": "2025-10-15T10:30:00Z"
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "متوفر! عايز كام علبة؟",
            "created_at": "2025-10-15T10:30:05Z"
        }
    ]
}
```

---

## 🧪 اختبار الـ API

### باستخدام cURL:
```bash
curl -X POST http://129.212.140.152/ai-agent/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "عايز باراسيتامول"
  }'
```

### باستخدام Python:
```python
import requests

url = "http://129.212.140.152/ai-agent/chat/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "message": "عايز باراسيتامول"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 🔐 المصادقة (Authentication)

جميع الـ endpoints محمية بـ `IsAuthenticated` permission.

لازم تبعت JWT Token في الـ header:
```
Authorization: Bearer <your-jwt-token>
```

للحصول على Token:
```http
POST /accounts/login/
{
    "username": "your-username",
    "password": "your-password"
}
```

---

## 🛠️ الوظائف المتاحة للـ AI

الـ AI Agent يقدر ينفذ الوظائف التالية تلقائيًا:

1. ✅ **check_availability** - التحقق من توفر دواء
2. 🔄 **suggest_alternative** - اقتراح بدائل
3. 📦 **create_order** - إنشاء طلب
4. 🔍 **track_order** - تتبع طلب
5. ❌ **cancel_order** - إلغاء طلب

---

## ⚠️ ملاحظات مهمة

1. **OPENAI_API_KEY** مطلوب - بدونه الـ API مش هيشتغل
2. الـ AI بيتكلم **عامية مصرية**
3. كل Function Call بيتسجل في الداتابيز
4. الـ Sessions بتتحفظ لكل user
5. الـ AI بيستخدم GPT-4o-mini، Whisper، و TTS models

---

## 🐛 Troubleshooting

### المشكلة: 404 Not Found
- ✅ تأكد إن الـ URL مش فيه `/ /` (double slash)
- ✅ استخدم `/ai-agent/` مش `/api/ai-agent/`
- ✅ تأكد إن migrations اتعملت

### المشكلة: 401 Unauthorized
- ✅ تأكد إنك باعت JWT token صحيح
- ✅ تأكد إن التوكن مش منتهي

### المشكلة: 500 Internal Server Error
- ✅ تأكد إن `OPENAI_API_KEY` مضاف في `.env`
- ✅ شوف الـ logs: `tail -f logs/django.log`

---

## 📚 الكود المصدر

- Models: `ai_agent/models.py`
- Views: `ai_agent/views.py`
- Services: `ai_agent/services.py`
- Tools: `ai_agent/tools.py`
- Prompts: `ai_agent/prompts.py`

---

## 🚀 للمزيد من المساعدة

راجع الملفات:
- `README.md` - الوثائق الرئيسية
- `project/urls.py` - URL routing
- `ai_agent/urls.py` - AI Agent URLs

