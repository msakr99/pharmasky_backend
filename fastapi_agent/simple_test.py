"""
Simple test for LLM understanding
"""
import requests
import json


def test_api():
    """Test API endpoints"""
    base_url = "http://129.212.140.152:8001"
    
    # Test messages
    test_messages = [
        "صباح الخير",
        "عايز باراسيتامول", 
        "أريد دواء للصداع",
        "ما هي أفضل العروض المتاحة؟"
    ]
    
    print("🧪 Testing API Endpoints\n")
    
    for message in test_messages:
        print(f"📝 Testing: '{message}'")
        
        # Test different endpoints
        endpoints = [
            "/agent/chat",
            "/agent/test-chat", 
            "/agent/smart-chat"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                data = {"message": message}
                
                response = requests.post(url, json=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {endpoint}: {result.get('message', 'No message')[:100]}...")
                else:
                    print(f"❌ {endpoint}: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ {endpoint}: Error - {str(e)[:100]}")
        
        print("-" * 50)


if __name__ == "__main__":
    test_api()
