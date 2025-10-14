#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت للتحقق من مستخدمي الصيدليات في قاعدة البيانات
Script to check pharmacy users in database
"""

import os
import sys
import django

# إعداد Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import User, Pharmacy
from accounts.choices import Role


def list_all_pharmacies():
    """عرض جميع الصيدليات في قاعدة البيانات"""
    print("\n" + "="*80)
    print("📋 قائمة الصيدليات في قاعدة البيانات")
    print("   List of Pharmacies in Database")
    print("="*80 + "\n")
    
    pharmacies = User.objects.filter(role=Role.PHARMACY)
    
    if not pharmacies.exists():
        print("⚠️  لا توجد صيدليات في قاعدة البيانات!")
        print("   No pharmacies found in database!")
        return
    
    print(f"📊 العدد الإجمالي / Total: {pharmacies.count()} صيدلية\n")
    
    for i, pharmacy in enumerate(pharmacies, 1):
        print(f"{i}. {'='*70}")
        print(f"   🆔 ID: {pharmacy.id}")
        print(f"   👤 Name: {pharmacy.name}")
        print(f"   📱 Username (Phone): {pharmacy.username}")
        print(f"   🏪 English Name: {pharmacy.e_name or 'N/A'}")
        print(f"   🎭 Role: {pharmacy.get_role_display()}")
        print(f"   ✅ Active: {'Yes' if pharmacy.is_active else 'No'}")
        print(f"   🔑 Has usable password: {'Yes' if pharmacy.has_usable_password() else 'No'}")
        print()


def search_pharmacy(search_term):
    """البحث عن صيدلية محددة"""
    print("\n" + "="*80)
    print(f"🔍 البحث عن: {search_term}")
    print("="*80 + "\n")
    
    # البحث في رقم الهاتف أو الاسم
    pharmacies = User.objects.filter(
        role=Role.PHARMACY
    ).filter(
        username__icontains=search_term
    ) | User.objects.filter(
        role=Role.PHARMACY,
        name__icontains=search_term
    )
    
    if not pharmacies.exists():
        print("❌ لم يتم العثور على صيدليات!")
        print("   No pharmacies found!")
        
        # اقتراحات
        print("\n💡 اقتراحات / Suggestions:")
        print("   - تحقق من رقم الهاتف الكامل")
        print("   - جرب البحث بجزء من الاسم")
        print("   - استخدم الأمر: python check_pharmacy_users.py --list")
        return
    
    print(f"✅ تم العثور على {pharmacies.count()} نتيجة:\n")
    
    for pharmacy in pharmacies:
        print(f"{'='*70}")
        print(f"🆔 ID: {pharmacy.id}")
        print(f"👤 Name: {pharmacy.name}")
        print(f"📱 Phone: {pharmacy.username}")
        print(f"✅ Active: {'Yes' if pharmacy.is_active else 'No'}")
        print()


def check_specific_user(username):
    """التحقق من مستخدم محدد"""
    print("\n" + "="*80)
    print(f"🔍 التحقق من المستخدم: {username}")
    print("="*80 + "\n")
    
    try:
        user = User.objects.get(username=username)
        
        print("✅ تم العثور على المستخدم!\n")
        print(f"🆔 ID: {user.id}")
        print(f"👤 Name: {user.name}")
        print(f"📱 Username: {user.username}")
        print(f"🎭 Role: {user.get_role_display()} ({user.role})")
        print(f"✅ Active: {'Yes' if user.is_active else 'No'}")
        print(f"🔑 Has usable password: {'Yes' if user.has_usable_password() else 'No'}")
        
        # تحقق من الدور
        if user.role == Role.PHARMACY:
            print(f"\n✅ هذا المستخدم صيدلية - يمكنه استخدام /pharmacy-login/")
        else:
            print(f"\n⚠️  هذا المستخدم ليس صيدلية!")
            print(f"   Role الحالي: {user.role}")
            print(f"   لا يمكنه استخدام /pharmacy-login/")
            print(f"   استخدم /login/ بدلاً من ذلك")
        
    except User.DoesNotExist:
        print("❌ المستخدم غير موجود في قاعدة البيانات!")
        print("   User not found in database!")
        print(f"\n🔍 تحقق من:")
        print(f"   1. رقم الهاتف صحيح؟ {username}")
        print(f"   2. الرقم مكتمل؟ (يجب أن يكون +201234567890)")
        print(f"   3. تم تسجيل المستخدم؟")
        
        # البحث عن أرقام مشابهة
        similar = User.objects.filter(username__icontains=username.replace('+20', ''))
        if similar.exists():
            print(f"\n💡 أرقام مشابهة موجودة:")
            for u in similar[:5]:
                print(f"   - {u.username} ({u.name})")


def create_test_pharmacy():
    """إنشاء صيدلية تجريبية"""
    print("\n" + "="*80)
    print("➕ إنشاء صيدلية تجريبية")
    print("="*80 + "\n")
    
    test_phone = "+201234567890"
    
    # تحقق من عدم وجود الرقم
    if User.objects.filter(username=test_phone).exists():
        print(f"⚠️  الرقم {test_phone} موجود بالفعل!")
        return
    
    confirm = input(f"هل تريد إنشاء صيدلية تجريبية برقم {test_phone}؟ (y/n): ")
    if confirm.lower() != 'y':
        print("❌ تم الإلغاء")
        return
    
    try:
        pharmacy = User.objects.create_user(
            username=test_phone,
            name="صيدلية تجريبية",
            e_name="Test Pharmacy",
            role=Role.PHARMACY,
            password="TestPass123"
        )
        
        print("\n✅ تم إنشاء الصيدلية بنجاح!")
        print(f"📱 Phone: {pharmacy.username}")
        print(f"👤 Name: {pharmacy.name}")
        print(f"🔑 Password: TestPass123")
        print(f"\n🧪 اختبر الآن:")
        print(f'   curl -X POST http://localhost:8000/accounts/pharmacy-login/ \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"username": "{test_phone}", "password": "TestPass123"}}\'')
        
    except Exception as e:
        print(f"❌ خطأ في الإنشاء: {e}")


def reset_user_password(username):
    """إعادة تعيين كلمة مرور مستخدم"""
    print("\n" + "="*80)
    print(f"🔑 إعادة تعيين كلمة المرور لـ: {username}")
    print("="*80 + "\n")
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ تم العثور على: {user.name}\n")
        
        new_password = input("أدخل كلمة المرور الجديدة: ")
        if not new_password:
            print("❌ تم الإلغاء")
            return
        
        confirm = input(f"تأكيد كلمة المرور: ")
        if new_password != confirm:
            print("❌ كلمات المرور غير متطابقة!")
            return
        
        user.set_password(new_password)
        user.save()
        
        print(f"\n✅ تم تغيير كلمة المرور بنجاح!")
        print(f"👤 User: {user.name}")
        print(f"📱 Phone: {user.username}")
        print(f"🔑 New Password: {new_password}")
        
    except User.DoesNotExist:
        print("❌ المستخدم غير موجود!")


def main():
    """الدالة الرئيسية"""
    print("="*80)
    print("🔐 أداة فحص مستخدمي الصيدليات")
    print("   Pharmacy Users Check Tool")
    print("="*80)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--list':
            list_all_pharmacies()
        elif command == '--search' and len(sys.argv) > 2:
            search_pharmacy(sys.argv[2])
        elif command == '--check' and len(sys.argv) > 2:
            check_specific_user(sys.argv[2])
        elif command == '--create-test':
            create_test_pharmacy()
        elif command == '--reset-password' and len(sys.argv) > 2:
            reset_user_password(sys.argv[2])
        else:
            print("\n❌ أمر غير صحيح!\n")
            show_help()
    else:
        # وضع تفاعلي
        interactive_mode()


def interactive_mode():
    """الوضع التفاعلي"""
    while True:
        print("\n" + "="*80)
        print("الخيارات / Options:")
        print("="*80)
        print("1. عرض جميع الصيدليات / List all pharmacies")
        print("2. البحث عن صيدلية / Search pharmacy")
        print("3. التحقق من مستخدم محدد / Check specific user")
        print("4. إنشاء صيدلية تجريبية / Create test pharmacy")
        print("5. إعادة تعيين كلمة مرور / Reset password")
        print("0. خروج / Exit")
        
        choice = input("\nاختر / Choose: ").strip()
        
        if choice == '1':
            list_all_pharmacies()
        elif choice == '2':
            term = input("أدخل رقم الهاتف أو الاسم / Enter phone or name: ").strip()
            if term:
                search_pharmacy(term)
        elif choice == '3':
            username = input("أدخل رقم الهاتف / Enter phone: ").strip()
            if username:
                check_specific_user(username)
        elif choice == '4':
            create_test_pharmacy()
        elif choice == '5':
            username = input("أدخل رقم الهاتف / Enter phone: ").strip()
            if username:
                reset_user_password(username)
        elif choice == '0':
            print("\n👋 إلى اللقاء!")
            break
        else:
            print("❌ اختيار غير صحيح!")


def show_help():
    """عرض المساعدة"""
    print("الاستخدام / Usage:")
    print("  python check_pharmacy_users.py                    # وضع تفاعلي")
    print("  python check_pharmacy_users.py --list             # عرض جميع الصيدليات")
    print("  python check_pharmacy_users.py --search <term>    # البحث")
    print("  python check_pharmacy_users.py --check <phone>    # التحقق من رقم محدد")
    print("  python check_pharmacy_users.py --create-test      # إنشاء صيدلية تجريبية")
    print("  python check_pharmacy_users.py --reset-password <phone>  # إعادة تعيين كلمة المرور")
    print("\nأمثلة / Examples:")
    print("  python check_pharmacy_users.py --list")
    print("  python check_pharmacy_users.py --search 0104")
    print("  python check_pharmacy_users.py --check +201234567890")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  تم الإلغاء")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

