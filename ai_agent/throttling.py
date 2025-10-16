"""
Rate limiting/throttling for AI Agent API
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AIAgentUserThrottle(UserRateThrottle):
    """
    Rate limiting for authenticated users
    - Limits AI Agent requests to prevent hitting OpenAI limits
    """
    scope = 'ai_agent_user'
    rate = '10/minute'  # 10 requests per minute per user


class AIAgentAnonThrottle(AnonRateThrottle):
    """
    Rate limiting for anonymous users (if any)
    """
    scope = 'ai_agent_anon'
    rate = '5/minute'  # 5 requests per minute for anonymous


class AIAgentBurstThrottle(UserRateThrottle):
    """
    Burst protection - prevents rapid consecutive requests
    """
    scope = 'ai_agent_burst'
    rate = '3/minute'  # Max 3 requests per minute for burst

