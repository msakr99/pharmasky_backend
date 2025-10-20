#!/bin/bash
# اختبار سريع للإشعارات على السيرفر

echo "🔔 اختبار سريع للإشعارات"
echo "════════════════════════════════════════════"
echo ""

# المتغيرات - عدلها حسب بيئتك
USERNAME="+201090572414"
PASSWORD="Sakr4601"

# محاولة URLs مختلفة
URLS=(
    "http://localhost/api/v1/accounts/login/"
    "http://127.0.0.1/api/v1/accounts/login/"
    "http://167.71.40.9/api/v1/accounts/login/"
    "http://localhost:8000/api/v1/accounts/login/"
)

echo "🔍 البحث عن الـ API الصحيح..."
echo ""

for URL in "${URLS[@]}"; do
    echo "محاولة: $URL"
    RESPONSE=$(curl -s -X POST "$URL" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
        --max-time 3)
    
    if echo "$RESPONSE" | grep -q "token"; then
        echo "✅ نجح! الـ URL الصحيح: $URL"
        echo ""
        echo "الاستجابة:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
        echo ""
        
        # استخراج Token
        TOKEN=$(echo "$RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$TOKEN" ]; then
            echo "════════════════════════════════════════════"
            echo "🔑 Token الخاص بك:"
            echo "$TOKEN"
            echo "════════════════════════════════════════════"
            echo ""
            
            # اختبار الإشعارات
            BASE_URL=$(echo "$URL" | sed 's|/api/v1/accounts/login/||')
            echo "📊 اختبار الإحصائيات..."
            curl -s -H "Authorization: Token $TOKEN" \
                "$BASE_URL/api/v1/notifications/notifications/stats/" \
                | python3 -m json.tool 2>/dev/null
            
            echo ""
            echo "✅ الاختبار ناجح!"
            echo ""
            echo "للمزيد من الاختبارات، استخدم:"
            echo "export TOKEN=\"$TOKEN\""
            echo "curl -H \"Authorization: Token \$TOKEN\" $BASE_URL/api/v1/notifications/notifications/"
        fi
        exit 0
    else
        echo "❌ فشل"
        echo ""
    fi
done

echo "════════════════════════════════════════════"
echo "⚠️  لم يتم العثور على API يعمل"
echo ""
echo "💡 جرب:"
echo "1. تحقق من تشغيل Django/Docker:"
echo "   docker ps"
echo "   "
echo "2. تحقق من Nginx:"
echo "   systemctl status nginx"
echo ""
echo "3. جرب Django shell مباشرة:"
echo "   cd /opt/pharmasky"
echo "   python manage.py shell"

