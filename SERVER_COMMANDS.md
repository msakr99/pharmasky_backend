# أوامر السيرفر - للنشر الفوري
# Server Commands - For Immediate Deployment

## 🚀 الأوامر المطلوبة على السيرفر

### الخطوة 1: الاتصال بالسيرفر

```bash
ssh user@129.212.140.152
```

---

### الخطوة 2: الانتقال لمجلد المشروع

```bash
cd /home/pharmasky/pharmasky_backend
# أو
cd /var/www/pharmasky
# أو حسب مكان المشروع عندك
```

---

### الخطوة 3: سحب التحديثات

```bash
git pull origin main
```

**المتوقع:**
```
Updating ee569b4..b63a131
Fast-forward
 finance/models.py                     | 62 ++++++++++++
 finance/serializers.py                | 25 +++++
 finance/views.py                      | 48 ++++++++++
 ...
 17 files changed, 3419 insertions(+)
```

---

### ⚠️ الخطوة 4: تشغيل Migration (مهم جداً!)

```bash
python manage.py migrate
```

**المتوقع:**
```
Running migrations:
  Applying finance.0004_expense... OK
```

---

### الخطوة 5: إعادة تشغيل Django

اختر حسب إعدادك:

#### إذا تستخدم Gunicorn:
```bash
sudo systemctl restart gunicorn
```

#### إذا تستخدم uWSGI:
```bash
sudo systemctl restart uwsgi
```

#### إذا تستخدم Supervisor:
```bash
sudo supervisorctl restart pharmasky
```

#### إذا تستخدم Docker:
```bash
docker-compose restart
```

---

### الخطوة 6: التحقق من النجاح

```bash
# فحص حالة الخدمة
sudo systemctl status gunicorn

# فحص السجلات
tail -f /var/log/gunicorn/error.log
```

---

## ✅ اختبار التحديثات

### 1. اختبر نظام المصاريف

```bash
curl -X POST http://129.212.140.152/finance/expenses/create/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "monthly",
    "category": "salary",
    "amount": 5000,
    "recipient": "test",
    "payment_method": "cash",
    "expense_date": "2025-10-10"
  }'
```

**المتوقع:** نجاح 201 Created

---

### 2. اختبر رأس المال

```bash
curl -X GET http://129.212.140.152/finance/safe/ \
  -H "Authorization: Token your-token"
```

**المتوقع:** ترى `expenses_total_amount` في الاستجابة

---

### 3. اختبر معلومات المورد في المخزون

```bash
curl -X GET http://129.212.140.152/inventory/inventory-items/ \
  -H "Authorization: Token your-token"
```

**المتوقع:** ترى `supplier_name`, `supplier_invoice_number`, `purchase_date`

---

## 🎯 ملخص الأوامر (نسخ ولصق)

```bash
# على السيرفر
cd /home/pharmasky/pharmasky_backend
git pull origin main
python manage.py migrate
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

---

## ⚠️ إذا حدث خطأ

### خطأ: Migration فشل

```bash
# جرب:
python manage.py migrate --fake finance 0004
python manage.py migrate
```

### خطأ: الخدمة لم تبدأ

```bash
# فحص السجلات
tail -f /var/log/gunicorn/error.log

# أو
journalctl -u gunicorn -f
```

---

## 📞 للمساعدة

إذا واجهت مشكلة، شارك:
1. رسالة الخطأ من السجلات
2. نتيجة `git pull`
3. نتيجة `python manage.py migrate`

---

**جاهز للتنفيذ!** 🚀

