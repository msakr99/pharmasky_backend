# 🏥 PharmasSky Backend

نظام إدارة الصيدليات والمستودعات الطبية - الخادم الخلفي

## 📋 نظرة عامة

PharmasSky Backend هو نظام شامل لإدارة الصيدليات والمستودعات الطبية مبني بـ Django و Django REST Framework.

### 🔧 التقنيات المستخدمة

- **Backend Framework:** Django 4.x + Django REST Framework
- **Database:** PostgreSQL (DigitalOcean Managed Database)
- **Cache & Message Broker:** Redis
- **File Storage:** DigitalOcean Spaces
- **Containerization:** Docker + Docker Compose
- **Web Server:** Nginx
- **Task Queue:** Celery
- **Authentication:** JWT (djangorestframework-simplejwt)

### 📱 المميزات الرئيسية

- إدارة المستخدمين والصلاحيات
- إدارة المخزون والمنتجات الطبية
- نظام الطلبات والفواتير
- إدارة العروض والخصومات
- نظام الإشعارات
- تقارير مالية ومحاسبية
- واجهة برمجة تطبيقات RESTful
- نظام مصادقة متقدم

---

## 🚀 التنصيب والنشر

### الطريقة الأولى: النشر التلقائي من GitHub (موصى بها)

```bash
# على خادم DigitalOcean
curl -o github_deploy.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/github_deploy.sh
chmod +x github_deploy.sh
./github_deploy.sh
```

### الطريقة الثانية: النشر اليدوي

```bash
# استنساخ المشروع
git clone https://github.com/msakr99/pharmasky_backend.git
cd pharmasky_backend

# إعداد البيئة
cp production.env .env.production
nano .env.production  # قم بتحرير الإعدادات

# تشغيل التطبيق
docker-compose up -d

# تشغيل المايجريشن
docker-compose exec web python manage.py migrate

# إنشاء مدير
docker-compose exec web python manage.py createsuperuser
```

للمزيد من التفاصيل، راجع: [دليل النشر من GitHub](GITHUB_DEPLOY.md)

---

## 🏗️ بنية المشروع

```
pharmasky_backend/
├── accounts/          # إدارة المستخدمين والمصادقة
├── market/           # إدارة المنتجات والسوق
├── inventory/        # إدارة المخزون
├── invoices/         # إدارة الفواتير
├── finance/          # إدارة الحسابات المالية
├── offers/           # إدارة العروض والخصومات
├── notifications/    # نظام الإشعارات
├── profiles/         # ملفات المستخدمين
├── shop/            # إدارة المتاجر
├── ads/             # إدارة الإعلانات
├── core/            # الوظائف المشتركة
├── fastapi_agent/   # خدمة الذكاء الاصطناعي (FastAPI)
├── project/         # إعدادات المشروع
├── staticfiles/     # الملفات الثابتة
├── templates/       # قوالب HTML
└── backup/          # النسخ الاحتياطية
```

---

## 🔧 الإعداد المحلي للتطوير

### المتطلبات
- Python 3.11+
- PostgreSQL
- Redis
- Docker (اختياري)

### خطوات التنصيب

```bash
# استنساخ المشروع
git clone https://github.com/msakr99/pharmasky_backend.git
cd pharmasky_backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate     # على Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py migrate

# إنشاء مدير
python manage.py createsuperuser

# تشغيل الخادم
python manage.py runserver
```

### متغيرات البيئة للتطوير

إنشئ ملف `.env` في جذر المشروع:

```env
DEBUG=True
SECRET_KEY=your-secret-key-for-development
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🤖 خدمة الذكاء الاصطناعي (FastAPI Agent)

تم استبدال `ai_agent` Django app بخدمة `fastapi_agent` منفصلة مع مميزات محسنة:

### المميزات الجديدة:
- **RAG (Retrieval Augmented Generation)** - استرجاع المعلومات الذكي
- **Ollama Integration** - استخدام نماذج محلية بدلاً من OpenAI
- **Function Calling** - تنفيذ تلقائي للوظائف
- **Microservice Architecture** - خدمة منفصلة وقابلة للتوسع

### نقاط النهاية:
- **Chat:** `POST /agent/chat` - محادثة نصية
- **Voice:** `POST /agent/voice` - معالجة صوتية
- **Call:** `POST /agent/call` - مكالمات مباشرة
- **Functions:** جميع وظائف AI Agent (9 وظائف)

للمزيد من التفاصيل، راجع: [FastAPI Agent Documentation](fastapi_agent/README.md)

## 📚 وثائق API

### نقاط النهاية الرئيسية

- **المصادقة:** `/api/auth/`
- **المستخدمين:** `/api/accounts/`
- **المنتجات:** `/api/market/`
- **المخزون:** `/api/inventory/`
- **الفواتير:** `/api/invoices/`
- **العروض:** `/api/offers/`
- **الإشعارات:** `/api/notifications/`
- **الذكاء الاصطناعي:** `http://localhost:8001/agent/`

### مثال على الاستخدام

```bash
# تسجيل الدخول
curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'

# الحصول على المنتجات
curl -X GET http://localhost:8000/api/market/products/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔒 الأمان

- مصادقة JWT متقدمة
- صلاحيات مستوى الكائن
- حماية CSRF
- تشفير كلمات المرور
- رفع الملفات الآمن
- حدود معدل الطلبات (Rate Limiting)

---

## 📊 المراقبة والصيانة

### الأوامر المفيدة

```bash
# عرض حالة الخدمات
docker-compose ps

# عرض السجلات
docker-compose logs -f web

# إعادة تشغيل الخدمات
docker-compose restart

# تنظيف النظام
docker system prune -a

# نسخ احتياطية
docker-compose exec web python manage.py dumpdata > backup.json
```

### Health Check

التطبيق يوفر endpoint للفحص الصحي:
```
GET /health/
```

---

## 🧪 الاختبارات

```bash
# تشغيل جميع الاختبارات
python manage.py test

# تشغيل اختبارات تطبيق معين
python manage.py test accounts

# تشغيل مع تغطية الكود
coverage run manage.py test
coverage report
```

---

## 🌐 النشر في الإنتاج

### المتطلبات
- Ubuntu 20.04+ أو CentOS 7+
- Docker & Docker Compose
- SSL Certificate (Let's Encrypt موصى به)
- Domain Name (اختياري)

### خطوات النشر
1. راجع [دليل النشر السريع](QUICK_DEPLOY.md)
2. راجع [دليل النشر من GitHub](GITHUB_DEPLOY.md)
3. راجع [دليل النشر المفصل](DEPLOYMENT.md)

---

## 📈 خطط التطوير المستقبلية

- [ ] دعم التطبيقات المحمولة
- [ ] نظام التقارير المتقدمة
- [ ] التكامل مع أنظمة الدفع
- [ ] نظام إدارة سلسلة التوريد
- [ ] الذكاء الاصطناعي للتوقعات
- [ ] دعم متعدد اللغات
- [ ] نظام الإشعارات المتقدم

---

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push للفرع (`git push origin feature/AmazingFeature`)
5. إنشاء Pull Request

---

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

## 📞 الاتصال والدعم

- **المطور:** Mohamed Sakr
- **GitHub:** [msakr99](https://github.com/msakr99)
- **Repository:** [pharmasky_backend](https://github.com/msakr99/pharmasky_backend)

---

## 🙏 شكر وتقدير

شكر خاص لجميع المساهمين والمكتبات المستخدمة في هذا المشروع:

- Django & Django REST Framework
- PostgreSQL
- Redis
- Docker
- DigitalOcean

---

**تم إنشاء هذا المشروع بـ ❤️ لخدمة قطاع الصيدلة والرعاية الصحية**
