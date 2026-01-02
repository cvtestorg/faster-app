"""
自动发现应用生命周期

扫描 apps/*/lifecycle.py 文件, 发现并注册所有应用的生命周期管理。
"""

import logging

from faster_app.apps.base import AppLifecycle
from faster_app.apps.registry import AppRegistry
from faster_app.utils.discover import BaseDiscover

logger = logging.getLogger(__name__)


class AppLifecycleDiscover(BaseDiscover):
    """应用生命周期发现器"""

    INSTANCE_TYPE = AppLifecycle

    TARGETS = [
        {
            "directory": "apps",
            "filename": "lifecycle.py",
            "skip_dirs": ["__pycache__", "utils", "tests"],
            "skip_files": [],
        },
    ]

    def discover(self) -> AppRegistry:
        """发现并注册所有应用生命周期

        Returns:
            应用注册表实例, 包含所有已注册的应用

        Raises:
            ValueError: 如果重复注册
        """
        registry = AppRegistry()
        instances = super().discover()

        if not instances:
            logger.info("未发现任何应用生命周期")
            return registry

        # 注册所有应用
        for instance in instances:
            try:
                registry.register(instance)
                logger.info(f"注册应用: {instance.app_name}")
            except ValueError as e:
                logger.error(f"注册应用失败: {e}")
                raise

        return registry
