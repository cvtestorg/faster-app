"""
数据库生命周期管理

提供数据库连接的生命周期管理。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from faster_app.settings import configs, logger


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """数据库生命周期管理"""
    logger.info("初始化数据库连接...")
    await Tortoise.init(config=configs.TORTOISE_ORM)
    logger.info("数据库连接初始化完成")

    yield

    logger.info("关闭数据库连接...")
    await Tortoise.close_connections()
    logger.info("数据库连接已关闭")
