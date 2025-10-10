# خطوات النشر | Deployment Steps

## المشكلة الحالية
خطأ 500 عند إغلاق فاتورة شراء على الخادم: http://129.212.140.152

## الحل

### الخطوة 1: رفع التغييرات إلى الخادم

```bash
# إذا كنت تستخدم Git
git add invoices/models.py finance/models.py invoices/serializers.py
git commit -m "Fix: Auto-create account on invoice close & Add purchase discount average"
git push origin main

# ثم على الخادم
cd /path/to/your/project
git pull origin main
```

### الخطوة 2: إعادة تشغيل خادم Django

اختر حسب إعداد الخادم:

#### إذا كنت تستخدم Gunicorn + Systemd:
```bash
sudo systemctl restart gunicorn
# أو
sudo systemctl restart your-project-name
```

#### إذا كنت تستخدم uWSGI:
```bash
sudo systemctl restart uwsgi
# أو
sudo service uwsgi restart
```

#### إذا كنت تستخدم Docker:
```bash
docker-compose down
docker-compose up -d
```

#### للتطوير المحلي:
```bash
# أوقف الخادم (Ctrl+C) ثم
python manage.py runserver
```

### الخطوة 3: التحقق من التحديث

```bash
# اختبر API
curl -X GET http://129.212.140.152/invoices/purchase-invoices/1/ \
  -H "Authorization: Token your-token"

# يجب أن ترى الحقول الجديدة:
# "total_public_price": "...",
# "average_purchase_discount_percentage": "..."
```

### الخطوة 4: إعادة محاولة إغلاق الفاتورة

```bash
curl -X PUT http://129.212.140.152/invoices/purchase-invoices/1/change-state/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_invoice_number": "4601",
    "status": "closed"
  }'
```

---

## التحقق من الأخطاء

### إذا استمر الخطأ 500

#### 1. تحقق من لوج الخادم:
```bash
# على الخادم
tail -f /var/log/gunicorn/error.log
# أو
tail -f /var/log/nginx/error.log
# أو حسب إعداد الخادم
```

#### 2. تحقق من حالة عناصر الفاتورة:
```bash
# تأكد أن جميع العناصر في حالة "received"
GET /invoices/purchase-invoice-items/?invoice=1

# إذا كانت في حالة "placed"، حدثها أولاً:
PUT /invoices/purchase-invoice-items/{item_id}/change-state/
{
  "status": "received"
}
```

#### 3. تحقق من وجود عناصر في الفاتورة:
```bash
# الفاتورة يجب أن تحتوي على عناصر
GET /invoices/purchase-invoices/1/

# تحقق من:
# - items_count > 0
# - items: [...]  (غير فارغة)
```

---

## ملفات تم تعديلها

يجب التأكد من رفع هذه الملفات:

1. ✅ `invoices/models.py` - إصلاح transaction_data
2. ✅ `finance/models.py` - إصلاح transaction_data  
3. ✅ `invoices/serializers.py` - إضافة حقول الخصم

---

## اختبار محلي أولاً

قبل النشر، اختبر محلياً:

```bash
cd E:\sky0\sky

# شغل الخادم المحلي
python manage.py runserver

# في نافذة أخرى، اختبر:
curl -X PUT http://localhost:8000/invoices/purchase-invoices/1/change-state/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_invoice_number": "4601",
    "status": "closed"
  }'
```

إذا نجح محلياً، يمكنك النشر على الخادم.

---

**آخر تحديث**: 2025-10-10

