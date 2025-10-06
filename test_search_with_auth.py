# -*- coding: utf-8 -*-
"""
Test search functionality with authentication
"""
import requests
import json
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://129.212.140.152"

def get_auth_token(username, password):
    """Login and get auth token"""
    url = f"{BASE_URL}/accounts/login/"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"[SUCCESS] Login successful! Token obtained.")
            return token
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Login request failed: {e}")
        return None

def test_search_with_token(search_term, token):
    """Test search with authentication token"""
    url = f"{BASE_URL}/offers/max-offers/"
    params = {"search": search_term} if search_term else {}
    headers = {"Authorization": f"Token {token}"}
    
    label = f"Search: '{search_term}'" if search_term else "All Max Offers"
    print(f"\n{'='*70}")
    print(f"Testing - {label}")
    print(f"URL: {url}")
    if search_term:
        print(f"Search parameter: {search_term}")
    print(f"{'='*70}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            results = data.get('results', [])
            
            print(f"Total Results: {count}")
            print(f"Results in this page: {len(results)}")
            
            if results:
                print(f"\n{'-'*70}")
                print("Sample Results:")
                print(f"{'-'*70}")
                
                for i, result in enumerate(results[:5], 1):
                    product = result.get('product', {})
                    user = result.get('user', {})
                    
                    print(f"\n{i}. Offer ID: {result.get('id')}")
                    print(f"   Product: {product.get('name')}")
                    print(f"   Product (EN): {product.get('e_name')}")
                    print(f"   Seller: {user.get('name')}")
                    print(f"   Price: {result.get('selling_price')} EGP")
                    print(f"   Discount: {result.get('selling_discount_percentage')}%")
                    print(f"   Available: {result.get('remaining_amount')} units")
                
                return True, count
            else:
                print("\n[!] No results found for this search term.")
                return True, 0
        else:
            print(f"\n[ERROR] Request failed with status: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False, 0
            
    except Exception as e:
        print(f"\n[ERROR] Request exception: {e}")
        return False, 0

def main():
    print("\n" + "="*70)
    print("MAX OFFERS SEARCH TEST WITH AUTHENTICATION")
    print("="*70)
    
    # Test credentials - you need to provide valid credentials
    print("\nNote: You need to provide valid credentials to test")
    print("Default testing with a sample token format...")
    
    # Option 1: If you have credentials, uncomment and use:
    # username = "+20 10 20304060"  # Replace with valid username
    # password = "your_password"    # Replace with valid password
    # token = get_auth_token(username, password)
    
    # Option 2: If you already have a token, use it directly:
    print("\nTo test properly, you need to:")
    print("1. Get a valid authentication token")
    print("2. Run: test_search_with_token('search_term', 'your_token_here')")
    
    print("\n" + "="*70)
    print("INSTRUCTIONS FOR MANUAL TESTING:")
    print("="*70)
    print("\n1. First, login to get your token:")
    print("   POST http://129.212.140.152/accounts/login/")
    print("   Body: {\"username\": \"your_phone\", \"password\": \"your_password\"}")
    
    print("\n2. Then test search using curl or browser:")
    print("   GET http://129.212.140.152/offers/max-offers/?search=SEARCH_TERM")
    print("   Header: Authorization: Token YOUR_TOKEN")
    
    print("\n3. Example searches to try:")
    print("   - ?search=ا     (any product starting with Arabic letter)")
    print("   - ?search=اسبرين   (products containing 'aspirin')")
    print("   - ?search=vitamin  (products containing 'vitamin')")
    
    print("\n" + "="*70)
    print("\nIf you have a token, you can test by editing this script")
    print("and calling: test_search_with_token('search_term', 'your_token')")
    print("="*70)

if __name__ == "__main__":
    main()

