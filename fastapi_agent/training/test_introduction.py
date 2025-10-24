"""
Test script for self-introduction training
"""
import requests
import json


def test_introduction():
    """Test self-introduction scenarios"""
    base_url = "http://129.212.140.152:8001"
    
    # Test messages for self-introduction
    test_messages = [
        "أنت مين؟",
        "عرف نفسك", 
        "من أنت؟",
        "إنت إيه؟",
        "مين أنت؟",
        "عرفني عليك",
        "إيه اسمك؟"
    ]
    
    print("🧪 Testing Self-Introduction Training")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📝 Testing: '{message}'")
        
        try:
            # Test with chat endpoint
            response = requests.post(
                f"{base_url}/agent/chat",
                json={"message": message, "context": {"user_id": 1}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('message', '')
                
                # Check if response contains key phrases
                key_phrases = [
                    "محمد صقر",
                    "تيلي سيلز", 
                    "فارماسكاي",
                    "توزيع الأدوية"
                ]
                
                found_phrases = [phrase for phrase in key_phrases if phrase in response_text]
                
                print(f"✅ Response: {response_text[:100]}...")
                print(f"🎯 Key phrases found: {found_phrases}")
                
                if len(found_phrases) >= 3:
                    print("🎉 Excellent! Model knows how to introduce itself")
                elif len(found_phrases) >= 2:
                    print("✅ Good! Model partially knows how to introduce itself")
                else:
                    print("⚠️ Model needs more training for self-introduction")
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("-" * 30)


def test_other_scenarios():
    """Test other training scenarios"""
    base_url = "http://129.212.140.152:8001"
    
    test_cases = [
        {
            "message": "عايز باراسيتامول",
            "expected_keywords": ["باراسيتامول", "سعر", "خصم", "متوفر"]
        },
        {
            "message": "ما هي أفضل العروض؟",
            "expected_keywords": ["عروض", "خصم", "أسعار", "متاح"]
        },
        {
            "message": "شكراً لك",
            "expected_keywords": ["العفو", "خدمة", "مساعدة", "تواصل"]
        }
    ]
    
    print("\n🧪 Testing Other Training Scenarios")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case['message']}'")
        
        try:
            response = requests.post(
                f"{base_url}/agent/chat",
                json={"message": test_case['message'], "context": {"user_id": 1}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('message', '')
                
                found_keywords = [keyword for keyword in test_case['expected_keywords'] 
                                if keyword in response_text]
                
                print(f"✅ Response: {response_text[:100]}...")
                print(f"🎯 Keywords found: {found_keywords}")
                
                if len(found_keywords) >= 2:
                    print("✅ Good response!")
                else:
                    print("⚠️ Response could be improved")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("-" * 30)


if __name__ == "__main__":
    test_introduction()
    test_other_scenarios()
