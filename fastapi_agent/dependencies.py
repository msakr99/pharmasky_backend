"""
FastAPI dependencies for dependency injection
"""
from fastapi import Header, HTTPException, status
from config import settings
from typing import Optional


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """
    Verify API key from Django or other clients
    This is a simple auth mechanism for service-to-service communication
    """
    if x_api_key != settings.DJANGO_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True

