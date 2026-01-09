"""
数据库生命周期管理

提供数据库连接的生命周期管理。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from faster_app.settings import logger
from faster_app.settings.builtins.orm import TORTOISE_ORM


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """数据库生命周期管理"""
    logger.debug("初始化数据库连接...")
    await Tortoise.init(config=TORTOISE_ORM)
    logger.info("数据库连接初始化完成")

    yield

    logger.debug("关闭数据库连接...")
    await Tortoise.close_connections()
    logger.debug("数据库连接已关闭")
