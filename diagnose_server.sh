#!/bin/bash
# سكريبت تشخيص السيرفر وفحص الإشعارات

echo "════════════════════════════════════════════════════════════════"
echo "🔍 فحص حالة السيرفر - PharmaSky"
echo "════════════════════════════════════════════════════════════════"
echo ""

# الألوان
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. فحص Docker containers
echo -e "${YELLOW}📦 1. فحص Docker Containers:${NC}"
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
else
    echo "Docker غير متوفر"
fi

# 2. فحص الـ ports
echo -e "${YELLOW}🔌 2. فحص Ports:${NC}"
netstat -tulpn | grep -E ':(80|8000|5432|6379)' || echo "لم يتم العثور على ports مفتوحة"
echo ""

# 3. فحص Nginx
echo -e "${YELLOW}🌐 3. فحص Nginx:${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx يعمل${NC}"
else
    echo -e "${RED}❌ Nginx لا يعمل${NC}"
fi
echo ""

# 4. اختبار الاتصال
echo -e "${YELLOW}🔗 4. اختبار الاتصال:${NC}"
echo "محاولة الاتصال بـ localhost..."
curl -I http://localhost 2>&1 | head -n 5
echo ""

echo "محاولة الاتصال بـ 167.71.40.9..."
curl -I http://167.71.40.9 2>&1 | head -n 5
echo ""

# 5. فحص المسار
echo -e "${YELLOW}📁 5. فحص المسار:${NC}"
pwd
ls -la | head -n 10
echo ""

# 6. فحص manage.py
echo -e "${YELLOW}🐍 6. فحص Django:${NC}"
if [ -f "manage.py" ]; then
    echo -e "${GREEN}✅ manage.py موجود${NC}"
    
    # التحقق من البيئة الافتراضية
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ venv موجود${NC}"
    elif [ -d "env" ]; then
        echo -e "${GREEN}✅ env موجود${NC}"
    else
        echo -e "${YELLOW}⚠️  البيئة الافتراضية غير موجودة في المسار الحالي${NC}"
    fi
else
    echo -e "${RED}❌ manage.py غير موجود في المسار الحالي${NC}"
fi
echo ""

# 7. فحص logs (Docker)
echo -e "${YELLOW}📋 7. آخر 10 أسطر من logs (إن وجدت):${NC}"
if docker ps --format '{{.Names}}' | grep -q 'web\|django\|pharmasky'; then
    CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep -E 'web|django|pharmasky' | head -n 1)
    echo "Container: $CONTAINER_NAME"
    docker logs --tail 10 "$CONTAINER_NAME" 2>&1 || echo "لا يمكن قراءة logs"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ انتهى الفحص${NC}"
echo "════════════════════════════════════════════════════════════════"

