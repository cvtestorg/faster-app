"""
默认 Lifespan 实现

提供框架默认的 lifespan 组合和获取函数。
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from faster_app.lifespan.apps import apps_lifespan
from faster_app.lifespan.combine import combine_lifespans
from faster_app.lifespan.database import database_lifespan
from faster_app.lifespan.discover import LifespanDiscover
from faster_app.settings import logger


def get_lifespan() -> Callable[[FastAPI], AsyncGenerator[None, None]]:
    """
    获取组合后的 lifespan 函数

    自动组合:
    1. 框架默认的 lifespan (database_lifespan, apps_lifespan)
    2. 用户自定义的 lifespan (从 config/lifespan.py 自动发现)

    启动顺序: 数据库 -> 应用 -> 用户自定义 lifespan
    关闭顺序: 用户自定义 lifespan -> 应用 -> 数据库 (自动逆序)

    Returns:
        组合后的 lifespan 函数
    """
    # 框架默认的 lifespan
    default_lifespans = [database_lifespan, apps_lifespan]

    # 发现用户自定义的 lifespan
    try:
        user_lifespans = LifespanDiscover().discover()
        if user_lifespans:
            logger.info(f"发现 {len(user_lifespans)} 个用户自定义 lifespan")
            # 用户自定义的 lifespan 在框架默认之后执行
            all_lifespans = default_lifespans + user_lifespans
        else:
            all_lifespans = default_lifespans
    except Exception as e:
        logger.warning(f"发现用户自定义 lifespan 失败: {e}, 使用默认配置")
        all_lifespans = default_lifespans

    # 组合所有 lifespan
    return combine_lifespans(*all_lifespans)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    组合的生命周期管理

    使用 get_lifespan() 获取组合后的 lifespan, 自动包含:
    1. database_lifespan - 数据库连接生命周期
    2. apps_lifespan - 应用生命周期
    3. 用户自定义的 lifespan (从 config/lifespan.py 自动发现)

    启动顺序: 数据库 -> 应用 -> 用户自定义
    关闭顺序: 用户自定义 -> 应用 -> 数据库 (自动逆序)

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime

    Note:
        Application registry is stored in app.state.app_registry
    """
    combined = get_lifespan()
    async with combined(app):
        yield
