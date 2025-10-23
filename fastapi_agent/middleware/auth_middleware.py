"""
Authentication middleware for token-based authentication
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from services import auth_service

logger = logging.getLogger(__name__)


async def token_auth_middleware(request: Request, call_next):
    """
    Middleware to validate tokens for protected endpoints
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler
        
    Returns:
        Response with user_id added to request state
    """
    # Skip auth for certain endpoints
    skip_auth_paths = [
        "/health",
        "/docs",
        "/openapi.json",
        "/agent/verify-token",
        "/agent/test-chat",
        "/agent/smart-chat"
    ]
    
    # Check if this is a skip path
    logger.info(f"Checking auth for path: {request.url.path}")
    if any(request.url.path.startswith(path) for path in skip_auth_paths):
        logger.info(f"Skipping auth for path: {request.url.path}")
        return await call_next(request)
    
    try:
        # Get token from Authorization header or request body
        token = None
        
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        # If no token in header, try to get from request body for POST requests
        body = None
        if not token and request.method == "POST":
            try:
                # Read request body
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)
                    token = data.get("token")
            except:
                pass  # Ignore JSON parsing errors
        
        # If no token found, check if endpoint requires auth
        if not token:
            # For agent endpoints, require authentication
            if request.url.path.startswith("/agent/"):
                # Check if there's user_id in context as fallback
                if body:
                    try:
                        import json
                        data = json.loads(body)
                        user_id = data.get('context', {}).get('user_id')
                        if user_id:
                            logger.info(f"Using user_id fallback: {user_id}")
                            request.state.user_id = user_id
                            request.state.user_info = {'username': f'user_{user_id}'}
                            request.state.permissions = ['chat', 'voice', 'call', 'process']
                            return await call_next(request)
                    except:
                        pass
                
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Authentication required",
                        "error": "Missing token"
                    }
                )
            else:
                # For other endpoints, continue without auth
                return await call_next(request)
        
        # Validate token
        auth_result = await auth_service.validate_token_for_agent(token)
        
        if not auth_result.get('success'):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Authentication failed",
                    "error": auth_result.get('error', 'Invalid token')
                }
            )
        
        # Add user info to request state
        request.state.user_id = auth_result.get('user_id')
        request.state.user_info = auth_result.get('user_info', {})
        request.state.permissions = auth_result.get('permissions', [])
        request.state.token = token
        
        logger.info(f"Authenticated user: {request.state.user_id}")
        
        return await call_next(request)
    
    except Exception as e:
        logger.error(f"Auth middleware error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Authentication service error",
                "error": str(e)
            }
        )


def get_current_user(request: Request) -> dict:
    """
    Get current user info from request state
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict with user info
        
    Raises:
        HTTPException: If user not authenticated
    """
    if not hasattr(request.state, 'user_id') or not request.state.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    return {
        'user_id': request.state.user_id,
        'user_info': getattr(request.state, 'user_info', {}),
        'permissions': getattr(request.state, 'permissions', []),
        'token': getattr(request.state, 'token', None)
    }
