from faster_app.models.discover import ModelDiscover
from faster_app.settings import logger
from faster_app.settings.config import configs
from tortoise.backends.base.config_generator import expand_db_url

# 发现所有模型并按 app 分组
models_discover = ModelDiscover().discover()

# 收集所有发现的模型路径
all_model_paths = []
for _app_name, model_paths in models_discover.items():
    all_model_paths.extend(model_paths)

# 构建 Tortoise ORM 配置
# 将所有模型放在 "models" app 下，这样 aerich 可以统一追踪所有模型
apps_config = {
    "models": {
        "models": ["aerich.models"] + all_model_paths,
        "default_connection": "default",
    },
}

# 完全使用 credentials 配置方式
# 始终使用 expand_db_url() 解析 URL，确保所有官方支持的参数都被正确处理
# 这样可以确保 schema、minsize、maxsize、ssl 等参数都能正确传递
db_url = configs.database.url

try:
    # 使用 expand_db_url 解析 URL
    # 它会自动：
    # 1. 从 URL scheme 推断引擎类型
    # 2. 解析所有查询参数
    # 3. 根据 DB_LOOKUP["cast"] 进行类型转换
    # 4. 返回包含 engine 和 credentials 的配置
    connection_config = expand_db_url(db_url)

    # 获取 schema 参数用于日志记录
    schema = connection_config.get("credentials", {}).get("schema")
    engine = connection_config.get("engine")

    logger.info(
        f"使用 credentials 配置方式初始化数据库连接，"
        f"引擎: {engine}, "
        f"schema: {schema if schema else '未设置（使用默认）'}"
    )

    TORTOISE_ORM = {
        "connections": {"default": connection_config},
        "apps": apps_config,
    }
except Exception as e:
    # 如果解析失败，回退到 URL 字符串方式（保持兼容性）
    logger.warning(
        f"解析 DB_URL 失败: {e}，回退到 URL 字符串配置方式。"
        f"如果使用了 schema 等特殊参数，可能无法正常工作。"
    )
    TORTOISE_ORM = {
        "connections": {"default": db_url},
        "apps": apps_config,
    }

logger.debug(f"Tortoise ORM config: {TORTOISE_ORM}")
