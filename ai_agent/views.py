"""
API Views for AI Agent
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from ai_agent.serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    VoiceRequestSerializer,
    VoiceResponseSerializer,
    CallRequestSerializer,
    CallResponseSerializer
)
from ai_agent.models import ChatSession, VoiceCall, CallTranscript, CallAction
from ai_agent.throttling import AIAgentUserThrottle
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
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
    throttle_classes = [AIAgentUserThrottle]
    
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
    """API endpoint for voice-based interaction"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from ai_agent.services import openai_service
        
        serializer = VoiceRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "بيانات غير صحيحة", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_base64 = serializer.validated_data['audio_base64']
        
        try:
            audio_bytes = base64.b64decode(audio_base64)
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "audio.webm"
            
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
    """API endpoint for real-time voice call simulation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from ai_agent.services import openai_service
        
        serializer = CallRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "بيانات غير صحيحة", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_chunk_base64 = serializer.validated_data['audio_chunk_base64']
        session_id = serializer.validated_data.get('session_id')
        
        try:
            session = None
            if session_id:
                session = ChatSession.objects.filter(
                    id=session_id,
                    user=request.user
                ).first()
            
            audio_bytes = base64.b64decode(audio_chunk_base64)
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "chunk.webm"
            
            transcription = openai_service.transcribe_audio(audio_file)
            
            if not transcription.get("success") or not transcription.get("text"):
                return Response({
                    "audio_response_base64": "",
                    "text_response": "",
                    "is_final": False
                }, status=status.HTTP_200_OK)
            
            text = transcription["text"]
            chat_response = openai_service.chat(
                user=request.user,
                message_text=text,
                session=session
            )
            
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
    """Get chat session history"""
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
            messages_data = [{
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            } for msg in messages]
            
            return Response({
                "session_id": session.id,
                "messages": messages_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CallListAPIView(APIView):
    """List all voice calls"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            calls = VoiceCall.objects.select_related('pharmacy', 'user').all()
            
            status_filter = request.query_params.get('status')
            if status_filter:
                calls = calls.filter(status=status_filter)
            
            page_size = int(request.query_params.get('page_size', 20))
            page = int(request.query_params.get('page', 1))
            start = (page - 1) * page_size
            
            total = calls.count()
            calls_list = calls[start:start+page_size]
            
            data = [{
                'id': c.id,
                'session_id': c.session_id,
                'pharmacy': {'id': c.pharmacy.id, 'name': c.pharmacy.name} if c.pharmacy else None,
                'status': c.status,
                'duration': c.duration,
                'created_at': c.created_at.isoformat(),
                'actions_count': c.actions.count()
            } for c in calls_list]
            
            return Response({'results': data, 'count': total}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallDetailAPIView(APIView):
    """Get call details"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, call_id):
        try:
            call = get_object_or_404(VoiceCall, id=call_id)
            transcripts = [{'speaker': t.speaker, 'text': t.text, 'timestamp': t.timestamp} for t in call.transcripts.all()]
            actions = [{'action_type': a.action_type, 'status': a.status, 'result': a.result} for a in call.actions.all()]
            
            return Response({
                'id': call.id,
                'session_id': call.session_id,
                'status': call.status,
                'duration': call.duration,
                'transcripts': transcripts,
                'actions': actions
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallAudioAPIView(APIView):
    """Serve audio file"""
    permission_classes = [AllowAny]
    
    def get(self, request, call_id):
        try:
            call = get_object_or_404(VoiceCall, id=call_id)
            if not call.audio_file:
                return Response({"error": "لا يوجد ملف صوتي"}, status=status.HTTP_404_NOT_FOUND)
            return FileResponse(call.audio_file.open('rb'), content_type='audio/mpeg')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
