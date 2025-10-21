"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# STT Schemas
class TranscribeRequest(BaseModel):
    """Request to transcribe audio"""
    audio_base64: str = Field(..., description="Base64 encoded audio file")
    language: str = Field(default="ar", description="Language code (ar, en, etc)")


class TranscribeResponse(BaseModel):
    """Response from transcription"""
    success: bool
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


# Agent Processing Schemas
class AgentRequest(BaseModel):
    """Request to process text query"""
    query: str = Field(..., description="User query text")
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response from agent processing"""
    success: bool
    response: str
    actions: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Call Schemas
class StartCallRequest(BaseModel):
    """Request to start a call"""
    pharmacy_id: Optional[int] = None
    user_id: Optional[int] = None


class StartCallResponse(BaseModel):
    """Response when starting a call"""
    session_id: str
    status: str
    websocket_url: str


class EndCallRequest(BaseModel):
    """Request to end a call"""
    session_id: str


class EndCallResponse(BaseModel):
    """Response when ending a call"""
    session_id: str
    duration: int
    transcript_count: int
    actions_count: int
    summary: Optional[str] = None


class CallDetailResponse(BaseModel):
    """Detailed call information"""
    session_id: str
    pharmacy_id: Optional[int] = None
    user_id: Optional[int] = None
    status: str
    duration: int
    created_at: datetime
    ended_at: Optional[datetime] = None
    transcripts: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    summary: Optional[str] = None


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime

