"""
应用生命周期基类

定义应用生命周期管理接口和基础实现。
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class AppState(Enum):
    """应用状态枚举"""

    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    READY = "ready"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


class AppLifecycle(ABC):
    """应用生命周期接口

    每个应用可以实现此接口来管理自己的生命周期。
    应用生命周期文件应命名为 lifecycle.py, 放在 apps/{app_name}/ 目录下。
    """

    @property
    @abstractmethod
    def app_name(self) -> str:
        """应用名称

        Returns:
            应用名称, 通常与目录名一致
        """
        pass

    @property
    def dependencies(self) -> list[str]:
        """依赖的其他应用名称列表

        Returns:
            依赖的应用名称列表, 这些应用会在当前应用之前启动
        """
        return []

    async def on_startup(self) -> None:  # noqa
        """应用启动时的钩子函数

        在应用启动时调用, 此时依赖的应用已经启动但可能还未就绪。
        适合进行:
        - 初始化资源连接
        - 启动后台任务
        - 预加载数据
        """
        pass

    async def on_ready(self) -> None:  # noqa
        """应用就绪时的钩子函数

        在所有依赖应用都已就绪后调用。
        此时可以安全地使用依赖应用的功能。
        """
        pass

    async def on_shutdown(self) -> None:  # noqa
        """应用关闭时的钩子函数

        在应用关闭时调用, 按启动顺序的逆序执行。
        适合进行:
        - 关闭连接
        - 停止后台任务
        - 保存状态
        """
        pass

    async def health_check(self) -> dict[str, Any]:
        """健康检查

        Returns:
            健康状态字典, 包含 status 字段
        """
        return {"status": "healthy", "app": self.app_name}
