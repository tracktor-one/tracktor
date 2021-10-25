from typing import Optional, Dict, Any

from fastapi import HTTPException


class ApiError(HTTPException):
    """
    Base exception for all exceptions which could occur in the api
    """

    def __init__(self, message: Optional[str] = None, status_code=500, headers: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=message if message else "Internal Server Error",
                         headers=headers)


class ItemNotFound(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Item not found", status_code=404, headers=headers)


class ItemConflict(ApiError):
    def __init__(self, message: Optional[str] = None, headers: Optional[Dict[str, Any]] = None):
        super().__init__(message=message if message else "Conflict", status_code=409, headers=headers)
