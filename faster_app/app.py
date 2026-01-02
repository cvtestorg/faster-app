"""
Faster APP application instance module.

Creates and configures the FastAPI application with automatic discovery
of routes, middleware, and database configuration.
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from faster_app.lifespan import lifespan
from faster_app.middleware.discover import MiddlewareDiscover
from faster_app.routes.discover import RoutesDiscover
from faster_app.settings import configs, logger
from faster_app.utils import BASE_DIR


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
        app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/statics"), name="static")
        logger.info("[应用初始化] 操作: 静态文件服务器 状态: 成功")
    except Exception as e:
        logger.error(
            f"[应用初始化] 操作: 静态文件服务器 状态: 失败 错误: {str(e)}",
            exc_info=True,
        )

    # 添加中间件
    middlewares = MiddlewareDiscover().discover()
    for middleware in middlewares:
        app.add_middleware(middleware["class"], **middleware["kwargs"])
        logger.info(f"[应用初始化] 操作: 加载中间件 中间件: {middleware['class'].__name__} 状态: 成功")

    # 添加路由 (启用路由冲突检测)
    validate_routes = getattr(configs, "VALIDATE_ROUTES", True)
    routes = RoutesDiscover().discover(validate=validate_routes)
    route_count = len(routes)
    for route in routes:
        app.include_router(route)
    if route_count > 0:
        logger.info(f"[应用初始化] 操作: 加载路由 数量: {route_count} 状态: 成功")

    # 注册异常处理器
    from faster_app.exceptions import get_manager

    get_manager().apply(app)

    logger.info(
        f"[应用初始化] 操作: 应用创建 应用名: {configs.PROJECT_NAME} 版本: {configs.VERSION} 状态: 完成"
    )

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
