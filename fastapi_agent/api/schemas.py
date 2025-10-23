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


# Chat Schemas (from ai_agent)
class ChatRequest(BaseModel):
    """Request for chat API"""
    message: str = Field(..., description="User message", max_length=5000)
    session_id: Optional[int] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="User context")
    token: Optional[str] = Field(None, description="Authentication token")


class ChatResponse(BaseModel):
    """Response from chat API"""
    message: str
    session_id: int


class VoiceRequest(BaseModel):
    """Request for voice API"""
    audio_base64: str = Field(..., description="Base64 encoded audio")
    session_id: Optional[int] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="User context")
    token: Optional[str] = Field(None, description="Authentication token")


class VoiceResponse(BaseModel):
    """Response from voice API"""
    text: str
    audio_base64: str
    session_id: int
    transcription: str


class CallRequest(BaseModel):
    """Request for call API (streaming)"""
    audio_chunk_base64: str = Field(..., description="Base64 encoded audio chunk")
    session_id: Optional[int] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="User context")
    token: Optional[str] = Field(None, description="Authentication token")


class CallResponse(BaseModel):
    """Response from call API"""
    audio_response_base64: str
    text_response: str
    is_final: bool = False


# Session Management
class ChatSession(BaseModel):
    """Chat session model"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    messages: List[Dict[str, Any]] = []


class ChatMessage(BaseModel):
    """Chat message model"""
    id: int
    role: str  # user, assistant, system
    content: str
    created_at: datetime
    function_name: Optional[str] = None
    function_arguments: Optional[Dict[str, Any]] = None
    function_response: Optional[Dict[str, Any]] = None


# Voice Call Models
class VoiceCall(BaseModel):
    """Voice call model"""
    id: int
    pharmacy_id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: str
    status: str  # active, completed, failed, cancelled
    duration: int = 0
    created_at: datetime
    ended_at: Optional[datetime] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CallTranscript(BaseModel):
    """Call transcript model"""
    id: int
    call_id: int
    speaker: str  # user, assistant, system
    text: str
    timestamp: float
    created_at: datetime


class CallAction(BaseModel):
    """Call action model"""
    id: int
    call_id: int
    action_type: str
    parameters: Dict[str, Any] = {}
    result: Dict[str, Any] = {}
    status: str  # pending, success, failed
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# Agent Processing Schemas
class AgentRequest(BaseModel):
    """Request to process text query"""
    query: str = Field(..., description="User query text")
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    token: Optional[str] = Field(None, description="Authentication token")


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


# Token Authentication Schemas
class TokenRequest(BaseModel):
    """Request with token authentication"""
    token: str = Field(..., description="Authentication token")


class TokenResponse(BaseModel):
    """Response from token validation"""
    valid: bool
    user_id: Optional[int] = None
    user_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime

