"""
API response format definitions.

This module provides standardized response formats for FastAPI endpoints.
"""

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """Standard API response format for successful operations.
    
    This is a simple response model that can be used for basic
    API responses.
    
    Attributes:
        message: Human-readable message describing the response
        data: Response payload as a dictionary
    """

    message: str = Field(..., description="Response message")
    data: dict = Field(..., description="Response data payload")
