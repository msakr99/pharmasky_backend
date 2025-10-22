"""
AI Agent processing endpoints
Includes all functions from ai_agent Django app
"""
from fastapi import APIRouter, HTTPException, Depends
from api.schemas import (
    AgentRequest, AgentResponse, ChatRequest, ChatResponse,
    VoiceRequest, VoiceResponse, CallRequest, CallResponse
)
from services import llm_service, rag_service, mcp_service
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=AgentResponse)
async def process_query(request: AgentRequest):
    """
    Process a text query through the AI agent with function calling
    
    Steps:
    1. Extract intent and entities
    2. Execute appropriate functions via MCP
    3. Return response with actions
    
    POST /agent/process
    Body: {"query": "عايز 10 علب باراسيتامول", "session_id": "...", "context": {"user_id": 123}}
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Get user_id from context
        user_id = request.context.get('user_id') if request.context else None
        
        # Process with function calling
        result = await llm_service.process_with_functions(
            text=request.query,
            user_id=user_id,
            session_id=request.session_id
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Processing failed'))
        
        return AgentResponse(
            success=True,
            response=result.get('response', ''),
            actions=[{
                'action': result.get('action', 'general_response'),
                'result': result.get('result', {})
            }],
            session_id=request.session_id,
            metadata=result.get('metadata', {})
        )
    
    except Exception as e:
        logger.error(f"Agent processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# Chat API endpoints (from ai_agent)
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Text-based chat with AI agent
    
    POST /agent/chat
    Body: {"message": "عايز باراسيتامول", "session_id": 123}
    """
    try:
        logger.info(f"Chat request: {request.message[:100]}...")
        
        # Send to Django backend via MCP
        result = await mcp_service.send_chat_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.context.get('user_id') if request.context else None
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('message', 'Chat failed'))
        
        return ChatResponse(
            message=result['message'],
            session_id=result['session_id']
        )
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/voice", response_model=VoiceResponse)
async def voice(request: VoiceRequest):
    """
    Voice-based interaction
    
    POST /agent/voice
    Body: {"audio_base64": "...", "session_id": 123}
    """
    try:
        logger.info(f"Voice request: session_id={request.session_id}")
        
        # Process voice message via MCP
        result = await mcp_service.process_voice_message(
            audio_base64=request.audio_base64,
            session_id=request.session_id,
            user_id=request.context.get('user_id') if request.context else None
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('message', 'Voice processing failed'))
        
        return VoiceResponse(
            text=result['text'],
            audio_base64=result['audio_base64'],
            session_id=result['session_id'],
            transcription=result['transcription']
        )
    
    except Exception as e:
        logger.error(f"Voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")


@router.post("/call", response_model=CallResponse)
async def call(request: CallRequest):
    """
    Real-time voice call simulation
    
    POST /agent/call
    Body: {"audio_chunk_base64": "...", "session_id": 123}
    """
    try:
        logger.info(f"Call request: session_id={request.session_id}")
        
        # Process call chunk via MCP
        result = await mcp_service.process_call_chunk(
            audio_chunk_base64=request.audio_chunk_base64,
            session_id=request.session_id,
            user_id=request.context.get('user_id') if request.context else None
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('message', 'Call processing failed'))
        
        return CallResponse(
            audio_response_base64=result['audio_response_base64'],
            text_response=result['text_response'],
            is_final=result['is_final']
        )
    
    except Exception as e:
        logger.error(f"Call error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Call processing failed: {str(e)}")


# AI Agent Function endpoints
@router.post("/check-availability")
async def check_availability(request: dict):
    """
    Check if a medicine is available in Max offers
    """
    try:
        medicine_name = request.get('medicine_name')
        user_id = request.get('user_id')
        result = await mcp_service.check_availability(medicine_name, user_id)
        return result
    except Exception as e:
        logger.error(f"Check availability error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Check availability failed: {str(e)}")


@router.post("/suggest-alternative")
async def suggest_alternative(request: dict):
    """
    Suggest alternative medicines
    """
    try:
        medicine_name = request.get('medicine_name')
        result = await mcp_service.suggest_alternative(medicine_name)
        return result
    except Exception as e:
        logger.error(f"Suggest alternative error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggest alternative failed: {str(e)}")


@router.post("/create-order")
async def create_order(request: dict):
    """
    Create a new order
    """
    try:
        medicine_name = request.get('medicine_name')
        quantity = request.get('quantity')
        user_id = request.get('user_id')
        result = await mcp_service.create_order(medicine_name, quantity, user_id)
        return result
    except Exception as e:
        logger.error(f"Create order error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Create order failed: {str(e)}")


@router.post("/track-order")
async def track_order(request: dict):
    """
    Track an existing order
    """
    try:
        order_id = request.get('order_id')
        user_id = request.get('user_id')
        result = await mcp_service.track_order(order_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Track order error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Track order failed: {str(e)}")


@router.post("/cancel-order")
async def cancel_order(request: dict):
    """
    Cancel an existing order
    """
    try:
        order_id = request.get('order_id')
        user_id = request.get('user_id')
        result = await mcp_service.cancel_order(order_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Cancel order error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cancel order failed: {str(e)}")


@router.post("/submit-complaint")
async def submit_complaint(request: dict):
    """
    Submit a complaint
    """
    try:
        subject = request.get('subject')
        body = request.get('body')
        user_id = request.get('user_id')
        result = await mcp_service.submit_complaint(subject, body, user_id)
        return result
    except Exception as e:
        logger.error(f"Submit complaint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Submit complaint failed: {str(e)}")


@router.get("/get-wishlist/{user_id}")
async def get_wishlist(user_id: int):
    """
    Get user's wishlist
    """
    try:
        result = await mcp_service.get_wishlist(user_id)
        return result
    except Exception as e:
        logger.error(f"Get wishlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get wishlist failed: {str(e)}")


@router.post("/add-to-wishlist")
async def add_to_wishlist(request: dict):
    """
    Add product to wishlist
    """
    try:
        product_name = request.get('product_name')
        user_id = request.get('user_id')
        result = await mcp_service.add_to_wishlist(product_name, user_id)
        return result
    except Exception as e:
        logger.error(f"Add to wishlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Add to wishlist failed: {str(e)}")


@router.get("/get-order-total/{user_id}")
async def get_order_total(user_id: int):
    """
    Get order total for user
    """
    try:
        result = await mcp_service.get_order_total(user_id)
        return result
    except Exception as e:
        logger.error(f"Get order total error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get order total failed: {str(e)}")


@router.get("/rag/query")
async def test_rag_query(q: str, top_k: int = 5):
    """
    Test RAG query directly
    
    GET /agent/rag/query?q=باراسيتامول&top_k=5
    """
    try:
        result = await rag_service.query(q, top_k=top_k)
        return result
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

