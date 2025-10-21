"""
MCP (Model Context Protocol) Service
Handles communication with Django backend API for executing actions
"""
import httpx
import logging
from config import settings
from typing import Dict, Any, List

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


async def close():
    """Close HTTP client"""
    await _client.aclose()

