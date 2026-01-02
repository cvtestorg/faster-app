"""
应用生命周期管理模块

提供应用生命周期管理的核心功能。
"""

from faster_app.lifespan.apps import apps_lifespan
from faster_app.lifespan.combine import combine_lifespans
from faster_app.lifespan.database import database_lifespan
from faster_app.lifespan.defaults import get_lifespan, lifespan
from faster_app.lifespan.discover import LifespanDiscover
from faster_app.lifespan.manager import LifespanManager, get_manager

__all__ = [
    "combine_lifespans",
    "database_lifespan",
    "apps_lifespan",
    "get_lifespan",
    "lifespan",
    "LifespanDiscover",
    "LifespanManager",
    "get_manager",
]
