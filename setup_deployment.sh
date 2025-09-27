#!/bin/bash

# 🔧 Setup Deployment Script
# Script لإعداد التحديث التلقائي لأول مرة

echo "🔧 إعداد التحديث التلقائي..."

# Check if config exists
if [ ! -f ".deploy_config" ]; then
    echo "📝 إعداد المعلومات الأساسية..."
    
    read -p "عنوان IP الخاص بالـ Droplet: " droplet_ip
    read -p "اسم المستخدم (default: root): " droplet_user
    droplet_user=${droplet_user:-root}
    
    read -p "مسار المشروع في الـ Droplet (default: /opt/pharmasky): " project_path
    project_path=${project_path:-/opt/pharmasky}
    
    # Save configuration
    cat > .deploy_config << EOF
DROPLET_IP="$droplet_ip"
DROPLET_USER="$droplet_user"
PROJECT_PATH="$project_path"
EOF
    
    echo "✅ تم حفظ الإعدادات في .deploy_config"
else
    echo "✅ تم العثور على إعدادات محفوظة"
fi

# Load configuration
source .deploy_config

# Update the main scripts with actual values
echo "🔄 تحديث الـ scripts بالقيم الصحيحة..."

# Update update_and_deploy.sh
sed -i "s/DROPLET_IP=\"your_droplet_ip\"/DROPLET_IP=\"$DROPLET_IP\"/" update_and_deploy.sh
sed -i "s/DROPLET_USER=\"root\"/DROPLET_USER=\"$DROPLET_USER\"/" update_and_deploy.sh
sed -i "s|PROJECT_PATH=\"/opt/pharmasky\"|PROJECT_PATH=\"$PROJECT_PATH\"|" update_and_deploy.sh

# Update quick_update.sh
sed -i "s/DROPLET_IP=\"your_droplet_ip\"/DROPLET_IP=\"$DROPLET_IP\"/" quick_update.sh
sed -i "s/DROPLET_USER=\"root\"/DROPLET_USER=\"$DROPLET_USER\"/" quick_update.sh
sed -i "s|PROJECT_PATH=\"/opt/pharmasky\"|PROJECT_PATH=\"$PROJECT_PATH\"|" quick_update.sh

# Make scripts executable
chmod +x update_and_deploy.sh
chmod +x quick_update.sh

echo "✅ تم إعداد جميع الـ scripts!"

# Test SSH connection
echo "🔍 اختبار الاتصال بالـ Droplet..."
if ssh -o ConnectTimeout=10 -o BatchMode=yes $DROPLET_USER@$DROPLET_IP 'echo "SSH connection successful"' 2>/dev/null; then
    echo "✅ الاتصال SSH يعمل بشكل صحيح"
else
    echo "⚠️  مشكلة في الاتصال SSH"
    echo "تأكد من:"
    echo "1. أن الـ SSH key محمّل"
    echo "2. أن عنوان IP صحيح"
    echo "3. أن المستخدم صحيح"
fi

echo
echo "🎉 الإعداد مكتمل!"
echo "📋 الـ Scripts المتاحة:"
echo "   ./update_and_deploy.sh  - تحديث كامل مع تفاصيل"
echo "   ./quick_update.sh       - تحديث سريع"
echo
echo "💡 لاستخدام التحديث السريع:"
echo "   ./quick_update.sh"
