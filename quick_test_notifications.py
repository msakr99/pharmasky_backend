"""
سكريبت اختبار سريع للإشعارات (بدون تفاعل)

الاستخدام:
python quick_test_notifications.py --token YOUR_TOKEN
python quick_test_notifications.py --username +201234567890 --password yourpass
"""

import requests
import argparse
import sys
from datetime import datetime


def test_notifications_api(base_url, token):
    """اختبار سريع لجميع endpoints الإشعارات"""
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "="*80)
    print("🔔 بدء اختبار نظام الإشعارات")
    print("="*80 + "\n")
    
    # Test 1: Get Stats
    print("📊 اختبار 1: جلب الإحصائيات")
    print("-" * 80)
    response = requests.get(f"{base_url}/api/v1/notifications/notifications/stats/", headers=headers)
    if response.status_code == 200:
        stats = response.json().get('data', {})
        print(f"✅ نجح الاختبار")
        print(f"   📬 الإجمالي: {stats.get('total', 0)}")
        print(f"   📩 غير المقروءة: {stats.get('unread', 0)}")
        print(f"   📖 المقروءة: {stats.get('read', 0)}")
    else:
        print(f"❌ فشل الاختبار: {response.status_code}")
        print(f"   الرسالة: {response.text}")
    print()
    
    # Test 2: Get All Notifications
    print("📬 اختبار 2: جلب جميع الإشعارات")
    print("-" * 80)
    response = requests.get(f"{base_url}/api/v1/notifications/notifications/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        results = data.get('results', [])
        print(f"✅ نجح الاختبار")
        print(f"   📊 إجمالي الإشعارات: {count}")
        print(f"   📄 الإشعارات في الصفحة الأولى: {len(results)}")
        if results:
            first = results[0]
            print(f"   📩 أحدث إشعار: {first['title'][:50]}...")
    else:
        print(f"❌ فشل الاختبار: {response.status_code}")
    print()
    
    # Test 3: Get Unread Notifications
    print("📩 اختبار 3: جلب الإشعارات غير المقروءة")
    print("-" * 80)
    response = requests.get(f"{base_url}/api/v1/notifications/notifications/unread/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        unread = data.get('results', [])
        print(f"✅ نجح الاختبار")
        print(f"   📊 عدد الإشعارات غير المقروءة: {len(unread)}")
        
        if unread:
            print(f"\n   أول 3 إشعارات غير مقروءة:")
            for notif in unread[:3]:
                print(f"   • #{notif['id']}: {notif['title']}")
    else:
        print(f"❌ فشل الاختبار: {response.status_code}")
    print()
    
    # Test 4: Get Topics
    print("📂 اختبار 4: جلب المواضيع")
    print("-" * 80)
    response = requests.get(f"{base_url}/api/v1/notifications/topics/my-topics/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        topics = data.get('data', [])
        print(f"✅ نجح الاختبار")
        print(f"   📊 عدد المواضيع: {len(topics)}")
        
        if topics:
            print(f"\n   المواضيع المتاحة:")
            for topic in topics:
                subscribed = "✅" if topic.get('is_subscribed') else "⬜"
                print(f"   {subscribed} #{topic['id']}: {topic['name']}")
    else:
        print(f"❌ فشل الاختبار: {response.status_code}")
    print()
    
    # Test 5: Mark notification as read (if there are unread)
    response = requests.get(f"{base_url}/api/v1/notifications/notifications/unread/", headers=headers)
    if response.status_code == 200:
        unread = response.json().get('results', [])
        if unread:
            notif_id = unread[0]['id']
            
            print(f"✓ اختبار 5: تحديد إشعار كمقروء (#{notif_id})")
            print("-" * 80)
            
            response = requests.patch(
                f"{base_url}/api/v1/notifications/notifications/{notif_id}/update/",
                headers=headers,
                json={"is_read": True}
            )
            
            if response.status_code == 200:
                print(f"✅ نجح الاختبار")
                print(f"   تم تحديد الإشعار #{notif_id} كمقروء")
            else:
                print(f"❌ فشل الاختبار: {response.status_code}")
            print()
    
    # Summary
    print("="*80)
    print("✅ انتهى الاختبار!")
    print("="*80 + "\n")


def login_and_get_token(base_url, username, password):
    """تسجيل الدخول والحصول على Token"""
    print("\n🔐 جاري تسجيل الدخول...")
    
    response = requests.post(
        f"{base_url}/api/v1/accounts/login/",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token')
        user = data.get('data', {}).get('user', {})
        
        print(f"✅ تم تسجيل الدخول بنجاح")
        print(f"👤 المستخدم: {user.get('name', username)}")
        print(f"🔑 Token: {token[:30]}...")
        
        return token
    else:
        print(f"❌ فشل تسجيل الدخول: {response.status_code}")
        print(f"   الرسالة: {response.json()}")
        return None


def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(
        description='اختبار سريع لنظام الإشعارات',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python quick_test_notifications.py --token abc123...
  python quick_test_notifications.py --username +201234567890 --password mypass
  python quick_test_notifications.py --username admin --password admin --url http://localhost:8000
        """
    )
    
    parser.add_argument('--url', default='http://127.0.0.1:8000',
                       help='Base URL للـ API (افتراضي: http://127.0.0.1:8000)')
    parser.add_argument('--token', help='Authentication Token')
    parser.add_argument('--username', help='Username للتسجيل الدخول')
    parser.add_argument('--password', help='Password للتسجيل الدخول')
    
    args = parser.parse_args()
    
    # التحقق من المصادقة
    token = args.token
    
    if not token:
        if args.username and args.password:
            token = login_and_get_token(args.url, args.username, args.password)
            if not token:
                sys.exit(1)
        else:
            print("❌ خطأ: يجب توفير --token أو (--username و --password)")
            parser.print_help()
            sys.exit(1)
    
    # تشغيل الاختبارات
    try:
        test_notifications_api(args.url, token)
    except requests.exceptions.ConnectionError:
        print("\n❌ خطأ في الاتصال!")
        print("   تأكد من تشغيل السيرفر على:", args.url)
        print("   استخدم: python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

