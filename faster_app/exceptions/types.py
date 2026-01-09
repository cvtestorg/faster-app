"""常见异常类型"""

from http import HTTPStatus

from faster_app.exceptions.base import FasterAppError


class ValidationError(FasterAppError):
    """验证错误 (400)"""

    default_status_code = HTTPStatus.BAD_REQUEST
    default_message = "请求参数验证失败"


class BadRequestError(FasterAppError):
    """错误请求 (400)"""

    default_status_code = HTTPStatus.BAD_REQUEST
    default_message = "错误的请求"


class UnauthorizedError(FasterAppError):
    """未授权错误 (401)"""

    default_status_code = HTTPStatus.UNAUTHORIZED
    default_message = "未授权, 请先登录"


class ForbiddenError(FasterAppError):
    """禁止访问错误 (403)"""

    default_status_code = HTTPStatus.FORBIDDEN
    default_message = "禁止访问"


class NotFoundError(FasterAppError):
    """资源未找到错误 (404)"""

    default_status_code = HTTPStatus.NOT_FOUND
    default_message = "资源未找到"


class ConflictError(FasterAppError):
    """冲突错误 (409)"""

    default_status_code = HTTPStatus.CONFLICT
    default_message = "资源冲突"


class TooManyRequestsError(FasterAppError):
    """请求频率过高错误 (429)"""

    default_status_code = HTTPStatus.TOO_MANY_REQUESTS
    default_message = "请求频率过高,请稍后再试"


class InternalServerError(FasterAppError):
    """内部服务器错误 (500)"""

    default_status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_message = "服务器内部错误"
