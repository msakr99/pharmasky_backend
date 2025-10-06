#!/bin/bash
# Script to verify all changes are in place

echo "======================================================================"
echo "التحقق من تطبيق تعديلات البحث"
echo "======================================================================"

echo ""
echo "1. التحقق من offers/views.py..."
echo "   البحث عن filter_backends في MaxOfferListAPIView:"
grep -A 1 "class MaxOfferListAPIView" offers/views.py | head -n 10 | grep "filter_backends"
if [ $? -eq 0 ]; then
    echo "   ✅ filter_backends موجود"
else
    echo "   ❌ filter_backends غير موجود"
fi

echo ""
echo "   البحث عن search_fields بدون ^:"
grep "search_fields.*product__name" offers/views.py | grep -v "\^"
if [ $? -eq 0 ]; then
    echo "   ✅ search_fields بدون ^ موجود"
else
    echo "   ❌ search_fields لا يزال يحتوي على ^"
fi

echo ""
echo "2. التحقق من project/settings.py..."
grep -A 2 "DEFAULT_FILTER_BACKENDS" project/settings.py | grep "rest_framework.filters.SearchFilter"
if [ $? -eq 0 ]; then
    echo "   ✅ SearchFilter موجود في settings.py"
else
    echo "   ❌ CustomSearchFilter لا يزال موجود في settings.py"
fi

echo ""
echo "3. التحقق من project/settings/base.py..."
grep -A 2 "DEFAULT_FILTER_BACKENDS" project/settings/base.py | grep "rest_framework.filters.SearchFilter"
if [ $? -eq 0 ]; then
    echo "   ✅ SearchFilter موجود في settings/base.py"
else
    echo "   ❌ CustomSearchFilter لا يزال موجود في settings/base.py"
fi

echo ""
echo "======================================================================"
echo "الخطوة التالية:"
echo "======================================================================"
echo ""
echo "إذا كانت كل الفحوصات ✅، فالكود صحيح!"
echo ""
echo "الآن يجب عليك:"
echo "1. أعد تشغيل السيرفر:"
echo "   sudo systemctl restart pharmasky"
echo ""
echo "2. اختبر البحث:"
echo "   curl -H \"Authorization: Token YOUR_TOKEN\" \\"
echo "        \"http://129.212.140.152/offers/max-offers/?search=TEXT\""
echo ""
echo "======================================================================"

