"""
Database lifecycle management for FastAPI.

Provides lifespan context manager for Tortoise ORM initialization
and cleanup.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from faster_app.settings import configs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage database connection lifecycle for FastAPI application.

    Initializes Tortoise ORM on startup and closes connections on shutdown.

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime

    Note:
        This function is designed to be used with FastAPI's lifespan parameter.

    Example:
        >>> app = FastAPI(lifespan=lifespan)
    """
    await Tortoise.init(config=configs.TORTOISE_ORM)
    yield
    await Tortoise.close_connections()
