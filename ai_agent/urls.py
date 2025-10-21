"""
URL Configuration for AI Agent app
"""
from django.urls import path
from ai_agent.views import (
    ChatAPIView,
    VoiceAPIView,
    CallAPIView,
    SessionHistoryAPIView,
    CallListAPIView,
    CallDetailAPIView,
    CallAudioAPIView
)

app_name = 'ai_agent'

urlpatterns = [
    # Chat endpoints
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('voice/', VoiceAPIView.as_view(), name='voice'),
    path('call/', CallAPIView.as_view(), name='call'),
    path('session/<int:session_id>/', SessionHistoryAPIView.as_view(), name='session-history'),
    
    # Voice call endpoints
    path('calls/', CallListAPIView.as_view(), name='call-list'),
    path('calls/<int:call_id>/', CallDetailAPIView.as_view(), name='call-detail'),
    path('calls/<int:call_id>/audio/', CallAudioAPIView.as_view(), name='call-audio'),
]

