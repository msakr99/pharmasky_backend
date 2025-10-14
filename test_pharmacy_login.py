#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار تسجيل دخول الصيدلية
Test Pharmacy Login

استخدام:
python test_pharmacy_login.py
"""

import requests
import sys

# إعدادات
BASE_URL = "http://localhost:8000"

def test_pharmacy_login(username, password):
    """
    اختبار تسجيل دخول صيدلية
    Test pharmacy login
    """
    print("\n" + "="*60)
    print("🔐 اختبار تسجيل دخول الصيدلية")
    print("   Pharmacy Login Test")
    print("="*60 + "\n")
    
    # البيانات
    url = f"{BASE_URL}/accounts/pharmacy-login/"
    data = {
        "username": username,
        "password": password
    }
    
    print(f"📞 رقم الهاتف / Phone: {username}")
    print(f"🔑 كلمة المرور / Password: {'*' * len(password)}")
    print(f"🌐 URL: {url}\n")
    
    try:
        # إرسال الطلب
        print("⏳ جاري الاتصال بالسيرفر...")
        response = requests.post(url, json=data)
        
        # عرض النتيجة
        print(f"📊 Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ تسجيل دخول ناجح! / Login Successful!\n")
            print("📦 البيانات المستلمة / Response Data:")
            print(f"   🎫 Token: {result.get('token', '')[:30]}...")
            print(f"   👤 User ID: {result.get('user_id')}")
            print(f"   🏪 Name: {result.get('name')}")
            print(f"   🎭 Role: {result.get('role')}")
            print(f"   🆕 New Login: {result.get('new_login')}")
            return result
            
        elif response.status_code == 403:
            result = response.json()
            print("❌ خطأ 403: الحساب ليس حساب صيدلية!")
            print("   Error: Account is not a pharmacy account!")
            print(f"   📝 Message: {result.get('error')}")
            return None
            
        elif response.status_code == 401 or response.status_code == 400:
            result = response.json()
            print("❌ خطأ: بيانات الدخول خاطئة!")
            print("   Error: Invalid credentials!")
            print(f"   📝 Details: {result}")
            return None
            
        else:
            print(f"❌ خطأ غير متوقع! / Unexpected Error!")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ فشل الاتصال بالسيرفر!")
        print("   Cannot connect to server!")
        print(f"   تأكد من أن السيرفر يعمل على {BASE_URL}")
        return None
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None


def test_non_pharmacy_login(username, password):
    """
    اختبار تسجيل دخول مستخدم ليس صيدلية
    Test login with non-pharmacy user
    """
    print("\n" + "="*60)
    print("🧪 اختبار: محاولة دخول مستخدم غير صيدلية")
    print("   Test: Non-pharmacy user attempting login")
    print("="*60 + "\n")
    
    result = test_pharmacy_login(username, password)
    
    if result is None:
        print("\n✅ الاختبار نجح: تم رفض المستخدم غير الصيدلية بنجاح")
        print("   Test passed: Non-pharmacy user rejected successfully")
    else:
        print("\n❌ الاختبار فشل: كان يجب رفض المستخدم")
        print("   Test failed: User should have been rejected")


def compare_endpoints(username, password):
    """
    مقارنة بين /login/ و /pharmacy-login/
    Compare /login/ and /pharmacy-login/
    """
    print("\n" + "="*60)
    print("🔄 مقارنة بين endpoint العام وendpoint الصيدليات")
    print("   Comparing general login vs pharmacy-specific login")
    print("="*60 + "\n")
    
    # 1. اختبار /login/
    print("1️⃣ اختبار /accounts/login/ (عام)")
    url1 = f"{BASE_URL}/accounts/login/"
    try:
        response1 = requests.post(url1, json={"username": username, "password": password})
        if response1.status_code == 200:
            print(f"   ✅ نجح - Role: {response1.json().get('role')}")
        else:
            print(f"   ❌ فشل - Status: {response1.status_code}")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    # 2. اختبار /pharmacy-login/
    print("\n2️⃣ اختبار /accounts/pharmacy-login/ (خاص بالصيدليات)")
    url2 = f"{BASE_URL}/accounts/pharmacy-login/"
    try:
        response2 = requests.post(url2, json={"username": username, "password": password})
        if response2.status_code == 200:
            result = response2.json()
            print(f"   ✅ نجح - Name: {result.get('name')}")
        elif response2.status_code == 403:
            print(f"   ⚠️  مرفوض - ليس حساب صيدلية")
        else:
            print(f"   ❌ فشل - Status: {response2.status_code}")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")


def interactive_test():
    """
    اختبار تفاعلي
    Interactive test
    """
    print("\n" + "="*60)
    print("🧪 اختبار تسجيل دخول الصيدلية التفاعلي")
    print("   Interactive Pharmacy Login Test")
    print("="*60 + "\n")
    
    username = input("📞 أدخل رقم الهاتف / Enter phone number: ").strip()
    password = input("🔑 أدخل كلمة المرور / Enter password: ").strip()
    
    if not username or not password:
        print("\n❌ يجب إدخال رقم الهاتف وكلمة المرور!")
        return
    
    result = test_pharmacy_login(username, password)
    
    if result:
        print("\n" + "="*60)
        print("💡 الخطوات التالية / Next Steps:")
        print("="*60)
        print("\n1. احفظ التوكن للاستخدام في الطلبات القادمة:")
        print(f'   localStorage.setItem("authToken", "{result["token"]}")')
        print("\n2. استخدم التوكن في الطلبات:")
        print(f'   Authorization: Token {result["token"][:20]}...')
        print("\n3. جرب الحصول على بياناتك:")
        print(f'   curl -X POST {BASE_URL}/accounts/whoami/ \\')
        print(f'     -H "Authorization: Token {result["token"]}"')


def main():
    """الدالة الرئيسية / Main function"""
    print("="*60)
    print("🔐 نظام اختبار تسجيل دخول الصيدلية")
    print("   Pharmacy Login Testing System")
    print("="*60)
    print(f"\n🌐 Server URL: {BASE_URL}")
    print(f"📍 Endpoint: /accounts/pharmacy-login/\n")
    
    if len(sys.argv) == 3:
        # استخدام من سطر الأوامر
        username = sys.argv[1]
        password = sys.argv[2]
        test_pharmacy_login(username, password)
    else:
        # وضع تفاعلي
        print("الخيارات / Options:")
        print("1. اختبار تفاعلي / Interactive test")
        print("2. اختبار سريع (حساب تجريبي) / Quick test")
        
        choice = input("\nاختر / Choose (1-2): ").strip()
        
        if choice == "1":
            interactive_test()
        elif choice == "2":
            print("\n⚠️  استخدم بيانات حقيقية من قاعدة البيانات")
            print("   Use real credentials from database\n")
            username = input("Phone: ").strip()
            password = input("Password: ").strip()
            if username and password:
                test_pharmacy_login(username, password)
        else:
            print("\n❌ اختيار غير صحيح!")
            print("\nاستخدام / Usage:")
            print("  python test_pharmacy_login.py")
            print("  python test_pharmacy_login.py +201234567890 password123")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إلغاء الاختبار / Test cancelled")
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع / Unexpected error: {e}")

