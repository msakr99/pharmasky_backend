"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from config import settings
from api.schemas import HealthResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service is running
    """
    services = {
        "whisper": "ok",
        "ollama": "ok",
        "chromadb": "ok",
        "database": "ok"
    }
    
    # TODO: Actually check service health
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        services=services,
        timestamp=datetime.utcnow()
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Docker orchestration
    """
    # TODO: Check if all services are ready
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Docker orchestration
    """
    return {"status": "alive"}

