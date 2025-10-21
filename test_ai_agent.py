"""
Test script for AI Agent Service
Tests STT, RAG, MCP, and full conversation flow
"""
import requests
import json
import base64
import time
from pathlib import Path

# Configuration
DJANGO_API_URL = "http://localhost:8000"
FASTAPI_URL = "http://localhost:8001"
API_KEY = "change-this-in-production"  # Match with your config

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    
    try:
        response = requests.get(f"{FASTAPI_URL}/health/")
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ FastAPI Service: {data['status']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Services: {json.dumps(data['services'], indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


def test_rag_query():
    """Test RAG query directly"""
    print_section("2. RAG Query Test")
    
    queries = [
        "باراسيتامول",
        "أدوية البرد",
        "مضاد حيوي"
    ]
    
    for query in queries:
        try:
            print(f"Querying: '{query}'")
            response = requests.get(
                f"{FASTAPI_URL}/agent/rag/query",
                params={"q": query, "top_k": 3}
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Found {data.get('count', 0)} results")
            if data.get('results'):
                for i, result in enumerate(data['results'][:2], 1):
                    print(f"  {i}. {result.get('metadata', {}).get('name', 'N/A')}")
            print()
        except Exception as e:
            print(f"✗ RAG query failed: {str(e)}\n")


def test_django_drug_search():
    """Test Django drug search API"""
    print_section("3. Django Drug Search API")
    
    try:
        response = requests.get(
            f"{DJANGO_API_URL}/market/ai/drugs/search/",
            params={"q": "باراسيتامول", "limit": 5},
            headers={"X-API-Key": API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Found {data.get('count', 0)} drugs")
        for drug in data.get('results', [])[:3]:
            print(f"  - {drug['name']} ({drug['company']}) - {drug['public_price']} جنيه")
        print()
        return True
    except Exception as e:
        print(f"✗ Drug search failed: {str(e)}\n")
        return False


def test_agent_processing():
    """Test agent text processing"""
    print_section("4. Agent Text Processing")
    
    queries = [
        "عايز معلومات عن باراسيتامول",
        "فيه أدوية للبرد متوفرة؟",
        "أريد طلب 10 علب أسبرين"
    ]
    
    for query in queries:
        try:
            print(f"Query: '{query}'")
            response = requests.post(
                f"{FASTAPI_URL}/agent/process",
                json={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Response: {data.get('response', '')[:200]}...")
            print(f"  Actions: {len(data.get('actions', []))}")
            print()
        except Exception as e:
            print(f"✗ Agent processing failed: {str(e)}\n")


def test_stt_with_sample():
    """Test STT with a sample audio file"""
    print_section("5. Speech-to-Text Test")
    
    # Create a simple test audio message
    print("Note: This test requires a sample audio file.")
    print("To test STT, create an audio file and uncomment the code below.\n")
    
    # Uncomment and modify this code to test with your audio file:
    """
    audio_file_path = "test_audio.wav"
    
    if Path(audio_file_path).exists():
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post(
                f"{FASTAPI_URL}/stt/transcribe/file",
                files=files,
                data={'language': 'ar'}
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Transcription: {data.get('text')}")
    else:
        print("✗ Audio file not found")
    """
    print("Skipping STT test (no sample audio provided)")


def test_call_session():
    """Test call session management"""
    print_section("6. Call Session Management")
    
    try:
        # Start call
        print("Starting call session...")
        response = requests.post(
            f"{FASTAPI_URL}/calls/start",
            json={"pharmacy_id": 1, "user_id": 1}
        )
        response.raise_for_status()
        data = response.json()
        session_id = data['session_id']
        
        print(f"✓ Call started: {session_id}")
        print(f"  WebSocket URL: {data['websocket_url']}")
        
        # Wait a bit
        time.sleep(2)
        
        # Get call details
        print("\nGetting call details...")
        response = requests.get(f"{FASTAPI_URL}/calls/{session_id}")
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Call status: {data['status']}")
        print(f"  Duration: {data['duration']}s")
        
        # End call
        print("\nEnding call...")
        response = requests.post(
            f"{FASTAPI_URL}/calls/{session_id}/end",
            json={"session_id": session_id}
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Call ended")
        print(f"  Total duration: {data['duration']}s")
        print()
        
    except Exception as e:
        print(f"✗ Call session test failed: {str(e)}\n")


def test_mcp_integration():
    """Test MCP (Django API) integration"""
    print_section("7. MCP Integration Test")
    
    # This test requires the FastAPI service to be running
    # and properly configured to connect to Django
    
    try:
        print("Testing drug search via MCP...")
        response = requests.post(
            f"{FASTAPI_URL}/agent/process",
            json={
                "query": "ابحث عن باراسيتامول",
                "context": {"test": True}
            }
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ MCP integration working")
        print(f"  RAG results: {data.get('metadata', {}).get('rag_results_count', 0)}")
        print()
        
    except Exception as e:
        print(f"✗ MCP integration test failed: {str(e)}\n")


def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("AI Agent Service - Test Suite")
    print("🧪" * 30)
    
    print("\nMake sure services are running:")
    print("  - Django: http://localhost:8000")
    print("  - FastAPI: http://localhost:8001")
    print("  - Ollama: http://localhost:11434")
    
    input("\nPress Enter to start tests...")
    
    # Run tests
    test_health_check()
    test_rag_query()
    test_django_drug_search()
    test_agent_processing()
    test_stt_with_sample()
    test_call_session()
    test_mcp_integration()
    
    print_section("Test Summary")
    print("✓ All tests completed!")
    print("\nNext steps:")
    print("  1. Check the logs for any errors")
    print("  2. Test the WebRTC call interface in the dashboard")
    print("  3. Export RAG data: docker-compose exec web python manage.py export_rag_data")
    print("  4. Verify Ollama model: docker-compose exec ollama ollama list")
    print()


if __name__ == "__main__":
    main()

