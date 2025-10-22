"""
MCP (Model Context Protocol) Service
Handles communication with Django backend API for executing actions
Includes all functions from ai_agent Django app
"""
import httpx
import logging
from config import settings
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# HTTP client with timeout and retry
_client = httpx.AsyncClient(
    base_url=settings.DJANGO_API_URL,
    headers={
        'X-API-Key': settings.DJANGO_API_KEY,
        'Content-Type': 'application/json'
    },
    timeout=30.0
)


async def search_drugs(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for drugs in Django backend
    
    Args:
        query: Search query
        limit: Max results
    
    Returns:
        Dict with search results
    """
    try:
        logger.info(f"MCP: Searching drugs with query='{query}', limit={limit}")
        
        response = await _client.get(
            "/market/ai/drugs/search/",
            params={'q': query, 'limit': limit}
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Found {data.get('count', 0)} drugs")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP search_drugs error: {str(e)}")
        return {
            'success': False,
            'results': [],
            'error': str(e)
        }


async def check_stock(product_id: int, store_id: int = None) -> Dict[str, Any]:
    """
    Check stock availability for a product
    
    Args:
        product_id: Product ID
        store_id: Optional store ID
    
    Returns:
        Dict with stock information
    """
    try:
        logger.info(f"MCP: Checking stock for product_id={product_id}, store_id={store_id}")
        
        response = await _client.post(
            "/market/ai/drugs/stock/",
            json={
                'product_id': product_id,
                'store_id': store_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Stock check result: available={data.get('available')}, quantity={data.get('quantity')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP check_stock error: {str(e)}")
        return {
            'success': False,
            'available': False,
            'error': str(e)
        }


async def get_recommendations(product_id: int) -> Dict[str, Any]:
    """
    Get alternative/related products
    
    Args:
        product_id: Product ID
    
    Returns:
        Dict with recommendations
    """
    try:
        logger.info(f"MCP: Getting recommendations for product_id={product_id}")
        
        response = await _client.get(
            f"/market/ai/drugs/{product_id}/recommendations/"
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Found {data.get('count', 0)} recommendations")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP get_recommendations error: {str(e)}")
        return {
            'success': False,
            'recommendations': [],
            'error': str(e)
        }


async def create_order(pharmacy_id: int, items: List[Dict[str, int]], notes: str = "") -> Dict[str, Any]:
    """
    Create an order via Django API
    
    Args:
        pharmacy_id: Pharmacy ID
        items: List of items with product_id and quantity
        notes: Optional order notes
    
    Returns:
        Dict with order creation result
    """
    try:
        logger.info(f"MCP: Creating order for pharmacy_id={pharmacy_id}, items={len(items)}")
        
        response = await _client.post(
            "/market/ai/orders/create/",
            json={
                'pharmacy_id': pharmacy_id,
                'items': items,
                'notes': notes
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Order created: order_id={data.get('order_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP create_order error: {str(e)}")
        return {
            'success': False,
            'message': 'فشل إنشاء الطلب',
            'error': str(e)
        }


async def get_pharmacy_info(pharmacy_id: int) -> Dict[str, Any]:
    """
    Get pharmacy information
    
    Args:
        pharmacy_id: Pharmacy ID
    
    Returns:
        Dict with pharmacy details
    """
    try:
        logger.info(f"MCP: Getting pharmacy info for id={pharmacy_id}")
        
        response = await _client.get(
            f"/market/ai/pharmacies/{pharmacy_id}/"
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Got pharmacy info: {data.get('name')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP get_pharmacy_info error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# AI Agent Functions (from ai_agent Django app)
async def check_availability(medicine_name: str, user_id: int = None) -> Dict[str, Any]:
    """
    Check if a medicine/product is available in Max offers
    Returns: availability status, original price, and discount percentage
    """
    try:
        logger.info(f"MCP: Checking availability for '{medicine_name}', user_id={user_id}")
        
        response = await _client.post(
            "/ai-agent/check-availability/",
            json={
                'medicine_name': medicine_name,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Availability check result: {data.get('available')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP check_availability error: {str(e)}")
        return {
            'success': False,
            'available': False,
            'message': f"خطأ في التحقق من التوفر: {str(e)}",
            'offers': []
        }


async def suggest_alternative(medicine_name: str) -> Dict[str, Any]:
    """
    Suggest alternative medicines based on effective material
    """
    try:
        logger.info(f"MCP: Getting alternatives for '{medicine_name}'")
        
        response = await _client.post(
            "/ai-agent/suggest-alternative/",
            json={'medicine_name': medicine_name}
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Found {len(data.get('alternatives', []))} alternatives")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP suggest_alternative error: {str(e)}")
        return {
            'success': False,
            'found': False,
            'message': f"خطأ في البحث عن البدائل: {str(e)}",
            'alternatives': []
        }


async def create_order(medicine_name: str, quantity: int, user_id: int) -> Dict[str, Any]:
    """
    Create a sale order for a medicine with best available offer
    """
    try:
        logger.info(f"MCP: Creating order for '{medicine_name}', qty={quantity}, user_id={user_id}")
        
        response = await _client.post(
            "/ai-agent/create-order/",
            json={
                'medicine_name': medicine_name,
                'quantity': quantity,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Order created: order_id={data.get('order_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP create_order error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في إنشاء الطلب: {str(e)}",
            'order_id': None
        }


async def track_order(order_id: int, user_id: int) -> Dict[str, Any]:
    """
    Track an existing order
    """
    try:
        logger.info(f"MCP: Tracking order {order_id} for user {user_id}")
        
        response = await _client.post(
            "/ai-agent/track-order/",
            json={
                'order_id': order_id,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Order tracking result: found={data.get('found')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP track_order error: {str(e)}")
        return {
            'success': False,
            'found': False,
            'message': f"خطأ في تتبع الطلب: {str(e)}",
            'order': None
        }


async def cancel_order(order_id: int, user_id: int) -> Dict[str, Any]:
    """
    Cancel an existing order
    """
    try:
        logger.info(f"MCP: Cancelling order {order_id} for user {user_id}")
        
        response = await _client.post(
            "/ai-agent/cancel-order/",
            json={
                'order_id': order_id,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Order cancellation result: success={data.get('success')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP cancel_order error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في إلغاء الطلب: {str(e)}"
        }


async def submit_complaint(subject: str, body: str, user_id: int) -> Dict[str, Any]:
    """
    Submit a complaint from the user
    """
    try:
        logger.info(f"MCP: Submitting complaint from user {user_id}")
        
        response = await _client.post(
            "/ai-agent/submit-complaint/",
            json={
                'subject': subject,
                'body': body,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Complaint submitted: complaint_id={data.get('complaint_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP submit_complaint error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في تسجيل الشكوى: {str(e)}"
        }


async def get_wishlist(user_id: int) -> Dict[str, Any]:
    """
    Get user's wishlist products
    """
    try:
        logger.info(f"MCP: Getting wishlist for user {user_id}")
        
        response = await _client.get(
            f"/ai-agent/get-wishlist/{user_id}/"
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Found {data.get('count', 0)} wishlist items")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP get_wishlist error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في الحصول على قائمة المفضلة: {str(e)}",
            'wishlist': [],
            'count': 0
        }


async def add_to_wishlist(product_name: str, user_id: int) -> Dict[str, Any]:
    """
    Add a product to user's wishlist
    """
    try:
        logger.info(f"MCP: Adding '{product_name}' to wishlist for user {user_id}")
        
        response = await _client.post(
            "/ai-agent/add-to-wishlist/",
            json={
                'product_name': product_name,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Product added to wishlist: success={data.get('success')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP add_to_wishlist error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في إضافة المنتج للمفضلة: {str(e)}"
        }


async def get_order_total(user_id: int) -> Dict[str, Any]:
    """
    Calculate total of today's orders
    """
    try:
        logger.info(f"MCP: Getting order total for user {user_id}")
        
        response = await _client.get(
            f"/ai-agent/get-order-total/{user_id}/"
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Order total: {data.get('grand_total', 0)}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP get_order_total error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في حساب إجمالي الطلبات: {str(e)}",
            'grand_total': 0,
            'total_items': 0
        }


# Chat and Session Management
async def create_chat_session(user_id: int) -> Dict[str, Any]:
    """
    Create a new chat session
    """
    try:
        logger.info(f"MCP: Creating chat session for user {user_id}")
        
        response = await _client.post(
            "/ai-agent/chat/session/",
            json={'user_id': user_id}
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Chat session created: session_id={data.get('session_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP create_chat_session error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في إنشاء جلسة المحادثة: {str(e)}"
        }


async def get_chat_session(session_id: int, user_id: int) -> Dict[str, Any]:
    """
    Get chat session with messages
    """
    try:
        logger.info(f"MCP: Getting chat session {session_id} for user {user_id}")
        
        response = await _client.get(
            f"/ai-agent/chat/session/{session_id}/",
            params={'user_id': user_id}
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Chat session retrieved: {len(data.get('messages', []))} messages")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP get_chat_session error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في الحصول على جلسة المحادثة: {str(e)}"
        }


async def send_chat_message(message: str, session_id: int = None, user_id: int = None) -> Dict[str, Any]:
    """
    Send a chat message and get AI response
    """
    try:
        logger.info(f"MCP: Sending chat message, session_id={session_id}, user_id={user_id}")
        
        response = await _client.post(
            "/ai-agent/chat/",
            json={
                'message': message,
                'session_id': session_id,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Chat response received: session_id={data.get('session_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP send_chat_message error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في إرسال الرسالة: {str(e)}"
        }


async def process_voice_message(audio_base64: str, session_id: int = None, user_id: int = None) -> Dict[str, Any]:
    """
    Process voice message: transcribe -> chat -> TTS
    """
    try:
        logger.info(f"MCP: Processing voice message, session_id={session_id}, user_id={user_id}")
        
        response = await _client.post(
            "/ai-agent/voice/",
            json={
                'audio_base64': audio_base64,
                'session_id': session_id,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Voice message processed: session_id={data.get('session_id')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP process_voice_message error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في معالجة الرسالة الصوتية: {str(e)}"
        }


async def process_call_chunk(audio_chunk_base64: str, session_id: int = None, user_id: int = None) -> Dict[str, Any]:
    """
    Process real-time call audio chunk
    """
    try:
        logger.info(f"MCP: Processing call chunk, session_id={session_id}, user_id={user_id}")
        
        response = await _client.post(
            "/ai-agent/call/",
            json={
                'audio_chunk_base64': audio_chunk_base64,
                'session_id': session_id,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"MCP: Call chunk processed: is_final={data.get('is_final')}")
        
        return {
            'success': True,
            **data
        }
    
    except Exception as e:
        logger.error(f"MCP process_call_chunk error: {str(e)}")
        return {
            'success': False,
            'message': f"خطأ في معالجة المقطع الصوتي: {str(e)}"
        }


async def close():
    """Close HTTP client"""
    await _client.aclose()

