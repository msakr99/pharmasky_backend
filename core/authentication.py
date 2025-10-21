"""
API Key Authentication for AI Agent Service
"""
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
import secrets


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API Key authentication for service-to-service communication
    
    Usage:
    - Add 'X-API-Key' header with the API key
    - The API key is configured in settings.AI_AGENT_API_KEY
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None
        
        # Get the configured API key from settings
        configured_key = getattr(settings, 'AI_AGENT_API_KEY', None)
        
        if not configured_key:
            raise exceptions.AuthenticationFailed('API Key authentication not configured')
        
        if api_key != configured_key:
            raise exceptions.AuthenticationFailed('Invalid API Key')
        
        # Return a special user object for service-to-service auth
        # You can create a service user or use AnonymousUser
        return (AnonymousUser(), None)
    
    def authenticate_header(self, request):
        return 'X-API-Key'


def generate_api_key():
    """
    Generate a secure random API key
    Use this to generate keys for the .env file
    """
    return secrets.token_urlsafe(32)


# For initial setup, you can run this to generate a key:
# python -c "from core.authentication import generate_api_key; print(generate_api_key())"

