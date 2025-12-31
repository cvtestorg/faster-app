"""
全局异常处理器

提供统一的异常处理机制, 自动将异常转换为标准响应格式。
"""

import logging
import traceback
from datetime import datetime

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from faster_app.exceptions.base import FasterAppError
from faster_app.settings import configs

logger = logging.getLogger(__name__)


async def faster_app_exception_handler(request: Request, exc: FasterAppError) -> JSONResponse:
    """处理 FasterAppError 异常

    Args:
        request: FastAPI 请求对象
        exc: FasterAppError 异常实例

    Returns:
        标准化的错误响应
    """
    error_data = exc.to_dict()
    error_data["timestamp"] = datetime.now().isoformat()

    # 在生产环境中隐藏详细错误信息
    if not configs.DEBUG and exc.error_detail:
        error_data.pop("error_detail", None)

    logger.warning(
        f"[异常处理] FasterAppError 消息: {exc.message} 错误码: {exc.code} "
        f"状态码: {exc.status_code} 资源: {exc.__class__.__name__}"
    )

    return JSONResponse(
        content=error_data,
        status_code=exc.status_code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证错误

    Args:
        request: FastAPI 请求对象
        exc: RequestValidationError 异常实例

    Returns:
        标准化的错误响应
    """
    errors = exc.errors()
    error_messages = []

    for error in errors:
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "验证失败")
        error_messages.append(f"{field}: {message}")

    error_detail = "; ".join(error_messages)
    message = "请求参数验证失败"

    error_data = {
        "success": False,
        "code": 400,
        "message": message,
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }

    # 在开发环境中显示详细错误信息
    if configs.DEBUG:
        error_data["error_detail"] = error_detail
        error_data["errors"] = errors

    logger.warning(f"[请求验证] 验证失败 详情: {error_detail}")

    return JSONResponse(
        content=error_data,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 HTTP 异常

    Args:
        request: FastAPI 请求对象
        exc: StarletteHTTPException 异常实例

    Returns:
        标准化的错误响应
    """
    error_data = {
        "success": False,
        "code": exc.status_code,
        "message": exc.detail if hasattr(exc, "detail") else "HTTP 错误",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }

    logger.warning(
        f"[HTTP异常] 状态码: {exc.status_code} 详情: {exc.detail if hasattr(exc, 'detail') else 'HTTP错误'}"
    )

    return JSONResponse(
        content=error_data,
        status_code=exc.status_code,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常

    Args:
        request: FastAPI 请求对象
        exc: 异常实例

    Returns:
        标准化的错误响应
    """
    error_data = {
        "success": False,
        "code": 500,
        "message": "服务器内部错误",
        "data": None,
        "timestamp": datetime.now().isoformat(),
    }

    # 在开发环境中显示详细错误信息
    if configs.DEBUG:
        error_data["error_detail"] = str(exc)
        error_data["traceback"] = traceback.format_exc()

    # 记录完整错误信息到日志
    logger.error(
        f"[未处理异常] 异常类型: {type(exc).__name__} 消息: {str(exc)} 路径: {request.url.path if hasattr(request, 'url') else 'unknown'}",
        exc_info=True,
    )

    return JSONResponse(
        content=error_data,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app) -> None:
    """注册所有异常处理器到 FastAPI 应用

    Args:
        app: FastAPI 应用实例
    """
    from faster_app.exceptions import FasterAppError

    # 注册异常处理器, 按优先级从高到低
    app.add_exception_handler(FasterAppError, faster_app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("[应用初始化] 异常处理器已注册")
