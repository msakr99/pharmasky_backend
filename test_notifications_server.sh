#!/bin/bash
# سكريبت اختبار الإشعارات على السيرفر
# الاستخدام: bash test_notifications_server.sh

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🔔 اختبار نظام الإشعارات - PharmaSky Server"
echo "════════════════════════════════════════════════════════════════"
echo ""

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL للـ API
BASE_URL="http://167.71.40.9"

echo -e "${BLUE}📋 معلومات السيرفر:${NC}"
echo "   URL: $BASE_URL"
echo ""

# التحقق من تشغيل السيرفر
echo -e "${YELLOW}🔍 التحقق من حالة السيرفر...${NC}"
if curl -s --head "$BASE_URL/admin/" | head -n 1 | grep "HTTP" > /dev/null; then
    echo -e "${GREEN}✅ السيرفر يعمل بنجاح${NC}"
else
    echo -e "${RED}❌ السيرفر لا يستجيب${NC}"
    exit 1
fi
echo ""

# طلب بيانات المصادقة
echo -e "${BLUE}🔐 المصادقة:${NC}"
read -p "Username (رقم الهاتف مع +2): " USERNAME
read -sp "Password: " PASSWORD
echo ""
echo ""

# تسجيل الدخول
echo -e "${YELLOW}🔑 جاري تسجيل الدخول...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/accounts/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

# التحقق من نجاح تسجيل الدخول
if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    USER_NAME=$(echo "$LOGIN_RESPONSE" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ تم تسجيل الدخول بنجاح${NC}"
    echo -e "   👤 المستخدم: $USER_NAME"
    echo -e "   🔑 Token: ${TOKEN:0:30}..."
else
    echo -e "${RED}❌ فشل تسجيل الدخول${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi
echo ""

# جلب الإحصائيات
echo "════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📊 اختبار 1: جلب الإحصائيات${NC}"
echo "────────────────────────────────────────────────────────────────"
STATS_RESPONSE=$(curl -s "$BASE_URL/api/v1/notifications/notifications/stats/" \
    -H "Authorization: Token $TOKEN")

if echo "$STATS_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ نجح الاختبار${NC}"
    echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"
else
    echo -e "${RED}❌ فشل الاختبار${NC}"
    echo "$STATS_RESPONSE"
fi
echo ""

# جلب الإشعارات
echo "════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📬 اختبار 2: جلب جميع الإشعارات (أول 5)${NC}"
echo "────────────────────────────────────────────────────────────────"
NOTIFS_RESPONSE=$(curl -s "$BASE_URL/api/v1/notifications/notifications/?page_size=5" \
    -H "Authorization: Token $TOKEN")

if echo "$NOTIFS_RESPONSE" | grep -q '"count"'; then
    echo -e "${GREEN}✅ نجح الاختبار${NC}"
    COUNT=$(echo "$NOTIFS_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo -e "   📊 إجمالي الإشعارات: $COUNT"
    
    # عرض أول 3 إشعارات
    echo ""
    echo "   أول 3 إشعارات:"
    echo "$NOTIFS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, notif in enumerate(data.get('results', [])[:3]):
    status = '📩' if not notif['is_read'] else '📖'
    print(f'   {status} #{notif[\"id\"]}: {notif[\"title\"][:60]}')
" 2>/dev/null || echo "   (تعذر عرض التفاصيل)"
else
    echo -e "${RED}❌ فشل الاختبار${NC}"
    echo "$NOTIFS_RESPONSE"
fi
echo ""

# جلب الإشعارات غير المقروءة
echo "════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📩 اختبار 3: جلب الإشعارات غير المقروءة${NC}"
echo "────────────────────────────────────────────────────────────────"
UNREAD_RESPONSE=$(curl -s "$BASE_URL/api/v1/notifications/notifications/unread/" \
    -H "Authorization: Token $TOKEN")

if echo "$UNREAD_RESPONSE" | grep -q '"count"'; then
    echo -e "${GREEN}✅ نجح الاختبار${NC}"
    UNREAD_COUNT=$(echo "$UNREAD_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo -e "   📊 عدد الإشعارات غير المقروءة: $UNREAD_COUNT"
else
    echo -e "${RED}❌ فشل الاختبار${NC}"
    echo "$UNREAD_RESPONSE"
fi
echo ""

# جلب المواضيع
echo "════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📂 اختبار 4: جلب المواضيع${NC}"
echo "────────────────────────────────────────────────────────────────"
TOPICS_RESPONSE=$(curl -s "$BASE_URL/api/v1/notifications/topics/my-topics/" \
    -H "Authorization: Token $TOKEN")

if echo "$TOPICS_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ نجح الاختبار${NC}"
    
    echo ""
    echo "   المواضيع المتاحة:"
    echo "$TOPICS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for topic in data.get('data', []):
    subscribed = '✅' if topic.get('is_subscribed') else '⬜'
    print(f'   {subscribed} #{topic[\"id\"]}: {topic[\"name\"]}')
    print(f'      👥 المشتركون: {topic.get(\"subscribers_count\", 0)}')
" 2>/dev/null || echo "   (تعذر عرض التفاصيل)"
else
    echo -e "${RED}❌ فشل الاختبار${NC}"
    echo "$TOPICS_RESPONSE"
fi
echo ""

# الملخص
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ انتهى الاختبار!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}💡 للاختبار المتقدم:${NC}"
echo ""
echo "# تحديد إشعار كمقروء:"
echo "curl -X PATCH \"$BASE_URL/api/v1/notifications/notifications/NOTIF_ID/update/\" \\"
echo "  -H \"Authorization: Token $TOKEN\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"is_read\": true}'"
echo ""
echo "# تحديد جميع الإشعارات كمقروءة:"
echo "curl -X POST \"$BASE_URL/api/v1/notifications/notifications/mark-all-read/\" \\"
echo "  -H \"Authorization: Token $TOKEN\""
echo ""
echo "# حذف إشعار:"
echo "curl -X DELETE \"$BASE_URL/api/v1/notifications/notifications/NOTIF_ID/delete/\" \\"
echo "  -H \"Authorization: Token $TOKEN\""
echo ""

