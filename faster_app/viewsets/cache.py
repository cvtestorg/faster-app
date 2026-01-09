"""
缓存系统

提供简单的缓存装饰器和工具,用于缓存 ViewSet 的响应。
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import Request


class SimpleCache:
    """
    简单内存缓存

    用于缓存 ViewSet 的响应结果。
    """

    _cache: dict[str, tuple[Any, float]] = {}  # {key: (value, expire_time)}

    def __init__(self, default_timeout: int = 300):
        """
        初始化缓存

        Args:
            default_timeout: 默认过期时间(秒),默认 5 分钟
        """
        self.default_timeout = default_timeout

    def get(self, key: str) -> Any | None:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值,如果不存在或已过期返回 None
        """
        import time

        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]
        if time.time() > expire_time:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间(秒),如果为 None 使用默认值
        """
        import time

        timeout = timeout or self.default_timeout
        expire_time = time.time() + timeout
        self._cache[key] = (value, expire_time)

    def delete(self, key: str) -> None:
        """
        删除缓存值

        Args:
            key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()


# 全局缓存实例
_default_cache = SimpleCache()


def cache_response(
    timeout: int = 300,
    key_func: Callable[[Request], str] | None = None,
    cache_instance: SimpleCache | None = None,
):
    """
    缓存响应装饰器

    Args:
        timeout: 缓存过期时间(秒),默认 5 分钟
        key_func: 自定义缓存键生成函数,如果为 None 使用默认函数
        cache_instance: 缓存实例,如果为 None 使用全局缓存

    Returns:
        装饰器函数

    Example:
        class DemoViewSet(ModelViewSet):
            @cache_response(timeout=600)
            async def list(self, request: Request, ...):
                # 响应会被缓存 10 分钟
                pass
    """
    cache = cache_instance or _default_cache

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, request: Request, *args: Any, **kwargs: Any) -> Any:
            # 生成缓存键
            if key_func:
                cache_key = key_func(request)
            else:
                # 默认缓存键：基于请求路径和查询参数
                cache_key = _generate_cache_key(request, func.__name__)

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            result = await func(self, request, *args, **kwargs)
            cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


def _generate_cache_key(request: Request, func_name: str) -> str:
    """
    生成缓存键

    Args:
        request: FastAPI 请求对象
        func_name: 函数名称

    Returns:
        缓存键字符串
    """
    # 构建键的组成部分
    parts = [
        func_name,
        request.url.path,
        str(sorted(request.query_params.items())),
    ]

    # 如果有用户,包含用户 ID
    if hasattr(request.state, "user") and request.state.user:
        user_id = getattr(request.state.user, "id", None)
        if user_id:
            parts.append(str(user_id))

    # 生成哈希键
    key_string = json.dumps(parts, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def invalidate_cache(pattern: str | None = None, cache_instance: SimpleCache | None = None) -> None:
    """
    使缓存失效

    Args:
        pattern: 缓存键模式(可选,如果提供则只删除匹配的键)
        cache_instance: 缓存实例,如果为 None 使用全局缓存
    """
    cache = cache_instance or _default_cache

    if pattern:
        # 删除匹配模式的键
        keys_to_delete = [key for key in cache._cache if pattern in key]
        for key in keys_to_delete:
            cache.delete(key)
    else:
        # 清空所有缓存
        cache.clear()
