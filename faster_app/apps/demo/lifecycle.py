"""
Demo 应用生命周期管理

演示如何使用应用生命周期管理功能。
"""

import logging

from faster_app.apps.base import AppLifecycle

logger = logging.getLogger(__name__)


class DemoAppLifecycle(AppLifecycle):
    """Demo 应用生命周期管理"""

    @property
    def app_name(self) -> str:
        return "demo"

    @property
    def dependencies(self) -> list[str]:
        """Demo 应用没有依赖其他应用"""
        return []

    async def on_startup(self) -> None:
        """启动时初始化"""
        logger.info("Demo 应用启动中...")
        # 这里可以:
        # - 初始化缓存连接
        # - 启动后台任务
        # - 预加载数据
        logger.info("Demo 应用启动完成")

    async def on_ready(self) -> None:
        """就绪时执行"""
        logger.info("Demo 应用已就绪")
        # 所有依赖已启动, 可以安全使用其他应用的功能

    async def on_shutdown(self) -> None:
        """关闭时清理"""
        logger.info("Demo 应用关闭中...")
        # 这里可以:
        # - 关闭连接
        # - 停止后台任务
        # - 保存状态
        logger.info("Demo 应用已关闭")

    async def health_check(self) -> dict:
        """健康检查"""
        return {
            "status": "healthy",
            "app": self.app_name,
            "message": "Demo app is running",
        }
