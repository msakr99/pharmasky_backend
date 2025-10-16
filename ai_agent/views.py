"""
API Views for AI Agent
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ai_agent.serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    VoiceRequestSerializer,
    VoiceResponseSerializer,
    CallRequestSerializer,
    CallResponseSerializer
)
from ai_agent.models import ChatSession
import base64
from io import BytesIO


class ChatAPIView(APIView):
    """
    API endpoint for text-based chat with AI agent
    
    POST /api/ai-agent/chat/
    Request: {"message": "text message", "session_id": 123 (optional)}
    Response: {"message": "AI response", "session_id": 123}
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Lazy import to avoid loading openai at startup
        from ai_agent.services import openai_service
        
        # Validate request
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "بيانات غير صحيحة", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        
        # Get session if provided
        session = None
        if session_id:
            session = ChatSession.objects.filter(
                id=session_id,
                user=request.user
            ).first()
        
        # Get AI response
        try:
            result = openai_service.chat(
                user=request.user,
                message_text=message,
                session=session
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceAPIView(APIView):
    """
    API endpoint for voice-based interaction
    
    POST /api/ai-agent/voice/
    Request: {"audio_base64": "base64 encoded audio", "session_id": 123 (optional)}
    Response: {
        "text": "AI text response",
        "audio_base64": "base64 encoded audio response",
        "session_id": 123,
        "transcription": "what user said"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Lazy import
        from ai_agent.services import openai_service
        
        # Validate request
        serializer = VoiceRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "بيانات غير صحيحة", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_base64 = serializer.validated_data['audio_base64']
        
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "audio.webm"  # Set a name for the file
            
            # Process voice message
            result = openai_service.process_voice_message(
                user=request.user,
                audio_file=audio_file
            )
            
            if not result.get("success"):
                return Response(
                    {"error": result.get("error", "حدث خطأ")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "text": result["text"],
                "audio_base64": result["audio_base64"],
                "session_id": result["session_id"],
                "transcription": result["transcription"]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CallAPIView(APIView):
    """
    API endpoint for real-time voice call simulation
    
    POST /api/ai-agent/call/
    Request: {"audio_chunk_base64": "base64 encoded audio chunk", "session_id": 123}
    Response: {
        "audio_response_base64": "base64 audio response",
        "text_response": "text response",
        "is_final": false
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Lazy import
        from ai_agent.services import openai_service
        
        # Validate request
        serializer = CallRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "بيانات غير صحيحة", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_chunk_base64 = serializer.validated_data['audio_chunk_base64']
        session_id = serializer.validated_data.get('session_id')
        
        try:
            # Get session
            session = None
            if session_id:
                session = ChatSession.objects.filter(
                    id=session_id,
                    user=request.user
                ).first()
            
            # Decode audio chunk
            audio_bytes = base64.b64decode(audio_chunk_base64)
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "chunk.webm"
            
            # Transcribe chunk
            transcription = openai_service.transcribe_audio(audio_file)
            
            if not transcription.get("success") or not transcription.get("text"):
                # No speech detected, return empty response
                return Response({
                    "audio_response_base64": "",
                    "text_response": "",
                    "is_final": False
                }, status=status.HTTP_200_OK)
            
            text = transcription["text"]
            
            # Get AI response
            chat_response = openai_service.chat(
                user=request.user,
                message_text=text,
                session=session
            )
            
            # Convert to speech
            tts_response = openai_service.text_to_speech(chat_response["message"])
            
            if not tts_response.get("success"):
                return Response(
                    {"error": "فشل تحويل النص إلى صوت"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "audio_response_base64": tts_response["audio_base64"],
                "text_response": chat_response["message"],
                "is_final": True,
                "session_id": chat_response["session_id"]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionHistoryAPIView(APIView):
    """
    Get chat session history
    
    GET /api/ai-agent/session/<session_id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id):
        try:
            session = ChatSession.objects.filter(
                id=session_id,
                user=request.user
            ).first()
            
            if not session:
                return Response(
                    {"error": "الجلسة غير موجودة"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            messages = session.messages.all().order_by('created_at')
            
            messages_data = []
            for msg in messages:
                messages_data.append({
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                })
            
            return Response({
                "session_id": session.id,
                "messages": messages_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

