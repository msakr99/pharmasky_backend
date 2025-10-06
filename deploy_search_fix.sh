#!/bin/bash
# Script to deploy search fix to production server

echo "======================================================================"
echo "تحديث ونشر إصلاح البحث إلى السيرفر"
echo "======================================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}الخطوة 1: التحقق من التعديلات المحلية${NC}"
echo "----------------------------------------------------------------------"

# Check if search_term is in the file
if grep -q "search_term = self.request.query_params.get('search'" offers/views.py; then
    echo -e "${GREEN}✓${NC} التعديلات موجودة في الكود المحلي"
else
    echo -e "${RED}✗${NC} التعديلات غير موجودة في الكود المحلي!"
    exit 1
fi

# Check if manual search filter is in the file
if grep -q "if search_term:" offers/views.py; then
    echo -e "${GREEN}✓${NC} البحث اليدوي موجود"
else
    echo -e "${RED}✗${NC} البحث اليدوي غير موجود!"
    exit 1
fi

echo ""
echo -e "${YELLOW}الخطوة 2: عمل commit و push للتعديلات${NC}"
echo "----------------------------------------------------------------------"

# Add changes
git add offers/views.py project/settings.py project/settings/base.py

# Commit
git commit -m "Fix: Implement manual search filter in MaxOfferListAPIView

- Added manual search filtering in get_queryset()
- Removed SearchFilter from filter_backends (conflicted with custom queryset)
- Added logging for debugging
- Search now properly filters by product name (Arabic and English)
" || echo "لا توجد تغييرات للـ commit أو تم الـ commit مسبقاً"

# Push
echo ""
echo "هل تريد عمل push للتعديلات؟ (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    git push origin main || git push origin master || echo "فشل الـ push - تحقق من الـ branch"
    echo -e "${GREEN}✓${NC} تم الـ push"
else
    echo -e "${YELLOW}!${NC} تخطي الـ push - ستحتاج لعمله يدوياً"
fi

echo ""
echo -e "${YELLOW}الخطوة 3: تعليمات النشر على السيرفر${NC}"
echo "======================================================================"
echo ""
echo "الآن يجب تنفيذ الأوامر التالية على السيرفر:"
echo ""
echo -e "${GREEN}# 1. SSH إلى السيرفر${NC}"
echo "   ssh user@129.212.140.152"
echo ""
echo -e "${GREEN}# 2. اذهب إلى مجلد المشروع${NC}"
echo "   cd /path/to/pharmasky"
echo ""
echo -e "${GREEN}# 3. اسحب آخر التعديلات${NC}"
echo "   git pull origin main"
echo ""
echo -e "${GREEN}# 4. أعد بناء وتشغيل Docker container${NC}"
echo "   docker-compose down"
echo "   docker-compose up -d --build"
echo ""
echo -e "${GREEN}# 5. تحقق من الـ logs${NC}"
echo "   docker-compose logs -f pharmasky_web | grep MaxOfferListAPIView"
echo ""
echo -e "${GREEN}# 6. اختبر البحث${NC}"
echo "   curl -H 'Authorization: Token YOUR_TOKEN' \\"
echo "        'http://localhost:8000/offers/max-offers/?search=test'"
echo ""
echo "======================================================================"
echo ""
echo -e "${YELLOW}أو إذا كان السيرفر يستخدم supervisor/systemd:${NC}"
echo ""
echo "   cd /path/to/pharmasky"
echo "   git pull"
echo "   sudo systemctl restart pharmasky"
echo "   # أو"
echo "   sudo supervisorctl restart pharmasky"
echo ""
echo "======================================================================"
echo ""
echo -e "${GREEN}انتهى!${NC} بعد تنفيذ الأوامر على السيرفر، اختبر البحث."
echo ""

