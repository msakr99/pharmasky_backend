#!/bin/bash

# 🔧 Setup Deployment Script
# Script لإعداد التحديث التلقائي لأول مرة

echo "🔧 إعداد التحديث التلقائي..."

# Use server configuration from server-config.md
DROPLET_IP="129.212.140.152"
DROPLET_USER="root"
PROJECT_PATH="/opt/pharmasky"
SSH_KEY="~/.ssh/pharmasky-github-deploy"

echo "✅ استخدام المعلومات من server-config.md:"
echo "   IP: $DROPLET_IP"
echo "   User: $DROPLET_USER" 
echo "   Path: $PROJECT_PATH"
echo "   SSH Key: $SSH_KEY"

# Scripts are already updated with correct values
echo "✅ الـ scripts محدثة بالفعل بالقيم الصحيحة"

# Make scripts executable
chmod +x update_and_deploy.sh
chmod +x quick_update.sh

echo "✅ تم إعداد جميع الـ scripts!"

# Test SSH connection
echo "🔍 اختبار الاتصال بالـ Droplet..."
if ssh -i $SSH_KEY -o ConnectTimeout=10 -o BatchMode=yes $DROPLET_USER@$DROPLET_IP 'echo "SSH connection successful"' 2>/dev/null; then
    echo "✅ الاتصال SSH يعمل بشكل صحيح"
else
    echo "⚠️  مشكلة في الاتصال SSH"
    echo "تأكد من:"
    echo "1. أن الـ SSH key موجود في: $SSH_KEY"
    echo "2. أن صلاحيات المفتاح صحيحة: chmod 600 $SSH_KEY"
    echo "3. أن المفتاح العام مضاف للـ server"
    echo "4. تشغيل: ssh-add $SSH_KEY"
fi

echo
echo "🎉 الإعداد مكتمل!"
echo "📋 الـ Scripts المتاحة:"
echo "   ./update_and_deploy.sh  - تحديث كامل مع تفاصيل"
echo "   ./quick_update.sh       - تحديث سريع"
echo
echo "💡 لاستخدام التحديث السريع:"
echo "   ./quick_update.sh"
