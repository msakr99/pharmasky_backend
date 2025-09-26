#!/bin/bash

# Complete PharmasSky Setup Script for New Droplet
# يقوم هذا السكريبت بإعداد كامل للمشروع على الدروبليت الجديدة

echo "🚀 بدء إعداد PharmasSky على الدروبليت الجديدة..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Setup SSH Key
setup_ssh_key() {
    print_status "إعداد SSH key..."
    
    mkdir -p ~/.ssh
    echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQH0MsW1lzkRkpbOspKXb1dlpA1hHD8AONnpDGSFtld pharmasky-github-deploy" >> ~/.ssh/authorized_keys
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    
    print_success "تم إعداد SSH key بنجاح"
}

# Step 2: Install requirements
install_requirements() {
    print_status "تثبيت المتطلبات الأساسية..."
    
    # Update system
    apt update && apt upgrade -y
    
    # Install basic packages
    apt install -y git curl wget htop nano ufw
    
    # Install Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_status "تثبيت Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_status "تثبيت Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    print_success "تم تثبيت المتطلبات بنجاح"
}

# Step 3: Setup firewall
setup_firewall() {
    print_status "إعداد Firewall..."
    
    ufw --force enable
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    
    print_success "تم إعداد Firewall بنجاح"
}

# Step 4: Clone project
clone_project() {
    print_status "استنساخ المشروع من GitHub..."
    
    # Create project directory
    mkdir -p /opt/pharmasky
    cd /opt/pharmasky
    
    # Clone repository
    if [ -d ".git" ]; then
        print_status "تحديث المشروع الموجود..."
        git fetch origin
        git reset --hard origin/main
    else
        print_status "استنساخ المشروع..."
        git clone https://github.com/msakr99/pharmasky_backend.git .
    fi
    
    # Set permissions
    chmod +x *.sh
    
    print_success "تم استنساخ المشروع بنجاح"
}

# Step 5: Setup environment
setup_environment() {
    print_status "إعداد ملف البيئة..."
    
    cd /opt/pharmasky
    
    if [ ! -f ".env.production" ]; then
        cp production.env .env.production
        print_warning "تم إنشاء .env.production - قم بتحديث الإعدادات حسب الحاجة"
    fi
    
    print_success "تم إعداد البيئة بنجاح"
}

# Step 6: Deploy application
deploy_application() {
    print_status "تشغيل التطبيق..."
    
    cd /opt/pharmasky
    
    # Build and start containers
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for containers to be ready
    print_status "انتظار تشغيل الخدمات..."
    sleep 30
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "فشل في تشغيل الحاويات!"
        docker-compose logs
        return 1
    fi
    
    print_success "تم تشغيل الحاويات بنجاح"
}

# Step 7: Setup database
setup_database() {
    print_status "إعداد قاعدة البيانات..."
    
    cd /opt/pharmasky
    
    # Run migrations
    docker-compose exec -T web python manage.py migrate
    
    # Collect static files
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_success "تم إعداد قاعدة البيانات بنجاح"
}

# Step 8: Health check
health_check() {
    print_status "فحص صحة التطبيق..."
    
    cd /opt/pharmasky
    
    # Check container status
    docker-compose ps
    
    # Test health endpoint
    sleep 10
    if curl -f -s http://localhost/health/ >/dev/null; then
        print_success "✅ التطبيق يعمل بشكل طبيعي!"
    else
        print_warning "⚠️ فحص الصحة فشل - قد يحتاج وقت إضافي للتشغيل"
    fi
}

# Main execution
main() {
    print_status "🚀 بدء الإعداد الكامل لـ PharmasSky..."
    echo ""
    
    setup_ssh_key
    echo ""
    
    install_requirements  
    echo ""
    
    setup_firewall
    echo ""
    
    clone_project
    echo ""
    
    setup_environment
    echo ""
    
    deploy_application
    echo ""
    
    setup_database
    echo ""
    
    health_check
    echo ""
    
    print_success "🎉 تم إكمال الإعداد بنجاح!"
    echo ""
    print_status "🔗 عناوين التطبيق:"
    print_status "   • التطبيق الرئيسي: http://$(curl -s ifconfig.me 2>/dev/null || echo '129.212.140.152')"
    print_status "   • لوحة الإدارة: http://$(curl -s ifconfig.me 2>/dev/null || echo '129.212.140.152')/admin/"
    print_status "   • فحص الصحة: http://$(curl -s ifconfig.me 2>/dev/null || echo '129.212.140.152')/health/"
    echo ""
    print_status "📝 الخطوات التالية:"
    print_status "   1. إنشاء مدير: docker-compose exec web python manage.py createsuperuser"
    print_status "   2. إعداد GitHub Secrets للنشر التلقائي"
    print_status "   3. اختبار التطبيق في المتصفح"
    echo ""
    print_status "🛠️ أوامر مفيدة:"
    print_status "   • عرض السجلات: docker-compose logs -f"
    print_status "   • إعادة التشغيل: docker-compose restart"
    print_status "   • فحص الحالة: ./quick_commands.sh status"
}

# Run main function
main
