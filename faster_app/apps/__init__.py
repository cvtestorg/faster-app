"""
应用生命周期管理模块

提供应用生命周期管理的基础设施。
"""

from faster_app.apps.base import AppLifecycle, AppState
from faster_app.apps.discover import AppLifecycleDiscover
from faster_app.apps.registry import AppRegistry

__all__ = [
    "AppLifecycle",
    "AppState",
    "AppRegistry",
    "AppLifecycleDiscover",
]
