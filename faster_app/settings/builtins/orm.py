from faster_app.models.discover import ModelDiscover
from faster_app.settings import logger
from faster_app.settings.config import configs

# 发现所有模型并按 app 分组
models_discover = ModelDiscover().discover()

# 构建 Tortoise ORM 配置
# "models" app 用于 aerich 迁移工具
apps_config = {
    "models": {
        "models": ["aerich.models"],
        "default_connection": "default",
    },
}

# 为每个发现的 app 添加配置
# 每个 app 只包含属于该 app 的模型
for app_name, model_paths in models_discover.items():
    apps_config[app_name] = {
        "models": model_paths,
        "default_connection": "default",
    }

TORTOISE_ORM = {
    "connections": {"default": configs.database.url},
    "apps": apps_config,
}

logger.debug(f"Tortoise ORM config: {TORTOISE_ORM}")
