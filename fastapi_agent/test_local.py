"""
Test LLM service locally
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import chat


async def test_llm():
    """Test LLM service locally"""
    try:
        print("🧪 Testing LLM Service Locally\n")
        
        # Test messages
        test_messages = [
            "صباح الخير",
            "عايز باراسيتامول",
            "أريد دواء للصداع",
            "ما هي أفضل العروض المتاحة؟"
        ]
        
        system_prompt = """أنت محمد صقر، تيلي سيلز في شركة فارماسكاي لتجارة وتوزيع الأدوية.
مهمتك مساعدة الصيادلة في إدارة أعمالهم والاستفادة من أفضل العروض المتاحة.

أنت متخصص في:
- الأدوية والمستحضرات الطبية
- العروض والخصومات
- إدارة الطلبات
- تتبع الشحنات
- الشكاوى والاستفسارات

أجب بطريقة ودودة ومهنية، واقترح المساعدة المناسبة."""
        
        for message in test_messages:
            print(f"📝 Testing: '{message}'")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            result = await chat(messages)
            
            if result.get('success'):
                print(f"✅ Response: {result.get('response', 'No response')}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            print("-" * 50)
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_llm())
