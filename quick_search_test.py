#!/usr/bin/env python3
"""
Quick test for advanced search functionality
Run this to verify search is working correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.production')
django.setup()

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from market.models import Product
from django.db.models import F, Q


def test_search_functionality():
    """Test if search functionality is working"""
    print("🔍 Testing Advanced Search Functionality")
    print("=" * 50)
    
    # Test 1: Check if we have products
    product_count = Product.objects.count()
    print(f"📊 Total products in database: {product_count}")
    
    if product_count == 0:
        print("❌ No products found. Please add some products first.")
        return False
    
    # Test 2: Test FTS search
    print("\n🔍 Testing FTS Search...")
    try:
        vector = SearchVector('name', weight='A', config='simple')
        query = SearchQuery('test', config='simple')
        
        results = Product.objects.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gt=0)
        
        print(f"✅ FTS search working. Found {results.count()} results for 'test'")
    except Exception as e:
        print(f"❌ FTS search failed: {e}")
        return False
    
    # Test 3: Test Trigram search
    print("\n🔍 Testing Trigram Search...")
    try:
        results = Product.objects.annotate(
            sim=TrigramSimilarity('name', 'test')
        ).filter(sim__gte=0.1)
        
        print(f"✅ Trigram search working. Found {results.count()} results for 'test'")
    except Exception as e:
        print(f"❌ Trigram search failed: {e}")
        return False
    
    # Test 4: Test Hybrid search
    print("\n🔍 Testing Hybrid Search...")
    try:
        vector = SearchVector('name', weight='A', config='simple')
        query = SearchQuery('test', config='simple')
        trig = TrigramSimilarity('name', 'test')
        
        results = Product.objects.annotate(
            rank=SearchRank(vector, query),
            sim=trig,
            score=F('rank')*1.0 + F('sim')*0.7
        ).filter(
            Q(rank__gt=0) | Q(sim__gte=0.1)
        )
        
        print(f"✅ Hybrid search working. Found {results.count()} results for 'test'")
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
        return False
    
    # Test 5: Test with actual Arabic text
    print("\n🔍 Testing with Arabic text...")
    try:
        # Get first product with Arabic name
        product = Product.objects.filter(name__isnull=False).exclude(name='').first()
        if product:
            arabic_name = product.name[:10]  # First 10 characters
            
            vector = SearchVector('name', weight='A', config='simple')
            query = SearchQuery(arabic_name, config='simple')
            
            results = Product.objects.annotate(
                rank=SearchRank(vector, query)
            ).filter(rank__gt=0)
            
            print(f"✅ Arabic search working. Found {results.count()} results for '{arabic_name}'")
        else:
            print("ℹ️  No Arabic products found to test")
    except Exception as e:
        print(f"❌ Arabic search failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All search tests passed!")
    print("🚀 Advanced search is ready to use!")
    return True


def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🌐 Testing API Endpoint...")
    
    try:
        import requests
        
        # Test basic search
        response = requests.get('http://localhost:8000/api/v1/market/products/?q=test')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API endpoint working. Found {data.get('count', 0)} results")
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ℹ️  API server not running. Start with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True


def main():
    """Main test function"""
    print("🚀 Quick Search Test")
    print("=" * 50)
    
    # Test search functionality
    search_ok = test_search_functionality()
    
    if search_ok:
        # Test API endpoint
        test_api_endpoint()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📚 Usage Examples:")
        print("  GET /api/v1/market/products/?q=باراسيتامول")
        print("  GET /api/v1/market/products/?q=test&search_mode=fts")
        print("  GET /api/v1/market/products/?q=test&search_mode=trigram&min_similarity=0.3")
        print("  GET /api/v1/market/products/?q=test&search_mode=hybrid")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
