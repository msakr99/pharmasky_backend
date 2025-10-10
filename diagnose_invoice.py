#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت تشخيص فاتورة الشراء
Diagnose Purchase Invoice Script

يساعد في تحديد سبب خطأ 500 عند محاولة إغلاق فاتورة الشراء
"""

import requests
import sys
from typing import Dict, List

# ========== الإعدادات | Settings ==========
BASE_URL = "http://129.212.140.152"
TOKEN = "your-token-here"  # ⚠️ ضع توكن المصادقة هنا
INVOICE_ID = 1  # ⚠️ رقم الفاتورة المراد فحصها

# ===========================================

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}


def print_header(text: str):
    """طباعة عنوان مميز"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """طباعة رسالة نجاح"""
    print(f"✅ {text}")


def print_error(text: str):
    """طباعة رسالة خطأ"""
    print(f"❌ {text}")


def print_warning(text: str):
    """طباعة رسالة تحذير"""
    print(f"⚠️  {text}")


def print_info(text: str):
    """طباعة معلومة"""
    print(f"ℹ️  {text}")


def get_invoice() -> Dict:
    """الحصول على تفاصيل الفاتورة"""
    print_header("جاري جلب تفاصيل الفاتورة...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/invoices/purchase-invoices/{INVOICE_ID}/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("تم جلب الفاتورة بنجاح")
            return response.json()
        elif response.status_code == 401:
            print_error("خطأ في المصادقة! تحقق من TOKEN")
            sys.exit(1)
        elif response.status_code == 404:
            print_error(f"الفاتورة رقم {INVOICE_ID} غير موجودة")
            sys.exit(1)
        else:
            print_error(f"خطأ {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_error("فشل الاتصال بالخادم! تأكد من BASE_URL")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print_error("انتهت مهلة الاتصال!")
        sys.exit(1)


def check_server_updated(invoice: Dict) -> bool:
    """التحقق من أن الخادم محدث بآخر التغييرات"""
    print_header("التحقق من تحديث الخادم")
    
    has_new_fields = all([
        'total_public_price' in invoice,
        'average_purchase_discount_percentage' in invoice
    ])
    
    if has_new_fields:
        print_success("الخادم محدث! الحقول الجديدة موجودة:")
        print(f"   - total_public_price: {invoice['total_public_price']}")
        print(f"   - average_purchase_discount_percentage: {invoice['average_purchase_discount_percentage']}")
        return True
    else:
        print_error("الخادم غير محدث! الحقول الجديدة غير موجودة")
        print_warning("يجب:")
        print("   1. رفع الملفات المعدلة إلى الخادم")
        print("   2. إعادة تشغيل Django")
        print("   راجع: DEPLOYMENT_STEPS.md")
        return False


def check_invoice_status(invoice: Dict) -> bool:
    """التحقق من حالة الفاتورة"""
    print_header("التحقق من حالة الفاتورة")
    
    status = invoice.get('status')
    print_info(f"الحالة الحالية: {status} ({invoice.get('status_label')})")
    
    if status == 'closed':
        print_error("الفاتورة مغلقة بالفعل! لا يمكن تعديلها")
        return False
    else:
        print_success(f"الحالة صحيحة ({status})")
        return True


def check_items_exist(invoice: Dict) -> bool:
    """التحقق من وجود عناصر في الفاتورة"""
    print_header("التحقق من عناصر الفاتورة")
    
    items_count = invoice.get('items_count', 0)
    items = invoice.get('items', [])
    
    if items_count == 0 or len(items) == 0:
        print_error("الفاتورة فارغة! لا تحتوي على عناصر")
        print_warning("يجب إضافة عناصر أولاً")
        return False
    else:
        print_success(f"الفاتورة تحتوي على {items_count} عنصر")
        return True


def check_items_status(invoice: Dict) -> bool:
    """التحقق من حالة العناصر"""
    print_header("التحقق من حالة العناصر")
    
    items = invoice.get('items', [])
    pending_items = []
    
    for item in items:
        status = item.get('status')
        product_name = item.get('product', {}).get('name', 'Unknown')
        
        print_info(f"العنصر {item['id']} ({product_name}): {status}")
        
        if status != 'received':
            pending_items.append(item)
    
    if pending_items:
        print_error(f"هناك {len(pending_items)} عنصر غير مستلم!")
        print_warning("يجب تحديث حالة جميع العناصر إلى 'received' قبل الإغلاق:")
        for item in pending_items:
            product_name = item.get('product', {}).get('name', 'Unknown')
            print(f"\n   PUT {BASE_URL}/invoices/purchase-invoice-items/{item['id']}/change-state/")
            print(f'   {{"status": "received"}}')
        return False
    else:
        print_success("جميع العناصر في حالة 'received' ✓")
        return True


def check_supplier_number(invoice: Dict) -> bool:
    """التحقق من رقم المورد"""
    print_header("التحقق من رقم فاتورة المورد")
    
    supplier_number = invoice.get('supplier_invoice_number', '')
    
    if supplier_number and supplier_number.strip():
        print_success(f"رقم فاتورة المورد: {supplier_number}")
        return True
    else:
        print_warning("رقم فاتورة المورد فارغ")
        print_info("سيتم إرساله في طلب الإغلاق")
        return True  # ليس خطأ فادح، يمكن إرساله مع طلب الإغلاق


def try_close_invoice() -> bool:
    """محاولة إغلاق الفاتورة"""
    print_header("محاولة إغلاق الفاتورة")
    
    data = {
        "supplier_invoice_number": "4601",
        "status": "closed"
    }
    
    print_info(f"إرسال طلب الإغلاق...")
    print(f"   PUT {BASE_URL}/invoices/purchase-invoices/{INVOICE_ID}/change-state/")
    print(f"   Data: {data}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/invoices/purchase-invoices/{INVOICE_ID}/change-state/",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print_info(f"رد الخادم: {response.status_code}")
        
        if response.status_code == 200:
            print_success("تم إغلاق الفاتورة بنجاح! 🎉")
            print("\nالاستجابة:")
            print(response.json())
            return True
        elif response.status_code == 400:
            print_error("خطأ في البيانات المرسلة:")
            print(response.json())
            return False
        elif response.status_code == 500:
            print_error("خطأ 500 في الخادم!")
            print_warning("الأسباب المحتملة:")
            print("   1. الخادم غير محدث (الأكثر احتمالاً)")
            print("   2. خطأ في قاعدة البيانات")
            print("   3. خطأ في الكود")
            print("\nافحص سجلات الخادم للتفاصيل")
            return False
        else:
            print_error(f"خطأ غير متوقع {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"خطأ في الاتصال: {str(e)}")
        return False


def main():
    """الوظيفة الرئيسية"""
    print("\n" + "█" * 60)
    print("█  سكريبت تشخيص فاتورة الشراء")
    print("█  Purchase Invoice Diagnostic Script")
    print("█" * 60)
    
    # التحقق من الإعدادات
    if TOKEN == "your-token-here":
        print_error("يجب تعيين TOKEN في الملف!")
        print_info("افتح diagnose_invoice.py وعدل قيمة TOKEN")
        sys.exit(1)
    
    print_info(f"الخادم: {BASE_URL}")
    print_info(f"الفاتورة: {INVOICE_ID}")
    
    # جلب الفاتورة
    invoice = get_invoice()
    
    # إجراء الفحوصات
    checks = {
        "تحديث الخادم": check_server_updated(invoice),
        "حالة الفاتورة": check_invoice_status(invoice),
        "وجود عناصر": check_items_exist(invoice),
        "حالة العناصر": check_items_status(invoice),
        "رقم المورد": check_supplier_number(invoice),
    }
    
    # ملخص النتائج
    print_header("ملخص الفحوصات")
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    # القرار النهائي
    print_header("النتيجة النهائية")
    
    if all_passed:
        print_success("جميع الفحوصات نجحت!")
        print_info("محاولة إغلاق الفاتورة الآن...")
        
        if try_close_invoice():
            print("\n" + "🎉" * 20)
            print("تم إغلاق الفاتورة بنجاح!")
            print("🎉" * 20)
        else:
            print_error("فشل إغلاق الفاتورة رغم نجاح الفحوصات")
            print_warning("راجع TROUBLESHOOTING_500_ERROR.md للمزيد")
    else:
        print_error("بعض الفحوصات فشلت!")
        print_warning("اتبع التعليمات أعلاه لحل المشاكل")
        print_info("راجع:")
        print("   - TROUBLESHOOTING_500_ERROR.md")
        print("   - DEPLOYMENT_STEPS.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nتم الإلغاء من قبل المستخدم")
        sys.exit(0)

