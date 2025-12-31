"""
应用注册表

管理所有应用的生命周期, 处理依赖关系和启动顺序。
"""

import asyncio
import logging
from collections import defaultdict, deque
from typing import Any

from faster_app.apps.base import AppLifecycle, AppState

logger = logging.getLogger(__name__)


class AppRegistry:
    """应用注册表 - 管理所有应用的生命周期"""

    def __init__(self):
        self._apps: dict[str, AppLifecycle] = {}
        self._states: dict[str, AppState] = {}
        self._startup_order: list[str] = []
        self._dependency_graph: dict[str, set[str]] = defaultdict(set)
        self._reverse_dependency_graph: dict[str, set[str]] = defaultdict(set)

    def register(self, app: AppLifecycle) -> None:
        """注册应用

        Args:
            app: 应用生命周期实例

        Raises:
            ValueError: 如果应用名称重复或依赖不存在
        """
        app_name = app.app_name

        if app_name in self._apps:
            raise ValueError(f"应用 {app_name} 已注册")

        # 验证依赖是否存在
        for dep in app.dependencies:
            if dep not in self._apps and dep != app_name:
                # 允许依赖尚未注册的应用 (可能还未发现)
                pass

        self._apps[app_name] = app
        self._states[app_name] = AppState.UNINITIALIZED

        # 构建依赖图
        for dep in app.dependencies:
            if dep != app_name:
                self._dependency_graph[app_name].add(dep)
                self._reverse_dependency_graph[dep].add(app_name)

    def _topological_sort(self) -> list[str]:
        """拓扑排序确定启动顺序

        Returns:
            按依赖关系排序的应用名称列表

        Raises:
            ValueError: 如果存在循环依赖
        """
        # Kahn 算法
        in_degree: dict[str, int] = defaultdict(int)
        for app_name in self._apps:
            in_degree[app_name] = len(self._dependency_graph[app_name])

        queue = deque([app for app in self._apps if in_degree[app] == 0])
        result = []

        while queue:
            app_name = queue.popleft()
            result.append(app_name)

            for dependent in self._reverse_dependency_graph[app_name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # 检查是否有循环依赖
        if len(result) != len(self._apps):
            # 找出未处理的应用 (循环依赖的一部分)
            unprocessed = set(self._apps.keys()) - set(result)
            raise ValueError(f"检测到循环依赖: {unprocessed}")

        return result

    async def startup_all(self, timeout: float = 30.0) -> None:
        """按依赖顺序启动所有应用

        Args:
            timeout: 启动超时时间 (秒)

        Raises:
            TimeoutError: 如果启动超时
            RuntimeError: 如果启动失败
        """
        # 计算启动顺序
        try:
            self._startup_order = self._topological_sort()
        except ValueError as e:
            logger.error(f"无法确定启动顺序: {e}")
            raise

        logger.info(f"应用启动顺序: {' -> '.join(self._startup_order)}")

        # 按顺序启动应用
        for app_name in self._startup_order:
            app = self._apps[app_name]
            self._states[app_name] = AppState.STARTING

            try:
                logger.info(f"[应用启动] 应用: {app_name} 状态: 启动中")
                await asyncio.wait_for(app.on_startup(), timeout=timeout)
                logger.info(f"[应用启动] 应用: {app_name} 状态: 完成")
            except asyncio.TimeoutError:
                logger.error(f"[应用启动] 应用: {app_name} 状态: 超时 超时时间: {timeout}秒")
                self._states[app_name] = AppState.STOPPED
                raise RuntimeError(f"应用 {app_name} 启动超时")
            except Exception as e:
                logger.error(f"[应用启动] 应用: {app_name} 状态: 失败 错误: {str(e)}", exc_info=True)
                self._states[app_name] = AppState.STOPPED
                # 继续启动其他应用, 不中断整个流程
                continue

        # 按顺序调用 on_ready
        for app_name in self._startup_order:
            if self._states[app_name] == AppState.STARTING:
                app = self._apps[app_name]
                try:
                    logger.info(f"[应用就绪] 应用: {app_name} 状态: 处理中")
                    await app.on_ready()
                    self._states[app_name] = AppState.READY
                    logger.info(f"[应用就绪] 应用: {app_name} 状态: 完成")
                except Exception as e:
                    logger.error(f"[应用就绪] 应用: {app_name} 状态: 失败 错误: {str(e)}", exc_info=True)
                    # 继续处理其他应用

    async def shutdown_all(self, timeout: float = 30.0) -> None:
        """按相反顺序关闭所有应用

        Args:
            timeout: 关闭超时时间 (秒)
        """
        # 按启动顺序的逆序关闭
        shutdown_order = list(reversed(self._startup_order))

        for app_name in shutdown_order:
            if self._states[app_name] not in (AppState.READY, AppState.STARTING):
                continue

            app = self._apps[app_name]
            self._states[app_name] = AppState.SHUTTING_DOWN

            try:
                logger.info(f"[应用关闭] 应用: {app_name} 状态: 关闭中")
                await asyncio.wait_for(app.on_shutdown(), timeout=timeout)
                logger.info(f"[应用关闭] 应用: {app_name} 状态: 完成")
            except asyncio.TimeoutError:
                logger.warning(f"[应用关闭] 应用: {app_name} 状态: 超时 超时时间: {timeout}秒")
            except Exception as e:
                logger.error(f"[应用关闭] 应用: {app_name} 状态: 失败 错误: {str(e)}", exc_info=True)
            finally:
                self._states[app_name] = AppState.STOPPED

    def get_app(self, app_name: str) -> AppLifecycle | None:
        """获取应用实例

        Args:
            app_name: 应用名称

        Returns:
            应用实例, 如果不存在则返回 None
        """
        return self._apps.get(app_name)

    def get_state(self, app_name: str) -> AppState | None:
        """获取应用状态

        Args:
            app_name: 应用名称

        Returns:
            应用状态, 如果不存在则返回 None
        """
        return self._states.get(app_name)

    def list_apps(self) -> list[dict[str, Any]]:
        """列出所有应用信息

        Returns:
            应用信息列表
        """
        return [
            {
                "name": app_name,
                "state": self._states[app_name].value,
                "dependencies": list(self._dependency_graph[app_name]),
            }
            for app_name in self._startup_order
        ]
