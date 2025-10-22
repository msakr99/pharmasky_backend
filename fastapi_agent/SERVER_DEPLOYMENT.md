# FastAPI Agent Server Deployment Guide

## 🚀 تشغيل FastAPI Agent على السيرفر

### 1. التحقق من الحالة الحالية
```bash
# التحقق من الخدمات
docker-compose ps

# التحقق من logs
docker-compose logs fastapi-agent
```

### 2. إعادة تشغيل FastAPI Agent
```bash
# إعادة بناء وتشغيل fastapi-agent
cd /opt/pharmasky/fastapi_agent
docker-compose down fastapi-agent
docker-compose build fastapi-agent
docker-compose up -d fastapi-agent

# أو إعادة تشغيل كامل
docker-compose restart fastapi-agent
```

### 3. التحقق من التشغيل
```bash
# التحقق من أن الخدمة تعمل
curl http://localhost:8001/

# التحقق من API docs
curl http://localhost:8001/docs
```

### 4. اختبار الـ Endpoints
```bash
# اختبار Chat
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "عايز باراسيتامول", "context": {"user_id": 5}}'

# اختبار Check Availability
curl -X POST http://localhost:8001/agent/check-availability \
  -H "Content-Type: application/json" \
  -d '{"medicine_name": "باراسيتامول", "user_id": 5}'

# اختبار Suggest Alternative
curl -X POST http://localhost:8001/agent/suggest-alternative \
  -H "Content-Type: application/json" \
  -d '{"medicine_name": "باراسيتامول"}'
```

### 5. إصلاح المشاكل الشائعة

#### مشكلة: Port 8001 غير متاح
```bash
# التحقق من المنافذ المستخدمة
netstat -tlnp | grep 8001

# إيقاف الخدمة التي تستخدم المنفذ
sudo kill -9 <PID>
```

#### مشكلة: FastAPI Agent لا يبدأ
```bash
# التحقق من logs
docker-compose logs fastapi-agent

# إعادة بناء الصورة
docker-compose build --no-cache fastapi_agent
```

#### مشكلة: Database connection
```bash
# التحقق من قاعدة البيانات
docker-compose logs fastapi_db

# إعادة تشغيل قاعدة البيانات
docker-compose restart fastapi_db
```

### 6. إعداد Environment Variables
```bash
# إنشاء ملف .env
cd /opt/pharmasky/fastapi_agent
cp config.env.example .env

# تحديث الإعدادات
nano .env
```

### 7. Monitoring والـ Logs
```bash
# مراقبة logs في الوقت الفعلي
docker-compose logs -f fastapi_agent

# مراقبة استخدام الموارد
docker stats fastapi_agent
```

### 8. Health Check
```bash
# التحقق من صحة الخدمة
curl http://localhost:8001/health

# التحقق من جميع الخدمات
curl http://localhost:8001/health/detailed
```

## 🔧 Troubleshooting

### مشكلة: "Connection refused"
```bash
# التحقق من أن الخدمة تعمل
docker-compose ps fastapi-agent

# إعادة تشغيل الخدمة
docker-compose restart fastapi-agent
```

### مشكلة: "Module not found"
```bash
# إعادة بناء الصورة
docker-compose build --no-cache fastapi_agent
```

### مشكلة: "Database connection failed"
```bash
# التحقق من قاعدة البيانات
docker-compose logs fastapi_db

# إعادة تشغيل قاعدة البيانات
docker-compose restart fastapi_db fastapi_agent
```

## 📊 Monitoring Commands

```bash
# مراقبة الأداء
docker stats

# مراقبة logs
docker-compose logs -f

# التحقق من المساحة
df -h

# التحقق من الذاكرة
free -h
```

## 🚀 Quick Start Commands

```bash
# تشغيل سريع
cd /opt/pharmasky/fastapi_agent
docker-compose up -d fastapi_agent

# التحقق من التشغيل
curl http://localhost:8001/

# اختبار API
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "مرحبا", "context": {"user_id": 1}}'
```

## 📝 Notes

- FastAPI Agent يعمل على المنفذ 8001
- يحتاج إلى قاعدة بيانات PostgreSQL
- يحتاج إلى Redis للـ caching
- يحتاج إلى Ollama للـ LLM
- جميع الـ endpoints متوفرة على `/agent/*`
