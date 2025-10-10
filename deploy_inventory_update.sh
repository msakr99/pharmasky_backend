#!/bin/bash
# نشر تحديث نظام المخزون
# Deploy Inventory Update

echo "=================================="
echo "  نشر تحديث نظام المخزون"
echo "=================================="

# الخطوة 1: رفع التحديثات
echo ""
echo "1️⃣ رفع التحديثات إلى Git..."
git add inventory/serializers.py
git add inventory/INVENTORY_GUIDE.md
git commit -m "feat: Add supplier info and purchase date to inventory items"
git push origin main

echo "✅ تم رفع التحديثات"

# الخطوة 2: على السيرفر
echo ""
echo "2️⃣ الآن على السيرفر..."
echo "قم بتشغيل الأوامر التالية على السيرفر:"
echo ""
echo "ssh user@129.212.140.152"
echo "cd /path/to/project"
echo "git pull origin main"
echo "sudo systemctl restart gunicorn"
echo ""

echo "=================================="
echo "✅ انتهى!"
echo "=================================="

