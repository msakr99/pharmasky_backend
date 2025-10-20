"""
Security middleware for handling suspicious requests.
"""
import logging
from django.core.exceptions import DisallowedHost
from django.http import HttpResponseBadRequest

logger = logging.getLogger(__name__)


class SuspiciousRequestMiddleware:
    """
    Middleware to handle suspicious requests and common attack patterns.
    Silently blocks common attack vectors without cluttering logs.
    """
    
    SUSPICIOUS_PATHS = [
        '/.env',
        '/admin.php',
        '/wp-admin',
        '/phpMyAdmin',
        '/config.php',
        '/.git/',
        '/api-docs',
        '/swagger',
        '/.aws/',
    ]
    
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap',
        'nikto',
        'nmap',
        'masscan',
        'ZmEu',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for suspicious paths
        if any(request.path.startswith(path) for path in self.SUSPICIOUS_PATHS):
            logger.warning(
                f"Blocked suspicious request: {request.path} from {self.get_client_ip(request)}"
            )
            return HttpResponseBadRequest("Bad Request")
        
        # Check for suspicious user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(agent in user_agent for agent in self.SUSPICIOUS_USER_AGENTS):
            logger.warning(
                f"Blocked suspicious user agent: {user_agent[:100]} from {self.get_client_ip(request)}"
            )
            return HttpResponseBadRequest("Bad Request")

        try:
            response = self.get_response(request)
            return response
        except DisallowedHost as e:
            # Log suspicious host but don't clutter logs with full traceback
            logger.warning(
                f"DisallowedHost attempt: {request.META.get('HTTP_HOST')} "
                f"from {self.get_client_ip(request)}"
            )
            return HttpResponseBadRequest("Invalid Host")

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

