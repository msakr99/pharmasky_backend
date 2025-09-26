#!/bin/bash

# PharmasSky Quick Commands Script
# مجموعة من الأوامر السريعة لإدارة التطبيق

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

# Function to show help
show_help() {
    echo "🚀 PharmasSky Quick Commands"
    echo ""
    echo "الاستخدام: ./quick_commands.sh [command]"
    echo ""
    echo "الأوامر المتاحة:"
    echo "  deploy       - نشر التطبيق من GitHub"
    echo "  update       - تحديث التطبيق من GitHub"
    echo "  restart      - إعادة تشغيل جميع الخدمات"
    echo "  logs         - عرض سجلات التطبيق"
    echo "  status       - عرض حالة الخدمات"
    echo "  backup       - إنشاء نسخة احتياطية"
    echo "  migrate      - تشغيل database migrations"
    echo "  shell        - فتح Django shell"
    echo "  superuser    - إنشاء مدير جديد"
    echo "  collectstatic- جمع الملفات الثابتة"
    echo "  cleanup      - تنظيف النظام"
    echo "  health       - فحص صحة التطبيق"
    echo "  help         - عرض هذه المساعدة"
    echo ""
}

# Deploy from GitHub
deploy() {
    print_status "نشر التطبيق من GitHub..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    # Pull latest changes
    git fetch origin
    git reset --hard origin/main
    
    # Build and start containers
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services
    sleep 30
    
    # Run migrations and collect static
    docker-compose exec -T web python manage.py migrate
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_success "تم النشر بنجاح!"
}

# Update application
update() {
    print_status "تحديث التطبيق..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    git pull origin main
    docker-compose up --build -d
    
    sleep 15
    
    docker-compose exec -T web python manage.py migrate
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_success "تم التحديث بنجاح!"
}

# Restart services
restart() {
    print_status "إعادة تشغيل الخدمات..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose restart
    
    print_success "تم إعادة تشغيل الخدمات!"
}

# Show logs
show_logs() {
    print_status "عرض سجلات التطبيق..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose logs -f --tail=100 web
}

# Show status
show_status() {
    print_status "حالة الخدمات:"
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose ps
    echo ""
    
    print_status "استخدام الموارد:"
    docker stats --no-stream
}

# Create backup
create_backup() {
    print_status "إنشاء نسخة احتياطية..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    backup_dir="/opt/backups"
    mkdir -p $backup_dir
    
    backup_file="$backup_dir/backup_$(date +%Y%m%d_%H%M%S).json"
    
    docker-compose exec -T web python manage.py dumpdata > $backup_file
    
    print_success "تم إنشاء النسخة الاحتياطية: $backup_file"
}

# Run migrations
run_migrations() {
    print_status "تشغيل database migrations..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose exec -T web python manage.py makemigrations
    docker-compose exec -T web python manage.py migrate
    
    print_success "تم تشغيل migrations بنجاح!"
}

# Open Django shell
open_shell() {
    print_status "فتح Django shell..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose exec web python manage.py shell
}

# Create superuser
create_superuser() {
    print_status "إنشاء مدير جديد..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose exec web python manage.py createsuperuser
}

# Collect static files
collect_static() {
    print_status "جمع الملفات الثابتة..."
    
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    print_success "تم جمع الملفات الثابتة!"
}

# Cleanup system
cleanup() {
    print_status "تنظيف النظام..."
    
    docker system prune -a -f
    docker volume prune -f
    
    print_success "تم تنظيف النظام!"
}

# Health check
health_check() {
    print_status "فحص صحة التطبيق..."
    
    # Check if containers are running
    cd /opt/pharmasky || { print_error "مجلد المشروع غير موجود"; exit 1; }
    
    if ! docker-compose ps | grep -q "Up"; then
        print_error "بعض الخدمات لا تعمل!"
        docker-compose ps
        exit 1
    fi
    
    # Check HTTP response
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        print_success "التطبيق يعمل بشكل طبيعي ✅"
    else
        print_error "فشل في فحص صحة التطبيق - HTTP Status: $response"
        exit 1
    fi
    
    print_status "معلومات إضافية:"
    echo "- عنوان التطبيق: http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost')"
    echo "- لوحة الإدارة: http://$(curl -s ifconfig.me 2>/dev/null || echo 'localhost')/admin/"
}

# Main script logic
case "$1" in
    deploy)
        deploy
        ;;
    update)
        update
        ;;
    restart)
        restart
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    backup)
        create_backup
        ;;
    migrate)
        run_migrations
        ;;
    shell)
        open_shell
        ;;
    superuser)
        create_superuser
        ;;
    collectstatic)
        collect_static
        ;;
    cleanup)
        cleanup
        ;;
    health)
        health_check
        ;;
    help|*)
        show_help
        ;;
esac
