"""
统一异常处理模块

提供统一的异常基类和常见异常类型。
"""

from faster_app.exceptions.base import FasterAppError
from faster_app.exceptions.types import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    TooManyRequestsError,
    UnauthorizedError,
    ValidationError,
)

__all__ = [
    "FasterAppError",
    "ValidationError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "TooManyRequestsError",
    "InternalServerError",
]
