# -*- coding: utf-8 -*-
"""
Test Excel download endpoint
"""
import requests

BASE_URL = "http://129.212.140.152"
TOKEN = "YOUR_TOKEN_HERE"  # استبدل بالـ token الخاص بك

def test_excel_download():
    print("="*70)
    print("اختبار تحميل Excel")
    print("="*70)
    
    headers = {
        "Authorization": f"Token {TOKEN}"
    }
    
    # Test 1: Download all
    print("\nTest 1: تحميل كل العروض...")
    url = f"{BASE_URL}/offers/max-offers/excel/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Size: {len(response.content)} bytes")
    
    if response.status_code == 200:
        filename = "max_offers_all.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ File saved: {filename}")
    else:
        print(f"✗ Error: {response.text[:200]}")
    
    # Test 2: Download with search
    print("\nTest 2: تحميل مع بحث...")
    url = f"{BASE_URL}/offers/max-offers/excel/?search=ا"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Size: {len(response.content)} bytes")
    
    if response.status_code == 200:
        filename = "max_offers_search.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ File saved: {filename}")
    else:
        print(f"✗ Error: {response.text[:200]}")
    
    print("\n" + "="*70)
    print("Done!")

if __name__ == "__main__":
    test_excel_download()


