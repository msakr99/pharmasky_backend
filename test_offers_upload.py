#!/usr/bin/env python
import requests
import pandas as pd
import io
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
    
    # حفظ في ملف
    df.to_excel('test_offers.xlsx', index=False)
    print("تم إنشاء ملف test_offers.xlsx")
    return 'test_offers.xlsx'

# اختبار الرفع
def test_upload_offers():
    """اختبار رفع العروض"""
    url = "http://129.212.140.152/offers/offers/upload/"
    
    # إنشاء ملف Excel
    excel_file = create_test_excel()
    
    # البيانات المطلوبة
    data = {
        'user': 4  # معرف المستخدم (Store user)
    }
    
    files = {
        'file': open(excel_file, 'rb')
    }
    
    try:
        print(f"جاري رفع الملف إلى: {url}")
        print(f"البيانات: {data}")
        
        response = requests.post(url, data=data, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"خطأ في الطلب: {e}")
    finally:
        files['file'].close()

if __name__ == "__main__":
    test_upload_offers()
