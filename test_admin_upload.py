#!/usr/bin/env python3
"""
Test script for Admin uploading offers for any store
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Server configuration
BASE_URL = "http://129.212.140.152"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
UPLOAD_URL = f"{BASE_URL}/offers/offers/upload/"

def create_test_excel():
    """Create a test Excel file with sample offers"""
    data = {
        'product_code': [22, 23, 24, 25, 26],
        'available_amount': [100, 50, 200, 75, 150],
        'purchase_discount_percentage': [15.50, 20.00, 10.25, 18.75, 12.00],
        'max_amount_per_invoice': [10, 5, 20, 8, 15],
        'min_purchase': [100.00, 50.00, 0.00, 75.00, 200.00],
        'product_expiry_date': [
            (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=400)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=450)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=200)).strftime('%Y-%m-%d')
        ],
        'operating_number': ['OP001', 'OP002', 'OP003', 'OP004', 'OP005']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('test_admin_offers.xlsx', index=False)
    print("Excel file created successfully")

def login_as_admin():
    """Login as admin user"""
    login_data = {
        'username': 'testuser',  # Test username
        'password': 'testpass123'  # Test password
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        user_id = data.get('user', {}).get('id')
        role = data.get('user', {}).get('role')
        username = data.get('user', {}).get('username')
        
        print(f"Login successful as Admin!")
        print(f"Username: {username}")
        print(f"Role: {role}")
        print(f"User ID: {user_id}")
        print(f"Token: {token[:20]}...")
        
        return token, user_id, role
    else:
        print(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None, None

def upload_offers_for_store(token, target_store_id):
    """Upload offers for a specific store"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'multipart/form-data'
    }
    
    # Prepare the data
    data = {
        'user': target_store_id  # Target store ID
    }
    
    # Prepare the file
    files = {
        'file': ('test_admin_offers.xlsx', open('test_admin_offers.xlsx', 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    print(f"Uploading offers for Store ID: {target_store_id}")
    print(f"URL: {UPLOAD_URL}")
    
    response = requests.post(UPLOAD_URL, headers={'Authorization': f'Token {token}'}, data=data, files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print("Upload successful!")
        result = response.json()
        print(f"Result: {result}")
    else:
        print("Upload failed")
        print(f"Response: {response.text}")
    
    # Close the file
    files['file'][1].close()

def main():
    print("Test Admin Upload for Any Store")
    print("=" * 50)
    
    # Create test Excel file
    create_test_excel()
    
    # Login as admin
    token, admin_id, role = login_as_admin()
    
    if not token:
        print("Cannot continue without login")
        return
    
    if role != 'ADMIN':
        print(f"Warning: User is not Admin (Role: {role})")
    
    # Test uploading for different stores
    test_stores = [4, 5, 6]  # Different store IDs to test
    
    for store_id in test_stores:
        print(f"\nTesting upload for Store {store_id}")
        print("-" * 30)
        upload_offers_for_store(token, store_id)
        print()

if __name__ == "__main__":
    main()
