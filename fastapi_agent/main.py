"""
FastAPI AI Sales Agent Service - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from api.routes import calls, agent, stt, health
from services import stt_service, rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting AI Sales Agent Service...")
    
    try:
        # Initialize Whisper model
        logger.info("Loading Whisper STT model...")
        stt_service.initialize()
        logger.info("✓ Whisper model loaded")
        
        # Initialize RAG service
        logger.info("Initializing RAG service...")
        await rag_service.initialize()
        logger.info("✓ RAG service initialized")
        
        logger.info("✅ Service started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Sales Agent Service...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(stt.router, prefix="/stt", tags=["Speech-to-Text"])
app.include_router(agent.router, prefix="/agent", tags=["AI Agent"])
app.include_router(calls.router, prefix="/calls", tags=["Voice Calls"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )

