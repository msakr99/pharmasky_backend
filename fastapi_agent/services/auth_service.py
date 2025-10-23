"""
Authentication service for token-based authentication
"""
import httpx
import logging
from config import settings
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# HTTP client for Django API
_auth_client = httpx.AsyncClient(
    base_url=settings.DJANGO_API_URL,
    headers={
        'Content-Type': 'application/json'
    },
    timeout=30.0
)


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify token with Django backend and get user info
    
    Args:
        token: JWT token or API token
        
    Returns:
        Dict with user info and validation status
    """
    try:
        logger.info(f"Verifying token: {token[:10]}...")
        
        # Try to verify token with Django backend
        response = await _auth_client.post(
            "/api/auth/verify-token/",
            json={"token": token}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Token verified for user: {data.get('user_id')}")
            return {
                'valid': True,
                'user_id': data.get('user_id'),
                'user_info': data.get('user_info', {}),
                'permissions': data.get('permissions', [])
            }
        else:
            logger.warning(f"Token verification failed: {response.status_code}")
            return {
                'valid': False,
                'error': 'Invalid token'
            }
    
    except httpx.RequestError as e:
        logger.error(f"Token verification request failed: {str(e)}")
        return {
            'valid': False,
            'error': 'Authentication service unavailable'
        }
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return {
            'valid': False,
            'error': 'Token verification failed'
        }


async def get_user_from_token(token: str) -> Optional[int]:
    """
    Get user_id from token
    
    Args:
        token: JWT token or API token
        
    Returns:
        user_id if valid, None if invalid
    """
    try:
        result = await verify_token(token)
        if result.get('valid'):
            return result.get('user_id')
        return None
    except Exception as e:
        logger.error(f"Get user from token error: {str(e)}")
        return None


async def validate_token_for_agent(token: str) -> Dict[str, Any]:
    """
    Validate token specifically for agent operations
    
    Args:
        token: JWT token or API token
        
    Returns:
        Dict with validation result and user info
    """
    try:
        # First verify the token
        token_result = await verify_token(token)
        
        if not token_result.get('valid'):
            return {
                'success': False,
                'error': token_result.get('error', 'Invalid token'),
                'user_id': None
            }
        
        user_id = token_result.get('user_id')
        if not user_id:
            return {
                'success': False,
                'error': 'User ID not found in token',
                'user_id': None
            }
        
        logger.info(f"Token validated for agent operations: user_id={user_id}")
        return {
            'success': True,
            'user_id': user_id,
            'user_info': token_result.get('user_info', {}),
            'permissions': token_result.get('permissions', [])
        }
    
    except Exception as e:
        logger.error(f"Token validation for agent error: {str(e)}")
        return {
            'success': False,
            'error': f'Token validation failed: {str(e)}',
            'user_id': None
        }


async def close():
    """Close HTTP client"""
    await _auth_client.aclose()
