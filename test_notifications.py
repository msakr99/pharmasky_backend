"""
سكريبت تجريبي لاختبار نظام الإشعارات في PharmaSky

يوفر هذا السكريبت طريقة سهلة لتجربة جميع وظائف الإشعارات:
- تسجيل الدخول
- جلب الإشعارات
- إنشاء إشعارات تجريبية
- تحديد الإشعارات كمقروءة
- حذف الإشعارات
- الاشتراك في المواضيع
"""

import requests
import json
from typing import Optional, Dict, List
from datetime import datetime
import sys


class NotificationTester:
    """كلاس لاختبار نظام الإشعارات"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {
            'Content-Type': 'application/json',
        }
    
    def set_token(self, token: str):
        """تعيين Authentication Token"""
        self.token = token
        self.headers['Authorization'] = f'Token {token}'
        print(f"✅ تم تعيين Token بنجاح")
    
    def login(self, username: str, password: str) -> bool:
        """تسجيل الدخول والحصول على Token"""
        url = f"{self.base_url}/api/v1/accounts/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('data', {}).get('token')
                self.headers['Authorization'] = f'Token {self.token}'
                print(f"✅ تم تسجيل الدخول بنجاح")
                print(f"👤 المستخدم: {result.get('data', {}).get('user', {}).get('name', username)}")
                print(f"🔑 Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ فشل تسجيل الدخول: {response.status_code}")
                print(f"   الرسالة: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def get_notifications(self, page: int = 1, is_read: Optional[bool] = None) -> Dict:
        """جلب قائمة الإشعارات"""
        url = f"{self.base_url}/api/v1/notifications/notifications/"
        params = {'page': page}
        
        if is_read is not None:
            params['is_read'] = 'true' if is_read else 'false'
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ فشل جلب الإشعارات: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return {}
    
    def get_unread_notifications(self) -> Dict:
        """جلب الإشعارات غير المقروءة فقط"""
        url = f"{self.base_url}/api/v1/notifications/notifications/unread/"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ فشل جلب الإشعارات غير المقروءة: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """جلب إحصائيات الإشعارات"""
        url = f"{self.base_url}/api/v1/notifications/notifications/stats/"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ فشل جلب الإحصائيات: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return {}
    
    def mark_as_read(self, notification_id: int) -> bool:
        """تحديد إشعار كمقروء"""
        url = f"{self.base_url}/api/v1/notifications/notifications/{notification_id}/update/"
        data = {"is_read": True}
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"✅ تم تحديد الإشعار #{notification_id} كمقروء")
                return True
            else:
                print(f"❌ فشل تحديد الإشعار كمقروء: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def mark_all_as_read(self) -> Dict:
        """تحديد جميع الإشعارات كمقروءة"""
        url = f"{self.base_url}/api/v1/notifications/notifications/mark-all-read/"
        
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                count = result.get('data', {}).get('updated_count', 0)
                print(f"✅ تم تحديد {count} إشعار كمقروءة")
                return result
            else:
                print(f"❌ فشل تحديد الإشعارات كمقروءة: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return {}
    
    def delete_notification(self, notification_id: int) -> bool:
        """حذف إشعار"""
        url = f"{self.base_url}/api/v1/notifications/notifications/{notification_id}/delete/"
        
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in [200, 204]:
                print(f"✅ تم حذف الإشعار #{notification_id}")
                return True
            else:
                print(f"❌ فشل حذف الإشعار: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def get_topics(self) -> List[Dict]:
        """جلب قائمة المواضيع المتاحة"""
        url = f"{self.base_url}/api/v1/notifications/topics/"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"❌ فشل جلب المواضيع: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return []
    
    def get_my_topics(self) -> Dict:
        """جلب المواضيع مع حالة الاشتراك"""
        url = f"{self.base_url}/api/v1/notifications/topics/my-topics/"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ فشل جلب المواضيع: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return {}
    
    def subscribe_to_topic(self, topic_id: int) -> bool:
        """الاشتراك في موضوع"""
        url = f"{self.base_url}/api/v1/notifications/subscriptions/create/"
        data = {
            "topic": topic_id,
            "is_active": True
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                print(f"✅ تم الاشتراك في الموضوع #{topic_id}")
                return True
            else:
                print(f"❌ فشل الاشتراك: {response.status_code}")
                print(f"   الرسالة: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            return False
    
    def print_notifications(self, notifications: List[Dict], show_details: bool = True):
        """طباعة الإشعارات بشكل منسق"""
        if not notifications:
            print("📭 لا توجد إشعارات")
            return
        
        print(f"\n{'='*80}")
        print(f"📬 عدد الإشعارات: {len(notifications)}")
        print(f"{'='*80}\n")
        
        for notif in notifications:
            status = "📖" if notif['is_read'] else "📩"
            print(f"{status} #{notif['id']} - {notif['title']}")
            
            if show_details:
                print(f"   💬 {notif['message']}")
                print(f"   🕐 {self.format_datetime(notif['created_at'])}")
                
                if notif.get('extra'):
                    extra = notif['extra']
                    if extra.get('type'):
                        print(f"   🏷️  النوع: {extra['type']}")
                
                if notif.get('topic'):
                    print(f"   📂 الموضوع: {notif['topic']['name']}")
            
            print()
    
    def print_stats(self, stats: Dict):
        """طباعة الإحصائيات بشكل منسق"""
        if not stats:
            return
        
        data = stats.get('data', {})
        
        print(f"\n{'='*80}")
        print(f"📊 إحصائيات الإشعارات")
        print(f"{'='*80}")
        print(f"📬 الإجمالي: {data.get('total', 0)}")
        print(f"📩 غير المقروءة: {data.get('unread', 0)}")
        print(f"📖 المقروءة: {data.get('read', 0)}")
        print(f"{'='*80}\n")
    
    def print_topics(self, topics: List[Dict]):
        """طباعة المواضيع بشكل منسق"""
        if not topics:
            print("📭 لا توجد مواضيع")
            return
        
        print(f"\n{'='*80}")
        print(f"📂 المواضيع المتاحة")
        print(f"{'='*80}\n")
        
        for topic in topics:
            subscribed = "✅" if topic.get('is_subscribed', False) else "⬜"
            print(f"{subscribed} #{topic['id']} - {topic['name']}")
            print(f"   📝 {topic['description']}")
            print(f"   👥 المشتركون: {topic.get('subscribers_count', 0)}")
            print()
    
    @staticmethod
    def format_datetime(dt_string: str) -> str:
        """تنسيق التاريخ والوقت"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_string


def print_menu():
    """طباعة القائمة الرئيسية"""
    print(f"\n{'='*80}")
    print("🔔 اختبار نظام الإشعارات - PharmaSky")
    print(f"{'='*80}")
    print("1️⃣  جلب جميع الإشعارات")
    print("2️⃣  جلب الإشعارات غير المقروءة")
    print("3️⃣  عرض الإحصائيات")
    print("4️⃣  تحديد إشعار كمقروء")
    print("5️⃣  تحديد الكل كمقروء")
    print("6️⃣  حذف إشعار")
    print("7️⃣  عرض المواضيع")
    print("8️⃣  الاشتراك في موضوع")
    print("9️⃣  تسجيل الدخول من جديد")
    print("0️⃣  خروج")
    print(f"{'='*80}\n")


def main():
    """الدالة الرئيسية"""
    print("🚀 مرحباً بك في اختبار نظام الإشعارات!")
    
    # إنشاء كائن الاختبار
    tester = NotificationTester()
    
    # طلب تسجيل الدخول أو استخدام Token موجود
    print("\n📝 اختر طريقة المصادقة:")
    print("1. تسجيل الدخول بـ Username وPassword")
    print("2. استخدام Token موجود")
    
    auth_choice = input("\nاختيارك (1 أو 2): ").strip()
    
    if auth_choice == "1":
        username = input("👤 Username (رقم الهاتف): ").strip()
        password = input("🔒 Password: ").strip()
        
        if not tester.login(username, password):
            print("❌ فشل تسجيل الدخول. تأكد من البيانات أو أن السيرفر يعمل.")
            return
    elif auth_choice == "2":
        token = input("🔑 أدخل الـ Token: ").strip()
        tester.set_token(token)
    else:
        print("❌ اختيار غير صحيح")
        return
    
    # الحلقة الرئيسية
    while True:
        print_menu()
        choice = input("اختر رقم العملية: ").strip()
        
        if choice == "1":
            # جلب جميع الإشعارات
            print("\n📬 جاري جلب الإشعارات...")
            data = tester.get_notifications()
            notifications = data.get('results', [])
            tester.print_notifications(notifications)
        
        elif choice == "2":
            # جلب الإشعارات غير المقروءة
            print("\n📩 جاري جلب الإشعارات غير المقروءة...")
            data = tester.get_unread_notifications()
            notifications = data.get('results', [])
            tester.print_notifications(notifications)
        
        elif choice == "3":
            # عرض الإحصائيات
            print("\n📊 جاري جلب الإحصائيات...")
            stats = tester.get_stats()
            tester.print_stats(stats)
        
        elif choice == "4":
            # تحديد إشعار كمقروء
            notif_id = input("\n🔢 أدخل رقم الإشعار: ").strip()
            if notif_id.isdigit():
                tester.mark_as_read(int(notif_id))
            else:
                print("❌ رقم غير صحيح")
        
        elif choice == "5":
            # تحديد الكل كمقروء
            confirm = input("\n⚠️ هل أنت متأكد من تحديد جميع الإشعارات كمقروءة؟ (y/n): ")
            if confirm.lower() == 'y':
                tester.mark_all_as_read()
        
        elif choice == "6":
            # حذف إشعار
            notif_id = input("\n🔢 أدخل رقم الإشعار للحذف: ").strip()
            if notif_id.isdigit():
                confirm = input(f"⚠️ هل أنت متأكد من حذف الإشعار #{notif_id}؟ (y/n): ")
                if confirm.lower() == 'y':
                    tester.delete_notification(int(notif_id))
            else:
                print("❌ رقم غير صحيح")
        
        elif choice == "7":
            # عرض المواضيع
            print("\n📂 جاري جلب المواضيع...")
            result = tester.get_my_topics()
            topics = result.get('data', [])
            tester.print_topics(topics)
        
        elif choice == "8":
            # الاشتراك في موضوع
            topic_id = input("\n🔢 أدخل رقم الموضوع للاشتراك: ").strip()
            if topic_id.isdigit():
                tester.subscribe_to_topic(int(topic_id))
            else:
                print("❌ رقم غير صحيح")
        
        elif choice == "9":
            # تسجيل الدخول من جديد
            username = input("\n👤 Username (رقم الهاتف): ").strip()
            password = input("🔒 Password: ").strip()
            tester.login(username, password)
        
        elif choice == "0":
            # خروج
            print("\n👋 شكراً لاستخدامك نظام الإشعارات!")
            break
        
        else:
            print("❌ اختيار غير صحيح. حاول مرة أخرى.")
        
        input("\n⏎ اضغط Enter للمتابعة...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البرنامج. إلى اللقاء!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        sys.exit(1)

