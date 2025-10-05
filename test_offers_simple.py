#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pandas as pd
import json

# إنشاء ملف Excel نموذجي للعروض
def create_test_excel():
    """إنشاء ملف Excel للاختبار"""
    test_data = {
        'product_code': [22, 23, 24, 25, 26],
        'available_amount': [100, 50, 200, 75, 150],
        'purchase_discount_percentage': [15.50, 20.00, 10.25, 18.75, 12.00],
        'max_amount_per_invoice': [10, 5, 20, 8, 15],
        'min_purchase': [100.00, 50.00, 0.00, 75.00, 200.00],
        'product_expiry_date': ['2025-12-31', '2026-01-15', '2025-11-30', '2026-02-28', '2025-10-15'],
        'operating_number': ['OP001', 'OP002', 'OP003', 'OP004', 'OP005']
    }
    
    df = pd.DataFrame(test_data)
    df.to_excel('test_offers.xlsx', index=False)
    print("تم إنشاء ملف test_offers.xlsx")
    return 'test_offers.xlsx'

# الحصول على token
def get_auth_token():
    """الحصول على token للـ authentication"""
    login_url = "http://129.212.140.152/accounts/login/"
    
    # بيانات تسجيل الدخول - جرب بيانات مختلفة
    login_attempts = [
        {'username': 'admin', 'password': 'admin'},
        {'username': '01234567890', 'password': '123456'},
        {'username': 'store', 'password': 'store'},
        {'username': 'pharmacy', 'password': 'pharmacy'},
    ]
    
    for login_data in login_attempts:
        try:
            print(f"جاري محاولة تسجيل الدخول بـ: {login_data['username']}")
            response = requests.post(login_url, json=login_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get('token')
                role = token_data.get('role')
                print(f"تم تسجيل الدخول بنجاح!")
                print(f"Role: {role}")
                print(f"Token: {token[:20]}...")
                return token, role
            else:
                print(f"فشل تسجيل الدخول: {response.text}")
                
        except Exception as e:
            print(f"خطأ في تسجيل الدخول: {e}")
    
    print("فشل في جميع محاولات تسجيل الدخول")
    return None, None

# اختبار الرفع
def test_upload_offers():
    """اختبار رفع العروض"""
    print("بدء اختبار رفع العروض...")
    
    # الحصول على token
    token, role = get_auth_token()
    
    if not token:
        print("لا يمكن المتابعة بدون token")
        return
    
    # إنشاء ملف Excel
    excel_file = create_test_excel()
    
    # إعداد الطلب
    url = "http://129.212.140.152/offers/offers/upload/"
    headers = {
        'Authorization': f'Token {token}'
    }
    
    data = {
        'user': 4  # معرف المستخدم (Store user)
    }
    
    files = {
        'file': open(excel_file, 'rb')
    }
    
    try:
        print(f"جاري رفع الملف إلى: {url}")
        print(f"User ID: {data['user']}")
        print(f"User Role: {role}")
        
        response = requests.post(url, data=data, files=files, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("تم رفع العروض بنجاح!")
            response_json = response.json()
            print(f"النتيجة: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        else:
            print(f"فشل في رفع العروض")
            try:
                error_json = response.json()
                print(f"تفاصيل الخطأ: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
            except:
                print(f"نص الخطأ: {response.text}")
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")
    finally:
        files['file'].close()

if __name__ == "__main__":
    test_upload_offers()
