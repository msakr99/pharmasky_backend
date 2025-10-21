"""
Speech-to-Text Service using Whisper
"""
import whisper
import io
import logging
from config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Global Whisper model
_model = None


def initialize():
    """Load Whisper model on startup"""
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        _model = whisper.load_model(settings.WHISPER_MODEL)
        logger.info("Whisper model loaded successfully")


def transcribe(audio_bytes: bytes, language: str = "ar") -> Dict[str, Any]:
    """
    Transcribe audio bytes to text
    
    Args:
        audio_bytes: Audio file bytes
        language: Language code (ar, en, etc.)
    
    Returns:
        Dict with 'text', 'language', 'duration'
    """
    global _model
    
    if _model is None:
        initialize()
    
    try:
        # Save bytes to temporary file-like object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"  # Whisper needs a name
        
        # Transcribe
        logger.info(f"Transcribing audio ({len(audio_bytes)} bytes) in language: {language}")
        result = _model.transcribe(
            audio_file,
            language=language,
            fp16=False  # Use FP32 for CPU compatibility
        )
        
        text = result['text'].strip()
        detected_language = result.get('language', language)
        
        logger.info(f"Transcription complete: '{text[:100]}...'")
        
        return {
            'success': True,
            'text': text,
            'language': detected_language,
            'duration': None  # Whisper doesn't return duration
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }


def transcribe_stream(audio_stream, language: str = "ar"):
    """
    Transcribe streaming audio (for real-time processing)
    
    Note: Whisper is not optimized for streaming, consider using
    a streaming STT service for production
    """
    # TODO: Implement streaming transcription
    # This would require buffering and processing chunks
    pass

