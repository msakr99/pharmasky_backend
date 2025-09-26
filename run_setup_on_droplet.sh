#!/bin/bash

echo "🚀 PharmasSky - إعداد SSH Key على الدروبليت"
echo ""

echo "📡 الاتصال بالدروبليت وتشغيل إعداد SSH key..."
echo ""

# الاتصال بالدروبليت وتشغيل الأوامر
ssh root@129.212.140.152 "curl -o setup_ssh_key.sh https://raw.githubusercontent.com/msakr99/pharmasky_backend/main/setup_ssh_key.sh && chmod +x setup_ssh_key.sh && ./setup_ssh_key.sh"

echo ""
echo "✅ تم إعداد SSH key بنجاح!"
echo ""
echo "📋 الخطوات التالية:"
echo "1. اذهب إلى GitHub Repository Settings"
echo "2. أضف Secrets كما هو مذكور في ملف SETUP_GITHUB_SECRETS.md"
echo "3. قم بعمل push لاختبار النشر التلقائي"
echo ""
echo "🔗 رابط GitHub Repository:"
echo "https://github.com/msakr99/pharmasky_backend/settings/secrets/actions"
echo ""

read -p "اضغط Enter للمتابعة..."
