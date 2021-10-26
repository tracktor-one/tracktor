from typing import Optional, Dict, Any

from fastapi import HTTPException, status


class ApiError(HTTPException):
    """
    Base exception for all exceptions which could occur in the routers
    """

    def __init__(self, message: Optional[str] = None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 headers: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=message if message else "Internal Server Error",
                         headers=headers)


class ItemNotFoundException(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Item not found", status_code=status.HTTP_404_NOT_FOUND,
                         headers=headers)


class ItemConflictException(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Conflict", status_code=status.HTTP_409_CONFLICT,
                         headers=headers)


class BadRequestException(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Bad Request", status_code=status.HTTP_400_BAD_REQUEST,
                         headers=headers)


class UnauthorizedException(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED,
                         headers=headers)


class ForbiddenException(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Forbidden", status_code=status.HTTP_403_FORBIDDEN,
                         headers=headers)
