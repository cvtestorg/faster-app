"""
统一日志格式工具

提供统一的日志格式,方便问题排查和日志分析。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_log_message(
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
    message: str | None = None,
) -> str:
    """
    格式化日志消息,统一格式便于排查问题

    Args:
        action: 操作类型 (如: "启动应用", "创建记录", "处理请求")
        resource: 资源类型 (如: "应用", "Demo", "路由")
        resource_id: 资源标识 (如: 应用名称, 记录ID)
        status: 状态 (如: "成功", "失败", "完成")
        details: 额外详细信息字典
        message: 自定义消息 (如果提供,将优先使用)

    Returns:
        格式化后的日志消息

    Example:
        >>> format_log_message("启动应用", resource="应用", resource_id="demo", status="成功")
        "[启动应用] 应用: demo 状态: 成功"

        >>> format_log_message("创建记录", resource="Demo", resource_id="123", details={"name": "test"})
        "[创建记录] Demo: 123 name: test"
    """
    if message:
        return message

    parts = [f"[{action}]"]

    if resource:
        if resource_id:
            parts.append(f"{resource}: {resource_id}")
        else:
            parts.append(f"{resource}")

    if status:
        parts.append(f"状态: {status}")

    if details:
        detail_parts = [f"{k}: {v}" for k, v in details.items()]
        parts.extend(detail_parts)

    return " ".join(parts)


def log_info(
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
    message: str | None = None,
    logger_instance: logging.Logger | None = None,
) -> None:
    """记录 INFO 级别日志

    使用 extra 参数传递结构化数据,JSON 格式中会作为顶级字段。
    """
    log = logger_instance or logger
    msg = format_log_message(action, resource, resource_id, status, details, message)

    # 构建结构化数据,用于 JSON 格式
    extra = {
        "event": action,
    }
    if resource:
        extra["resource_type"] = resource
    if resource_id:
        extra["resource_id"] = resource_id
    if status:
        extra["status"] = status
    if details:
        extra.update(details)

    log.info(msg, extra=extra)


def log_warning(
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
    message: str | None = None,
    logger_instance: logging.Logger | None = None,
) -> None:
    """记录 WARNING 级别日志

    使用 extra 参数传递结构化数据,JSON 格式中会作为顶级字段。
    """
    log = logger_instance or logger
    msg = format_log_message(action, resource, resource_id, status, details, message)

    # 构建结构化数据,用于 JSON 格式
    extra = {
        "event": action,
    }
    if resource:
        extra["resource_type"] = resource
    if resource_id:
        extra["resource_id"] = resource_id
    if status:
        extra["status"] = status
    if details:
        extra.update(details)

    log.warning(msg, extra=extra)


def log_error(
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
    message: str | None = None,
    logger_instance: logging.Logger | None = None,
    exc_info: bool = False,
) -> None:
    """记录 ERROR 级别日志

    使用 extra 参数传递结构化数据,JSON 格式中会作为顶级字段。
    """
    log = logger_instance or logger
    msg = format_log_message(action, resource, resource_id, status, details, message)

    # 构建结构化数据,用于 JSON 格式
    extra = {
        "event": action,
    }
    if resource:
        extra["resource_type"] = resource
    if resource_id:
        extra["resource_id"] = resource_id
    if status:
        extra["status"] = status
    if details:
        extra.update(details)

    log.error(msg, extra=extra, exc_info=exc_info)


def log_debug(
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
    message: str | None = None,
    logger_instance: logging.Logger | None = None,
) -> None:
    """记录 DEBUG 级别日志

    使用 extra 参数传递结构化数据,JSON 格式中会作为顶级字段。
    """
    log = logger_instance or logger
    msg = format_log_message(action, resource, resource_id, status, details, message)

    # 构建结构化数据,用于 JSON 格式
    extra = {
        "event": action,
    }
    if resource:
        extra["resource_type"] = resource
    if resource_id:
        extra["resource_id"] = resource_id
    if status:
        extra["status"] = status
    if details:
        extra.update(details)

    log.debug(msg, extra=extra)
