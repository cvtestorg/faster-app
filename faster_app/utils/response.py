"""
Standardized API response utility.

This module provides a consistent API response format for all endpoints,
including success and error responses.
"""

from datetime import datetime
from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse


class ApiResponse:
    """Utility class for creating standardized API responses.

    Provides static methods to create consistent JSON responses for
    success and error scenarios.

    Note:
        - **抛出异常**: 对于需要中断流程的错误（如 NotFoundError, UnauthorizedError 等），
          应该抛出异常，由全局异常处理器自动处理。
        - **返回错误响应**: 对于业务逻辑错误，但需要返回错误信息给用户而不中断流程的场景，
          可以使用 `ApiResponse.error()` 直接返回错误响应。
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

        Use this method when you need to return an error response directly
        without raising an exception (e.g., business logic errors that should
        be returned to the user without interrupting the flow).

        Args:
            message: Error message (default: "操作失败")
            code: Business error code (default: 500)
            status_code: HTTP status code (default: 500 Internal Server Error)
            error_detail: Detailed error information (optional)
            data: Additional error data (optional)

        Returns:
            JSONResponse with standardized error format

        Note:
            - For errors that should interrupt the flow (e.g., NotFoundError,
              UnauthorizedError), use exceptions instead.
            - Avoid including sensitive information in error_detail in production

        Example:
            # 业务逻辑错误，需要返回给用户但不中断流程
            >>> if not valid_condition:
            ...     return ApiResponse.error(
            ...         message="业务验证失败",
            ...         code=400,
            ...         status_code=HTTPStatus.BAD_REQUEST
            ...     )

            # 需要中断流程的错误，使用异常
            >>> from faster_app.exceptions import NotFoundError
            >>> raise NotFoundError(message="资源未找到")
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
