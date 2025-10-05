#!/usr/bin/env python3
"""
Simple script to check users on the server
"""

import requests
import json

# Server configuration
BASE_URL = "http://129.212.140.152"
LOGIN_URL = f"{BASE_URL}/accounts/login/"

def test_login(username, password):
    """Test login with given credentials"""
    login_data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        user_id = data.get('user', {}).get('id')
        role = data.get('user', {}).get('role')
        username = data.get('user', {}).get('username')
        
        print(f"Login successful!")
        print(f"Username: {username}")
        print(f"Role: {role}")
        print(f"User ID: {user_id}")
        print(f"Token: {token[:20]}...")
        return True
    else:
        print(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    print("Testing different user credentials...")
    print("=" * 50)
    
    # Test different possible admin credentials
    test_credentials = [
        ('admin', 'admin'),
        ('admin', 'admin123'),
        ('admin', 'password'),
        ('admin', '123456'),
        ('root', 'root'),
        ('root', 'admin'),
        ('superuser', 'admin'),
        ('testuser', 'testpass'),
        ('testuser', 'password'),
    ]
    
    for username, password in test_credentials:
        print(f"\nTesting: {username} / {password}")
        print("-" * 30)
        if test_login(username, password):
            print(f"Found working credentials: {username} / {password}")
            break
    else:
        print("\nNo working credentials found")

if __name__ == "__main__":
    main()
