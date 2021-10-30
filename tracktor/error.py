"""
Module that contains all possible Exceptions
"""
from typing import Optional, Dict, Any

from fastapi import HTTPException, status


class DatabaseConstructionError(Exception):
    """
    Error if no Database url can not be build
    """

    def __init__(self, message=""):
        self.message = message
        super().__init__()


class ApiError(HTTPException):
    """
    Base exception for all exceptions which could occur in the routers
    """

    def __init__(
        self,
        message: Optional[str] = None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=message if message else "Internal Server Error",
            headers=headers,
        )


class BadRequestException(ApiError):
    """
    400 Bad Request Response
    """

    def __init__(
        self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message if message else "Bad Request",
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers,
        )


class UnauthorizedException(ApiError):
    """
    401 Unauthorized Response
    """

    def __init__(
        self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message if message else "Unauthorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=headers,
        )


class ForbiddenException(ApiError):
    """
    403 Forbidden Response
    """

    def __init__(
        self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message if message else "Forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
            headers=headers,
        )


class ItemNotFoundException(ApiError):
    """
    404 Not Found Response
    """

    def __init__(
        self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message if message else "Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
            headers=headers,
        )


class ItemConflictException(ApiError):
    """
    409 Conflict Response
    """

    def __init__(
        self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message if message else "Conflict",
            status_code=status.HTTP_409_CONFLICT,
            headers=headers,
        )
