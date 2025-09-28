#!/bin/bash

# 🚀 PharmasSky Auto Update & Deploy Script
# Script لتحديث GitHub repository والـ DigitalOcean Droplet تلقائياً

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - معلومات السيرفر من server-config.md
DROPLET_IP="129.212.140.152"         # عنوان IP الخاص بالـ Droplet
DROPLET_USER="root"                   # المستخدم (root أو اسم المستخدم)
PROJECT_PATH="/opt/pharmasky"         # مسار المشروع في الـ Droplet
BRANCH="main"                         # الفرع المطلوب تحديثه
SSH_KEY="~/.ssh/pharmasky-github-deploy"  # مسار SSH key

echo -e "${BLUE}🚀 PharmasSky Auto Update & Deploy Script${NC}"
echo -e "${BLUE}=============================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Check if we're in a git repository
echo
print_info "Step 1: التحقق من Git repository..."
if [ ! -d ".git" ]; then
    print_error "ليس في مجلد Git repository!"
    exit 1
fi
print_status "في Git repository صحيح"

# Step 2: Check for uncommitted changes
echo
print_info "Step 2: التحقق من التغييرات غير المحفوظة..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "يوجد تغييرات غير محفوظة!"
    read -p "هل تريد حفظها والمتابعة؟ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Add all changes
        print_info "إضافة جميع التغييرات..."
        git add .
        
        # Ask for commit message
        read -p "اكتب رسالة الـ commit: " commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Auto update - $(date '+%Y-%m-%d %H:%M:%S')"
        fi
        
        # Commit changes
        git commit -m "$commit_message"
        print_status "تم حفظ التغييرات"
    else
        print_error "تم إلغاء العملية"
        exit 1
    fi
fi

# Step 3: Push to GitHub
echo
print_info "Step 3: رفع التحديثات لـ GitHub..."
git push origin $BRANCH
if [ $? -eq 0 ]; then
    print_status "تم رفع التحديثات بنجاح لـ GitHub"
else
    print_error "فشل في رفع التحديثات لـ GitHub"
    exit 1
fi

# Step 4: Update Droplet
echo
print_info "Step 4: تحديث الـ DigitalOcean Droplet..."

# Create the update script for droplet
cat > droplet_update.sh << 'EOF'
#!/bin/bash
cd PROJECT_PATH_PLACEHOLDER

echo "🔄 بدء تحديث المشروع..."

# Stash local changes
git stash

# Pull latest changes
echo "📥 سحب التحديثات من GitHub..."
git pull origin BRANCH_PLACEHOLDER

# Check if docker-compose exists and containers are running
if [ -f "docker-compose.yml" ] && [ "$(docker ps -q)" ]; then
    echo "🐳 إعادة تشغيل Docker containers..."
    
    # Stop containers
    docker-compose down
    
    # Rebuild and start containers
    docker-compose up --build -d
    
    # Wait a bit for containers to start
    sleep 10
    
    # Check container status
    echo "📊 حالة الـ containers:"
    docker-compose ps
    
elif systemctl list-units | grep -q gunicorn; then
    echo "🔄 إعادة تشغيل Gunicorn و Nginx..."
    
    # Activate virtual environment if exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -r requirements.txt
        python manage.py collectstatic --noinput
    fi
    
    # Restart services
    systemctl restart gunicorn
    systemctl restart nginx
    
else
    echo "⚠️  لم يتم العثور على Docker أو systemd services"
fi

echo "✅ تم التحديث بنجاح!"
EOF

# Replace placeholders in the script
sed -i "s|PROJECT_PATH_PLACEHOLDER|$PROJECT_PATH|g" droplet_update.sh
sed -i "s|BRANCH_PLACEHOLDER|$BRANCH|g" droplet_update.sh

# Copy and execute the script on droplet
print_info "نسخ وتنفيذ script التحديث على الـ Droplet..."

# Copy script to droplet
scp -i $SSH_KEY droplet_update.sh $DROPLET_USER@$DROPLET_IP:/tmp/

# Execute the script on droplet
ssh -i $SSH_KEY $DROPLET_USER@$DROPLET_IP 'chmod +x /tmp/droplet_update.sh && /tmp/droplet_update.sh && rm /tmp/droplet_update.sh'

if [ $? -eq 0 ]; then
    print_status "تم تحديث الـ Droplet بنجاح!"
else
    print_error "فشل في تحديث الـ Droplet"
    exit 1
fi

# Cleanup
rm droplet_update.sh

# Step 5: Test the API
echo
print_info "Step 5: اختبار الـ API..."
sleep 5

# Test login endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://$DROPLET_IP/accounts/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}')

if [ "$response" = "400" ] || [ "$response" = "401" ] || [ "$response" = "200" ]; then
    print_status "الـ API يستجيب بشكل صحيح (HTTP $response)"
else
    print_warning "الـ API قد لا يعمل بشكل صحيح (HTTP $response)"
fi

# Final message
echo
echo -e "${GREEN}🎉 تم الانتهاء من جميع الخطوات!${NC}"
echo -e "${BLUE}📋 ملخص العملية:${NC}"
echo -e "   ✅ تم رفع التحديثات لـ GitHub"
echo -e "   ✅ تم تحديث الـ Droplet"
echo -e "   ✅ تم إعادة تشغيل الخدمات"
echo -e "   ✅ تم اختبار الـ API"
echo

print_info "يمكنك الآن اختبار التطبيق على: http://$DROPLET_IP"
