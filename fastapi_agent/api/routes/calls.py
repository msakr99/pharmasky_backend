"""
Voice call management endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from api.schemas import (
    StartCallRequest,
    StartCallResponse,
    EndCallRequest,
    EndCallResponse,
    CallDetailResponse
)
# from services import webrtc_service  # Disabled - using WebSocket instead
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory call sessions (replace with database in production)
active_calls = {}


@router.post("/start", response_model=StartCallResponse)
async def start_call(request: StartCallRequest):
    """
    Initialize a new voice call session
    
    POST /calls/start
    Body: {"pharmacy_id": 123, "user_id": 456}
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create call record
        active_calls[session_id] = {
            'session_id': session_id,
            'pharmacy_id': request.pharmacy_id,
            'user_id': request.user_id,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'transcripts': [],
            'actions': []
        }
        
        logger.info(f"Started call session: {session_id}")
        
        return StartCallResponse(
            session_id=session_id,
            status="active",
            websocket_url=f"ws://localhost:8001/calls/{session_id}/audio"
        )
    
    except Exception as e:
        logger.error(f"Error starting call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start call: {str(e)}")


@router.websocket("/{session_id}/audio")
async def websocket_audio(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time audio streaming
    
    WS /calls/{session_id}/audio
    
    Flow:
    1. Client sends audio chunks
    2. Server transcribes with Whisper
    3. Server processes with LLM + RAG
    4. Server generates TTS response
    5. Server sends audio response back
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")
    
    if session_id not in active_calls:
        await websocket.close(code=1008, reason="Invalid session ID")
        return
    
    try:
        while True:
            # Receive audio chunk from client
            data = await websocket.receive_bytes()
            logger.debug(f"Received audio chunk: {len(data)} bytes")
            
            # TODO: Process audio chunk
            # 1. Transcribe with Whisper
            # 2. Process with Agent
            # 3. Generate TTS response
            # 4. Send back to client
            
            # For now, send acknowledgment
            await websocket.send_json({
                "type": "ack",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))


@router.post("/{session_id}/end", response_model=EndCallResponse)
async def end_call(session_id: str, request: EndCallRequest):
    """
    End a voice call session
    
    POST /calls/{session_id}/end
    """
    if session_id not in active_calls:
        raise HTTPException(status_code=404, detail="Call session not found")
    
    call = active_calls[session_id]
    call['status'] = 'completed'
    call['ended_at'] = datetime.utcnow()
    
    duration = int((call['ended_at'] - call['created_at']).total_seconds())
    
    logger.info(f"Ended call session: {session_id}, duration: {duration}s")
    
    # TODO: Save to database, generate summary
    
    return EndCallResponse(
        session_id=session_id,
        duration=duration,
        transcript_count=len(call['transcripts']),
        actions_count=len(call['actions']),
        summary=None
    )


@router.get("/{session_id}", response_model=CallDetailResponse)
async def get_call_detail(session_id: str):
    """
    Get detailed information about a call
    
    GET /calls/{session_id}
    """
    if session_id not in active_calls:
        raise HTTPException(status_code=404, detail="Call session not found")
    
    call = active_calls[session_id]
    
    return CallDetailResponse(
        session_id=call['session_id'],
        pharmacy_id=call.get('pharmacy_id'),
        user_id=call.get('user_id'),
        status=call['status'],
        duration=int((
            (call.get('ended_at') or datetime.utcnow()) - call['created_at']
        ).total_seconds()),
        created_at=call['created_at'],
        ended_at=call.get('ended_at'),
        transcripts=call['transcripts'],
        actions=call['actions'],
        summary=call.get('summary')
    )

