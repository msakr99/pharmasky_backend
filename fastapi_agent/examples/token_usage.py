"""
Examples for using FastAPI AI Agent with Token Authentication
"""
import asyncio
import httpx
import json


async def chat_with_token():
    """Example: Chat with token authentication"""
    url = "http://129.212.140.152:8001/agent/chat"
    
    # Method 1: Token in Authorization header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_jwt_token_here"
    }
    
    data = {
        "message": "صباح الخير",
        "session_id": 123
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Chat with Authorization header:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def chat_with_token_in_body():
    """Example: Chat with token in request body"""
    url = "http://129.212.140.152:8001/agent/chat"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "message": "صباح الخير",
        "session_id": 123,
        "token": "your_jwt_token_here"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Chat with token in body:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def chat_with_fallback():
    """Example: Chat with user_id fallback (old method)"""
    url = "http://129.212.140.152:8001/agent/chat"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "message": "صباح الخير",
        "session_id": 123,
        "context": {
            "user_id": 5
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Chat with user_id fallback:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def verify_token():
    """Example: Verify token"""
    url = "http://129.212.140.152:8001/agent/verify-token"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "token": "your_jwt_token_here"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Token verification:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def check_availability_with_token():
    """Example: Check availability with token"""
    url = "http://129.212.140.152:8001/agent/check-availability"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_jwt_token_here"
    }
    
    data = {
        "medicine_name": "باراسيتامول"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Check availability with token:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def process_with_token():
    """Example: Process query with token"""
    url = "http://129.212.140.152:8001/agent/process"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_jwt_token_here"
    }
    
    data = {
        "query": "عايز 10 علب باراسيتامول",
        "session_id": "session_123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            result = response.json()
            print("Process with token:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Run all examples"""
    print("🚀 FastAPI AI Agent Token Authentication Examples\n")
    
    print("=" * 50)
    await chat_with_token()
    
    print("\n" + "=" * 50)
    await chat_with_token_in_body()
    
    print("\n" + "=" * 50)
    await chat_with_fallback()
    
    print("\n" + "=" * 50)
    await verify_token()
    
    print("\n" + "=" * 50)
    await check_availability_with_token()
    
    print("\n" + "=" * 50)
    await process_with_token()


if __name__ == "__main__":
    asyncio.run(main())
