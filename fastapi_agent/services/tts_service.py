"""
Text-to-Speech Service using gTTS
"""
from gtts import gTTS
import io
import logging
import base64
from config import settings

logger = logging.getLogger(__name__)


def text_to_speech(text: str, language: str = "ar", slow: bool = False) -> dict:
    """
    Convert text to speech audio
    
    Args:
        text: Text to convert
        language: Language code (ar, en, etc.)
        slow: Speak slowly
    
    Returns:
        Dict with 'success', 'audio_bytes', 'audio_base64'
    """
    try:
        logger.info(f"Generating TTS for text ({len(text)} chars) in {language}")
        
        # Create gTTS object
        tts = gTTS(text=text, lang=language, slow=slow)
        
        # Save to BytesIO
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        audio_bytes = audio_fp.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        logger.info(f"TTS generated successfully ({len(audio_bytes)} bytes)")
        
        return {
            'success': True,
            'audio_bytes': audio_bytes,
            'audio_base64': audio_base64
        }
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


async def text_to_speech_async(text: str, language: str = "ar", slow: bool = False) -> dict:
    """
    Async version of text_to_speech
    
    Note: gTTS is synchronous, but we wrap it for async context
    In production, consider using an async TTS service
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, text_to_speech, text, language, slow)

