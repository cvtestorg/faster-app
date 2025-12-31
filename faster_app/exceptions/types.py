"""
常见异常类型

定义常用的异常类型, 方便使用。
"""

from http import HTTPStatus

from faster_app.exceptions.base import FasterAppError


class ValidationError(FasterAppError):
    """验证错误 (400)"""

    def __init__(
        self,
        message: str = "请求参数验证失败",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=400,
            status_code=HTTPStatus.BAD_REQUEST,
            error_detail=error_detail,
            data=data,
        )


class BadRequestError(FasterAppError):
    """错误请求 (400)"""

    def __init__(
        self,
        message: str = "错误的请求",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=400,
            status_code=HTTPStatus.BAD_REQUEST,
            error_detail=error_detail,
            data=data,
        )


class UnauthorizedError(FasterAppError):
    """未授权错误 (401)"""

    def __init__(
        self,
        message: str = "未授权, 请先登录",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=401,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_detail=error_detail,
            data=data,
        )


class ForbiddenError(FasterAppError):
    """禁止访问错误 (403)"""

    def __init__(
        self,
        message: str = "禁止访问",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=403,
            status_code=HTTPStatus.FORBIDDEN,
            error_detail=error_detail,
            data=data,
        )


class NotFoundError(FasterAppError):
    """资源未找到错误 (404)"""

    def __init__(
        self,
        message: str = "资源未找到",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=404,
            status_code=HTTPStatus.NOT_FOUND,
            error_detail=error_detail,
            data=data,
        )


class TooManyRequestsError(FasterAppError):
    """请求频率过高错误 (429)"""

    def __init__(
        self,
        message: str = "请求频率过高，请稍后再试",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=429,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_detail=error_detail,
            data=data,
        )

    def __init__(
        self,
        message: str = "资源未找到",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=404,
            status_code=HTTPStatus.NOT_FOUND,
            error_detail=error_detail,
            data=data,
        )


class ConflictError(FasterAppError):
    """冲突错误 (409)"""

    def __init__(
        self,
        message: str = "资源冲突",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=409,
            status_code=HTTPStatus.CONFLICT,
            error_detail=error_detail,
            data=data,
        )


class InternalServerError(FasterAppError):
    """内部服务器错误 (500)"""

    def __init__(
        self,
        message: str = "服务器内部错误",
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=500,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_detail=error_detail,
            data=data,
        )
