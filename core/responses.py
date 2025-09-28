"""
Unified response structures for PharmaSky API.

This module provides standardized response formats for success and error cases,
ensuring consistency across the entire API.
"""

from typing import Any, Dict, Optional, List
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Standardized API response builder.
    
    Provides methods to create consistent response structures across the application.
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        Create a successful response.
        
        Args:
            data: Response data payload
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
            
        Returns:
            Response: Formatted success response
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response_data["meta"] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict[str, List[str]]] = None,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ) -> Response:
        """
        Create an error response.
        
        Args:
            message: Error message
            errors: Field-specific error details
            error_code: Application-specific error code
            status_code: HTTP status code
            data: Optional error data
            
        Returns:
            Response: Formatted error response
        """
        response_data = {
            "success": False,
            "message": message
        }
        
        if errors:
            response_data["errors"] = errors
            
        if error_code:
            response_data["error_code"] = error_code
            
        if data:
            response_data["data"] = data
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(
        errors: Dict[str, List[str]],
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR"
    ) -> Response:
        """
        Create a validation error response.
        
        Args:
            errors: Field validation errors
            message: Validation error message
            error_code: Error code
            
        Returns:
            Response: Formatted validation error response
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND"
    ) -> Response:
        """
        Create a not found error response.
        
        Args:
            message: Not found message
            error_code: Error code
            
        Returns:
            Response: Formatted not found response
        """
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        error_code: str = "UNAUTHORIZED"
    ) -> Response:
        """
        Create an unauthorized error response.
        
        Args:
            message: Unauthorized message
            error_code: Error code
            
        Returns:
            Response: Formatted unauthorized response
        """
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access denied",
        error_code: str = "FORBIDDEN"
    ) -> Response:
        """
        Create a forbidden error response.
        
        Args:
            message: Forbidden message
            error_code: Error code
            
        Returns:
            Response: Formatted forbidden response
        """
        return APIResponse.error(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> Response:
        """
        Create a resource created response.
        
        Args:
            data: Created resource data
            message: Success message
            
        Returns:
            Response: Formatted created response
        """
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def no_content(
        message: str = "Operation completed successfully"
    ) -> Response:
        """
        Create a no content response.
        
        Args:
            message: Success message
            
        Returns:
            Response: Formatted no content response
        """
        return APIResponse.success(
            message=message,
            status_code=status.HTTP_204_NO_CONTENT
        )


def paginated_response(
    data: List[Any],
    count: int,
    page_size: int,
    page: int,
    message: str = "Data retrieved successfully"
) -> Response:
    """
    Create a paginated response.
    
    Args:
        data: Paginated data
        count: Total count of items
        page_size: Items per page
        page: Current page number
        message: Success message
        
    Returns:
        Response: Formatted paginated response
    """
    meta = {
        "pagination": {
            "count": count,
            "page_size": page_size,
            "current_page": page,
            "total_pages": (count + page_size - 1) // page_size,
            "has_next": page * page_size < count,
            "has_previous": page > 1
        }
    }
    
    return APIResponse.success(
        data=data,
        message=message,
        meta=meta
    )

