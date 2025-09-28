#!/bin/bash

# 🚀 PharmasSky Auto Deploy Script
# Script متكامل للتحديث السريع والنشر التلقائي

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server configuration from server-config.md
DROPLET_IP="129.212.140.152"
DROPLET_USER="root"
PROJECT_PATH="/opt/pharmasky"
SSH_KEY="~/.ssh/pharmasky-github-deploy"
BRANCH="main"

echo -e "${BLUE}🚀 PharmasSky Auto Deploy${NC}"
echo -e "${BLUE}========================${NC}"
echo

# Function to print status
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "ليس في مجلد Git repository!"
    exit 1
fi

# Check SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    # Try Windows path for Git Bash
    SSH_KEY="$HOME/.ssh/pharmasky-github-deploy"
    if [ ! -f "$SSH_KEY" ]; then
        print_error "SSH key غير موجود في: $SSH_KEY"
        print_info "قم بتشغيل: ./setup_deployment.sh أولاً"
        exit 1
    fi
fi

# Test SSH connection
print_info "اختبار الاتصال بالسيرفر..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$DROPLET_USER@$DROPLET_IP" 'echo "SSH OK"' >/dev/null 2>&1; then
    print_error "فشل الاتصال بالسيرفر"
    print_info "تأكد من أن SSH key مضاف للسيرفر"
    exit 1
fi
print_success "الاتصال بالسيرفر نجح"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_info "حفظ التغييرات المحلية..."
    git add .
    
    # Get commit message from user or use default
    if [ "$1" != "" ]; then
        commit_message="$*"
    else
        commit_message="Auto deploy - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
    print_success "تم حفظ التغييرات: $commit_message"
else
    print_info "لا توجد تغييرات جديدة للحفظ"
fi

# Push to GitHub
print_info "رفع التحديثات لـ GitHub..."
if git push origin "$BRANCH"; then
    print_success "تم رفع التحديثات لـ GitHub"
else
    print_error "فشل رفع التحديثات لـ GitHub"
    exit 1
fi

# Update server
print_info "تحديث السيرفر..."
ssh -i "$SSH_KEY" "$DROPLET_USER@$DROPLET_IP" bash << EOF
set -e

cd $PROJECT_PATH

echo "🔄 سحب التحديثات..."
git stash push -m "Auto-stash before deploy $(date)"
git pull origin $BRANCH

echo "🐳 إعادة تشغيل Docker containers..."
docker-compose down
docker-compose up -d --build

echo "⏳ انتظار تشغيل الخدمات..."
sleep 15

echo "📊 حالة الـ containers:"
docker-compose ps

echo "🩺 اختبار الـ API..."
if curl -f http://localhost:8000/ >/dev/null 2>&1; then
    echo "✅ API يعمل بشكل صحيح"
else
    echo "⚠️ API قد لا يعمل بشكل صحيح"
fi

echo "✅ تم تحديث السيرفر بنجاح!"
EOF

if [ $? -eq 0 ]; then
    print_success "تم تحديث السيرفر بنجاح!"
else
    print_error "فشل في تحديث السيرفر"
    exit 1
fi

# Test external access
print_info "اختبار الوصول الخارجي..."
sleep 5
if curl -f "http://$DROPLET_IP/" >/dev/null 2>&1; then
    print_success "الموقع يعمل بشكل صحيح"
else
    print_warning "قد تكون هناك مشكلة في الوصول الخارجي"
fi

# Final status
echo
echo -e "${GREEN}🎉 تم الانتهاء من النشر بنجاح!${NC}"
echo -e "${BLUE}🔗 الموقع متاح على: http://$DROPLET_IP${NC}"
echo

# Show recent commits
print_info "آخر التحديثات:"
git log --oneline -5
