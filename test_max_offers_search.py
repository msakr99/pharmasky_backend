#!/usr/bin/env python
"""
Quick test script for Max Offers Advanced Search
Run: python test_max_offers_search.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your-auth-token-here"  # استبدله بـ token حقيقي

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

def test_search(query, mode='hybrid', min_similarity=0.2):
    """Test search with given parameters"""
    url = f"{BASE_URL}/offers/max-offers/"
    params = {
        'q': query,
        'search_mode': mode,
        'min_similarity': min_similarity
    }
    
    start_time = datetime.now()
    response = requests.get(url, params=params, headers=headers)
    end_time = datetime.now()
    
    elapsed_ms = (end_time - start_time).total_seconds() * 1000
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        results = data.get('results', [])
        
        print(f"✅ Query: '{query}' | Mode: {mode}")
        print(f"   Results: {count} | Time: {elapsed_ms:.2f}ms")
        
        if results and len(results) > 0:
            first = results[0]
            product_name = first.get('product', {}).get('name', 'N/A')
            print(f"   Top result: {product_name}")
            
            # Show scores if available
            if 'rank' in first:
                print(f"   Rank: {first.get('rank', 0):.3f}")
            if 'sim' in first:
                print(f"   Similarity: {first.get('sim', 0):.3f}")
            if 'score' in first:
                print(f"   Score: {first.get('score', 0):.3f}")
        
        print()
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        print()
        return False

def main():
    print("🔍 Testing Max Offers Advanced Search")
    print("=" * 50)
    print()
    
    # Test 1: Hybrid Mode (Default)
    print("1️⃣ Testing Hybrid Mode (Default)...")
    test_search("test", mode="hybrid")
    
    # Test 2: FTS Mode
    print("2️⃣ Testing FTS Mode...")
    test_search("test", mode="fts")
    
    # Test 3: Trigram Mode
    print("3️⃣ Testing Trigram Mode...")
    test_search("test", mode="trigram", min_similarity=0.2)
    
    # Test 4: Arabic Search
    print("4️⃣ Testing Arabic Search...")
    test_search("باراسيتامول", mode="hybrid")
    
    # Test 5: Typo Handling
    print("5️⃣ Testing Typo Handling...")
    test_search("parasetmol", mode="trigram", min_similarity=0.2)
    
    # Test 6: Company Search
    print("6️⃣ Testing Company Search...")
    test_search("نوفارتس", mode="hybrid")
    
    # Test 7: Low Similarity (More Results)
    print("7️⃣ Testing Low Similarity...")
    test_search("aspirin", mode="trigram", min_similarity=0.15)
    
    # Test 8: High Similarity (Precise)
    print("8️⃣ Testing High Similarity...")
    test_search("aspirin", mode="trigram", min_similarity=0.5)
    
    print("=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print(f"   Make sure the server is running at {BASE_URL}")
    except Exception as e:
        print(f"❌ Error: {e}")

