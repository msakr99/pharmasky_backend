"""
Test script for FastAPI AI Agent API
"""
import asyncio
import httpx
import json


async def test_without_auth():
    """Test API without authentication"""
    url = "http://129.212.140.152:8001/agent/test-chat"
    
    data = {
        "message": "صباح الخير"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")


async def test_with_token():
    """Test API with token"""
    url = "http://129.212.140.152:8001/agent/chat"
    
    headers = {
        "Authorization": "Bearer de5654ae8bcd82cb933f5a3a2e1f674bf8a302e6",
        "Content-Type": "application/json"
    }
    
    data = {
        "message": "صباح الخير"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")


async def test_verify_token():
    """Test token verification"""
    url = "http://129.212.140.152:8001/agent/verify-token"
    
    data = {
        "token": "de5654ae8bcd82cb933f5a3a2e1f674bf8a302e6"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")


async def test_with_user_id():
    """Test API with user_id fallback"""
    url = "http://129.212.140.152:8001/agent/chat"
    
    data = {
        "message": "صباح الخير",
        "context": {
            "user_id": 5
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Run all tests"""
    print("🧪 Testing FastAPI AI Agent API\n")
    
    print("=" * 50)
    print("1. Test without authentication:")
    await test_without_auth()
    
    print("\n" + "=" * 50)
    print("2. Test token verification:")
    await test_verify_token()
    
    print("\n" + "=" * 50)
    print("3. Test with token:")
    await test_with_token()
    
    print("\n" + "=" * 50)
    print("4. Test with user_id fallback:")
    await test_with_user_id()


if __name__ == "__main__":
    asyncio.run(main())
