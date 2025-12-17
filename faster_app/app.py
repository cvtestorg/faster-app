"""
Faster APP application instance module.

Creates and configures the FastAPI application with automatic discovery
of routes, middleware, and database configuration.
"""

from typing import Optional
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from faster_app.routes.discover import RoutesDiscover
from faster_app.middleware.discover import MiddlewareDiscover
from faster_app.settings import logger
from faster_app.settings import configs
from faster_app.utils import BASE_DIR
from faster_app.utils.db import lifespan


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application instance.
    
    Automatically discovers and registers:
    - Routes from apps/*/routes.py files
    - Middleware from middleware/*.py files
    - Static file serving from /statics directory
    
    Returns:
        Configured FastAPI application instance
        
    Note:
        Uses singleton pattern via get_app() to ensure single instance
    """
    app = FastAPI(
        title=configs.PROJECT_NAME,
        version=configs.VERSION,
        debug=configs.DEBUG,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )

    # 添加静态文件服务器
    try:
        app.mount(
            "/static", StaticFiles(directory=f"{BASE_DIR}/statics"), name="static"
        )
    except Exception as e:
        logger.error(f"静态文件服务器启动失败: {e}")

    # 添加中间件
    middlewares = MiddlewareDiscover().discover()
    for middleware in middlewares:
        app.add_middleware(middleware["class"], **middleware["kwargs"])
        logger.info(f"Loaded middleware: {middleware['class'].__name__}")

    # 添加路由
    routes = RoutesDiscover().discover()
    for route in routes:
        app.include_router(route)

    return app


def get_app() -> FastAPI:
    """
    Get application instance using singleton pattern.
    
    Creates the app on first call and returns cached instance on
    subsequent calls.
    
    Returns:
        FastAPI application instance
    """
    if not hasattr(get_app, "_app"):
        get_app._app = create_app()
    return get_app._app
