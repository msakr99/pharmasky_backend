"""
Search Performance Middleware
Logs search query performance and timing for optimization
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SearchPerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to track search performance
    """
    
    def process_request(self, request):
        # Start timing for search requests
        if self._is_search_request(request):
            request._search_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Log search performance
        if hasattr(request, '_search_start_time'):
            duration = time.time() - request._search_start_time
            search_query = request.GET.get('q') or request.GET.get('search')
            
            logger.info(
                f"Search Performance - Query: '{search_query}', "
                f"Duration: {duration:.3f}s, "
                f"Path: {request.path}, "
                f"Status: {response.status_code}"
            )
            
            # Log slow queries (>1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow Search Query - Query: '{search_query}', "
                    f"Duration: {duration:.3f}s, "
                    f"Path: {request.path}"
                )
            
            # Save to SearchLog for analytics
            if search_query and response.status_code == 200:
                try:
                    from core.models import SearchLog
                    import json
                    
                    # Extract results count from response
                    results_count = 0
                    try:
                        if hasattr(response, 'data'):
                            results_count = response.data.get('count', 0)
                        elif response.content:
                            content = json.loads(response.content.decode('utf-8'))
                            results_count = content.get('count', 0)
                    except:
                        pass
                    
                    # Determine search type and mode
                    search_type = 'product' if '/products/' in request.path else 'offer'
                    search_mode = request.GET.get('search_mode', 'hybrid' if request.GET.get('q') else 'legacy')
                    min_similarity = request.GET.get('min_similarity')
                    
                    # Create log entry
                    SearchLog.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        query=search_query,
                        search_mode=search_mode,
                        search_type=search_type,
                        results_count=results_count,
                        response_time=duration,
                        min_similarity=float(min_similarity) if min_similarity else None,
                        user_role=getattr(request.user, 'role', '') if request.user.is_authenticated else ''
                    )
                except Exception as e:
                    logger.error(f"Failed to save search log: {e}")
        
        return response
    
    def _is_search_request(self, request):
        """
        Check if this is a search request
        """
        return (
            request.path.endswith('/products/') and 
            (request.GET.get('q') or request.GET.get('search'))
        )
