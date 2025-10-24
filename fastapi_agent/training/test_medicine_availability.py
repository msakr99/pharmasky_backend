#!/usr/bin/env python3
"""
Test script for medicine availability scenarios
Tests the trained model's ability to handle medicine availability queries
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test scenarios for medicine availability
TEST_SCENARIOS = [
    {
        "name": "إيزوجاست متوفر",
        "input": "إيزوجاست موجود؟",
        "expected_keywords": ["متوفر", "إيزوجاست", "سعر", "خصم", "كم علبة"]
    },
    {
        "name": "إيزوجاست غير متوفر",
        "input": "إيزوجاست خلصان؟",
        "expected_keywords": ["خلصان", "متى يجي", "أول ما يجي", "بدائل"]
    },
    {
        "name": "طلب إيزوجاست",
        "input": "عايز إيزوجاست",
        "expected_keywords": ["متوفر", "إيزوجاست", "سعر", "خصم", "كم علبة"]
    },
    {
        "name": "سعر إيزوجاست",
        "input": "إيزوجاست سعره كام؟",
        "expected_keywords": ["سعر", "إيزوجاست", "خصم", "متوفر"]
    },
    {
        "name": "تحقق من التوفر",
        "input": "إيزوجاست متوفر ولا لأ؟",
        "expected_keywords": ["متوفر", "إيزوجاست", "سعر", "خصم"]
    }
]

async def test_medicine_availability():
    """Test medicine availability scenarios"""
    print("🧪 Testing Medicine Availability Scenarios")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n📋 Test {i}: {scenario['name']}")
            print(f"Input: {scenario['input']}")
            
            try:
                response = await client.post(
                    "http://129.212.140.152:8001/agent/trained-chat",
                    json={"message": scenario['input']},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    output = data.get('message', '')
                    
                    print(f"✅ Response: {output[:100]}...")
                    
                    # Check for expected keywords
                    found_keywords = []
                    missing_keywords = []
                    
                    for keyword in scenario['expected_keywords']:
                        if keyword in output:
                            found_keywords.append(keyword)
                        else:
                            missing_keywords.append(keyword)
                    
                    print(f"✅ Found keywords: {found_keywords}")
                    if missing_keywords:
                        print(f"❌ Missing keywords: {missing_keywords}")
                    
                    # Calculate score
                    score = len(found_keywords) / len(scenario['expected_keywords']) * 100
                    print(f"📊 Score: {score:.1f}%")
                    
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
            
            print("-" * 30)

async def test_specific_medicine(medicine_name: str):
    """Test specific medicine availability"""
    print(f"\n🔍 Testing {medicine_name} Availability")
    print("=" * 50)
    
    test_queries = [
        f"{medicine_name} موجود؟",
        f"{medicine_name} متوفر؟",
        f"{medicine_name} خلصان؟",
        f"{medicine_name} سعره كام؟",
        f"عايز {medicine_name}"
    ]
    
    async with httpx.AsyncClient() as client:
        for query in test_queries:
            print(f"\n💬 Query: {query}")
            
            try:
                response = await client.post(
                    "http://129.212.140.152:8001/agent/trained-chat",
                    json={"message": query},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    output = data.get('message', '')
                    print(f"✅ Response: {output}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting Medicine Availability Tests")
    print("=" * 60)
    
    # Test general scenarios
    await test_medicine_availability()
    
    # Test specific medicines
    medicines = ["إيزوجاست", "باراسيتامول", "فيتامين د", "أوميبرازول"]
    
    for medicine in medicines:
        await test_specific_medicine(medicine)
    
    print("\n🎉 Medicine Availability Tests Completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
