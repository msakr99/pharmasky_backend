"""
URL Configuration for AI Agent app
"""
from django.urls import path
from ai_agent.views import (
    ChatAPIView,
    VoiceAPIView,
    CallAPIView,
    SessionHistoryAPIView
)

app_name = 'ai_agent'

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('voice/', VoiceAPIView.as_view(), name='voice'),
    path('call/', CallAPIView.as_view(), name='call'),
    path('session/<int:session_id>/', SessionHistoryAPIView.as_view(), name='session-history'),
]

