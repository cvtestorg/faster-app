"""
中间件配置

⚠️ 注意：默认只启用 FastAPI 内置的核心中间件，不包含自定义中间件以避免性能开销。
如需添加自定义中间件（如日志、性能监控），请参考 custom.py 中的使用示例。

支持特性：
1. 环境感知：根据 DEBUG 配置自动选择开发/生产环境配置
2. 优先级排序：通过 priority 字段控制中间件执行顺序（数字越小越先执行）
3. 动态启用/禁用：通过 enabled 字段控制中间件是否加载
4. 配置来自 Settings：所有敏感配置从配置文件读取

优先级说明：
- 1-10: 日志和监控（最外层，捕获一切）
- 11-20: 安全相关（CORS, TrustedHost, SecurityHeaders）
- 21-30: 压缩和优化
- 31+: 其他业务中间件

中间件执行顺序：
请求流：priority 1 -> 2 -> 3 -> ... -> 路由处理器
响应流：路由处理器 -> ... -> 3 -> 2 -> 1
"""

from faster_app.settings import configs

# 中间件配置列表

MIDDLEWARES = [
    # 安全相关
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "priority": 12,  # CORS 处理
        "enabled": True,
        "kwargs": {
            "allow_origins": configs.middleware.cors.allow_origins,
            "allow_credentials": configs.middleware.cors.allow_credentials,
            "allow_methods": configs.middleware.cors.allow_methods,
            "allow_headers": configs.middleware.cors.allow_headers,
            "expose_headers": configs.middleware.cors.expose_headers,
            "max_age": configs.middleware.cors.max_age,
        },
    },
    {
        "class": "fastapi.middleware.trustedhost.TrustedHostMiddleware",
        "priority": 13,  # 主机名验证
        "enabled": configs.middleware.trusted_host.enabled,
        "kwargs": {
            "allowed_hosts": configs.middleware.trusted_host.hosts,
        },
    },
    # 压缩和优化
    {
        "class": "fastapi.middleware.gzip.GZipMiddleware",
        "priority": 21,  # GZip 压缩
        "enabled": configs.middleware.gzip.enabled,
        "kwargs": {
            "minimum_size": configs.middleware.gzip.minimum_size,
        },
    },
]


# 启动时日志提示


def _log_middleware_info():
    """记录中间件配置信息"""
    from faster_app.settings import logger

    if configs.debug:
        logger.info("🔧 [开发模式] 中间件使用宽松的安全配置")
    else:
        # 生产环境提示
        cors_cfg = configs.middleware.cors
        if "*" in cors_cfg.allow_origins:
            logger.warning("⚠️  [安全提示] 生产环境 CORS 允许所有域名访问，建议指定明确的域名列表")

        trusted_cfg = configs.middleware.trusted_host
        if not trusted_cfg.enabled:
            logger.warning(
                "⚠️  [安全提示] 生产环境建议启用 TrustedHostMiddleware "
                "（设置 TRUSTED_HOST_ENABLED=true）"
            )
        elif "*" in trusted_cfg.hosts:
            logger.warning("⚠️  [安全提示] TrustedHost 允许所有主机名，建议指定明确的主机名列表")


# 记录配置信息
_log_middleware_info()
