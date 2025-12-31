"""
Action 装饰器

提供 @action 装饰器用于定义自定义操作，类似 DRF 的 @action。
"""

from functools import wraps
from typing import Any, Callable

from fastapi import Request


def action(
    methods: list[str] | None = None,
    detail: bool = False,
    url_path: str | None = None,
    url_name: str | None = None,
    **kwargs: Any,
) -> Callable:
    """
    装饰器：定义自定义操作

    Args:
        methods: HTTP 方法列表，如 ["GET", "POST"]，默认 ["GET"]
        detail: 是否是针对单个对象的操作（需要 pk 参数）
        url_path: 自定义 URL 路径，默认使用函数名
        url_name: URL 名称（用于反向解析）
        **kwargs: 其他 FastAPI 路由参数

    Returns:
        装饰器函数

    Example:
        class MyViewSet(ModelViewSet):
            @action(detail=True, methods=["POST"])
            async def activate(self, request: Request, pk: str):
                # 激活操作
                pass

            @action(detail=False, methods=["GET"])
            async def stats(self, request: Request):
                # 统计操作
                pass
    """
    if methods is None:
        methods = ["GET"]

    def decorator(func: Callable) -> Callable:
        # 将 action 元数据附加到函数上
        func.action = True
        func.action_methods = methods
        func.action_detail = detail
        func.action_url_path = url_path or func.__name__.replace("_", "-")
        func.action_url_name = url_name or func.__name__
        func.action_kwargs = kwargs

        @wraps(func)
        async def wrapper(self, request: Request, *args: Any, **kwargs: Any) -> Any:
            return await func(self, request, *args, **kwargs)

        return wrapper

    return decorator
