"""
Speech-to-Text API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from api.schemas import TranscribeRequest, TranscribeResponse
from services import stt_service
import base64
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio from base64 encoded data
    
    POST /stt/transcribe
    Body: {"audio_base64": "...", "language": "ar"}
    """
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64)
        
        # Transcribe
        result = stt_service.transcribe(audio_bytes, language=request.language)
        
        return TranscribeResponse(
            success=True,
            text=result.get('text', ''),
            language=result.get('language'),
            duration=result.get('duration')
        )
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/transcribe/file")
async def transcribe_file(audio: UploadFile = File(...), language: str = "ar"):
    """
    Transcribe audio from uploaded file
    
    POST /stt/transcribe/file
    Form data: audio (file), language (string)
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe
        result = stt_service.transcribe(audio_bytes, language=language)
        
        return TranscribeResponse(
            success=True,
            text=result.get('text', ''),
            language=result.get('language'),
            duration=result.get('duration')
        )
    
    except Exception as e:
        logger.error(f"File transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

