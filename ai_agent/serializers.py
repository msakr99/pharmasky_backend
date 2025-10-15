"""
Serializers for AI Agent API
"""
from rest_framework import serializers
from ai_agent.models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat API request"""
    message = serializers.CharField(required=True, max_length=5000)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat API response"""
    message = serializers.CharField()
    session_id = serializers.IntegerField()


class VoiceRequestSerializer(serializers.Serializer):
    """Serializer for voice API request"""
    audio_base64 = serializers.CharField(required=True)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class VoiceResponseSerializer(serializers.Serializer):
    """Serializer for voice API response"""
    text = serializers.CharField()
    audio_base64 = serializers.CharField()
    session_id = serializers.IntegerField()
    transcription = serializers.CharField()


class CallRequestSerializer(serializers.Serializer):
    """Serializer for call API request (streaming)"""
    audio_chunk_base64 = serializers.CharField(required=True)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class CallResponseSerializer(serializers.Serializer):
    """Serializer for call API response"""
    audio_response_base64 = serializers.CharField()
    text_response = serializers.CharField()
    is_final = serializers.BooleanField(default=False)

