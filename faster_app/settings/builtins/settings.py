"""
应用配置文件
"""

from pydantic_settings import BaseSettings


class DefaultSettings(BaseSettings):
    """应用设置"""

    # 基础配置
    PROJECT_NAME: str = "Faster APP"
    VERSION: str = "0.0.1"
    DEBUG: bool = True  # 生产环境中应设置为 False, 可通过环境变量 DEBUG=false 覆盖

    # Server 配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API 配置
    API_V1_STR: str = "/api/v1"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DB_URL: str = "sqlite://db.sqlite"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "STRING"
    LOG_TO_FILE: bool = False  # 是否输出日志到文件
    LOG_FILE_PATH: str = "logs/app.log"  # 日志文件路径
    LOG_FILE_BACKUP_COUNT: int = 10  # 保留的备份文件数量（按天归档时，默认保留10天）

    # 路由验证配置
    VALIDATE_ROUTES: bool = True  # 是否启用路由冲突检测

    # 限流配置
    THROTTLE_RATES: dict[str, str] = {
        "user": "100/hour",  # 已认证用户默认限流速率
        "anon": "20/hour",  # 匿名用户默认限流速率
        "default": "100/hour",  # 默认限流速率
    }

    class Config:
        env_file = ".env"
        extra = "ignore"
