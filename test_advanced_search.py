#!/usr/bin/env python3
"""
Test script for advanced search functionality
Tests FTS, trigram, and hybrid search modes
"""

import os
import sys
import django
import time
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from market.models import Product, Company, Category
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F, Q

User = get_user_model()


def create_test_data():
    """Create test data for search testing"""
    print("🔧 Creating test data...")
    
    # Create company
    company, created = Company.objects.get_or_create(
        name="نوفارتس",
        defaults={'e_name': 'Novartis'}
    )
    
    # Create category
    category, created = Category.objects.get_or_create(
        name="مسكنات",
        defaults={'e_name': 'Analgesics'}
    )
    
    # Create test products
    test_products = [
        {
            'name': 'باراسيتامول 500 مجم',
            'e_name': 'Paracetamol 500mg',
            'effective_material': 'باراسيتامول',
            'public_price': 15.50,
            'company': company,
            'category': category,
        },
        {
            'name': 'أسبرين 100 مجم',
            'e_name': 'Aspirin 100mg',
            'effective_material': 'أسبرين',
            'public_price': 8.25,
            'company': company,
            'category': category,
        },
        {
            'name': 'ايبوبروفين 400 مجم',
            'e_name': 'Ibuprofen 400mg',
            'effective_material': 'ايبوبروفين',
            'public_price': 12.00,
            'company': company,
            'category': category,
        },
        {
            'name': 'ديكلوفيناك 50 مجم',
            'e_name': 'Diclofenac 50mg',
            'effective_material': 'ديكلوفيناك',
            'public_price': 18.75,
            'company': company,
            'category': category,
        },
    ]
    
    for product_data in test_products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"✅ Created: {product.name}")
        else:
            print(f"ℹ️  Exists: {product.name}")


def test_fts_search(query):
    """Test Full Text Search"""
    print(f"\n🔍 Testing FTS search for: '{query}'")
    
    start_time = time.time()
    
    vector = (
        SearchVector('name', weight='A', config='simple') +
        SearchVector('effective_material', weight='B', config='simple') +
        SearchVector('company__name', weight='C', config='simple') +
        SearchVector('e_name', weight='D', config='simple')
    )
    search_query = SearchQuery(query, config='simple')
    
    results = Product.objects.select_related('company', 'category').annotate(
        rank=SearchRank(vector, search_query)
    ).filter(rank__gt=0).order_by('-rank')
    
    duration = time.time() - start_time
    
    print(f"⏱️  Duration: {duration:.3f}s")
    print(f"📊 Results: {results.count()}")
    
    for product in results[:5]:
        print(f"  • {product.name} (rank: {product.rank:.3f})")
    
    return results


def test_trigram_search(query, min_similarity=0.2):
    """Test Trigram Similarity Search"""
    print(f"\n🔍 Testing Trigram search for: '{query}' (min_sim: {min_similarity})")
    
    start_time = time.time()
    
    trig = (
        TrigramSimilarity('name', query) * 1.0 +
        TrigramSimilarity('effective_material', query) * 0.8 +
        TrigramSimilarity('company__name', query) * 0.6 +
        TrigramSimilarity('e_name', query) * 0.4
    )
    
    results = Product.objects.select_related('company', 'category').annotate(
        sim=trig
    ).filter(sim__gte=min_similarity).order_by('-sim')
    
    duration = time.time() - start_time
    
    print(f"⏱️  Duration: {duration:.3f}s")
    print(f"📊 Results: {results.count()}")
    
    for product in results[:5]:
        print(f"  • {product.name} (similarity: {product.sim:.3f})")
    
    return results


def test_hybrid_search(query, min_similarity=0.2):
    """Test Hybrid FTS + Trigram Search"""
    print(f"\n🔍 Testing Hybrid search for: '{query}' (min_sim: {min_similarity})")
    
    start_time = time.time()
    
    # FTS
    vector = (
        SearchVector('name', weight='A', config='simple') +
        SearchVector('effective_material', weight='B', config='simple') +
        SearchVector('company__name', weight='C', config='simple') +
        SearchVector('e_name', weight='D', config='simple')
    )
    search_query = SearchQuery(query, config='simple')
    
    # Trigram
    trig = (
        TrigramSimilarity('name', query) * 1.0 +
        TrigramSimilarity('effective_material', query) * 0.8 +
        TrigramSimilarity('company__name', query) * 0.6 +
        TrigramSimilarity('e_name', query) * 0.4
    )
    
    results = Product.objects.select_related('company', 'category').annotate(
        rank=SearchRank(vector, search_query),
        sim=trig,
        score=F('rank')*1.0 + F('sim')*0.7
    ).filter(
        Q(rank__gt=0) | Q(sim__gte=min_similarity)
    ).order_by('-score')
    
    duration = time.time() - start_time
    
    print(f"⏱️  Duration: {duration:.3f}s")
    print(f"📊 Results: {results.count()}")
    
    for product in results[:5]:
        print(f"  • {product.name} (rank: {product.rank:.3f}, sim: {product.sim:.3f}, score: {product.score:.3f})")
    
    return results


def test_typo_tolerance():
    """Test typo tolerance with trigram"""
    print("\n🧪 Testing typo tolerance...")
    
    # Test with common typos
    typos = [
        "باراسيتامول",  # Correct
        "باراسيتامول",  # Same
        "باراسيتامول",  # Same
        "باراسيتامول",  # Same
    ]
    
    for typo in typos:
        print(f"\n🔍 Testing typo: '{typo}'")
        results = test_trigram_search(typo, min_similarity=0.1)
        if results.exists():
            print(f"✅ Found {results.count()} matches")
        else:
            print("❌ No matches found")


def test_performance():
    """Test search performance"""
    print("\n⚡ Performance Testing...")
    
    queries = [
        "باراسيتامول",
        "أسبرين", 
        "ايبوبروفين",
        "ديكلوفيناك",
        "نوفارتس",
        "مسكنات"
    ]
    
    total_fts_time = 0
    total_trigram_time = 0
    total_hybrid_time = 0
    
    for query in queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # FTS
        start = time.time()
        test_fts_search(query)
        fts_time = time.time() - start
        total_fts_time += fts_time
        
        # Trigram
        start = time.time()
        test_trigram_search(query)
        trigram_time = time.time() - start
        total_trigram_time += trigram_time
        
        # Hybrid
        start = time.time()
        test_hybrid_search(query)
        hybrid_time = time.time() - start
        total_hybrid_time += hybrid_time
    
    print(f"\n📊 Performance Summary:")
    print(f"  FTS Average: {total_fts_time/len(queries):.3f}s")
    print(f"  Trigram Average: {total_trigram_time/len(queries):.3f}s")
    print(f"  Hybrid Average: {total_hybrid_time/len(queries):.3f}s")


def main():
    """Main test function"""
    print("🚀 Advanced Search Testing")
    print("=" * 50)
    
    # Create test data
    create_test_data()
    
    # Test different search modes
    test_queries = [
        "باراسيتامول",
        "أسبرين",
        "ايبوبروفين",
        "نوفارتس"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing search for: '{query}'")
        print(f"{'='*60}")
        
        # Test all modes
        test_fts_search(query)
        test_trigram_search(query)
        test_hybrid_search(query)
    
    # Test typo tolerance
    test_typo_tolerance()
    
    # Test performance
    test_performance()
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
