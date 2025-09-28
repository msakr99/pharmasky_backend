#!/bin/bash

# 🚀 Quick Update Script - تحديث سريع
# استخدم هذا الـ script للتحديث السريع بدون تفاصيل كثيرة

# Configuration - معلومات السيرفر من server-config.md
DROPLET_IP="129.212.140.152"
DROPLET_USER="root"
PROJECT_PATH="/opt/pharmasky"
SSH_KEY="~/.ssh/pharmasky-github-deploy"

echo "🚀 Quick Update Starting..."

# Add, commit and push
git add .
git commit -m "Auto update - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# Update droplet
echo "📡 Updating droplet..."
ssh -i $SSH_KEY $DROPLET_USER@$DROPLET_IP "cd $PROJECT_PATH && git stash && git pull origin main && docker-compose down && docker-compose up --build -d"

echo "✅ Done! Check your app at: http://$DROPLET_IP"
