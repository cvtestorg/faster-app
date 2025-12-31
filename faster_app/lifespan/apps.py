"""
应用生命周期管理

提供应用模块的生命周期管理。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from faster_app.apps.discover import AppLifecycleDiscover
from faster_app.settings import logger


@asynccontextmanager
async def apps_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    try:
        logger.info("[生命周期] 操作: 发现应用生命周期")
        registry = AppLifecycleDiscover().discover()
        app.state.app_registry = registry

        if registry.list_apps():
            app_count = len(registry.list_apps())
            logger.info(f"[生命周期] 操作: 发现应用 数量: {app_count}")
            await registry.startup_all()
            logger.info(f"[生命周期] 操作: 启动应用 状态: 完成 数量: {app_count}")
        else:
            logger.info("[生命周期] 操作: 发现应用 状态: 未发现 动作: 跳过启动")
    except Exception as e:
        logger.error(f"[生命周期] 操作: 应用启动 状态: 失败 错误: {str(e)}", exc_info=True)
        # 继续运行, 不中断整个应用

    yield

    # 关闭所有应用
    if hasattr(app.state, "app_registry"):
        registry = app.state.app_registry
        try:
            logger.info("[生命周期] 操作: 关闭应用 状态: 开始")
            await registry.shutdown_all()
            logger.info("[生命周期] 操作: 关闭应用 状态: 完成")
        except Exception as e:
            logger.error(f"[生命周期] 操作: 关闭应用 状态: 失败 错误: {str(e)}", exc_info=True)
