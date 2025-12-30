"""
Standardized API response utility.

This module provides a consistent API response format for all endpoints,
including success, error, and paginated responses.
"""

from datetime import datetime
from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse


class ApiResponse:
    """Utility class for creating standardized API responses.

    Provides static methods to create consistent JSON responses for
    success, error, and paginated data scenarios.
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200,
        status_code: int = HTTPStatus.OK,
    ) -> JSONResponse:
        """
        Create a successful API response.

        Args:
            data: The response data (can be any JSON-serializable type)
            message: Success message (default: "操作成功")
            code: Business status code (default: 200)
            status_code: HTTP status code (default: 200 OK)

        Returns:
            JSONResponse with standardized success format

        Example:
            >>> ApiResponse.success(data={"user_id": 123}, message="User created")
        """
        response_data = {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        return JSONResponse(content=response_data, status_code=status_code)

    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 500,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_detail: str | None = None,
        data: Any = None,
    ) -> JSONResponse:
        """
        Create an error API response.

        Args:
            message: Error message (default: "操作失败")
            code: Business error code (default: 500)
            status_code: HTTP status code (default: 500 Internal Server Error)
            error_detail: Detailed error information (optional)
            data: Additional error data (optional)

        Returns:
            JSONResponse with standardized error format

        Note:
            Avoid including sensitive information in error_detail in production

        Example:
            >>> ApiResponse.error(
            ...     message="Validation failed",
            ...     code=400,
            ...     status_code=HTTPStatus.BAD_REQUEST
            ... )
        """
        response_data = {
            "success": False,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        # 如果有详细错误信息, 添加到响应中
        if error_detail:
            response_data["error_detail"] = error_detail

        return JSONResponse(content=response_data, status_code=status_code)

    @staticmethod
    def paginated(
        data: list[Any],
        total: int,
        page: int = 1,
        page_size: int = 10,
        message: str = "查询成功",
    ) -> JSONResponse:
        """
        Create a paginated API response.

        Args:
            data: List of items for the current page
            total: Total number of items across all pages
            page: Current page number (1-indexed, default: 1)
            page_size: Number of items per page (default: 10)
            message: Response message (default: "查询成功")

        Returns:
            JSONResponse with standardized pagination format including
            pagination metadata (total, page, page_size, total_pages, has_next, has_prev)

        Example:
            >>> ApiResponse.paginated(
            ...     data=[{"id": 1}, {"id": 2}],
            ...     total=50,
            ...     page=1,
            ...     page_size=10
            ... )
        """
        pagination_info = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_next": page * page_size < total,
            "has_prev": page > 1,
        }

        response_data = {
            "success": True,
            "code": 200,
            "message": message,
            "data": data,
            "pagination": pagination_info,
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(content=response_data, status_code=HTTPStatus.OK)
