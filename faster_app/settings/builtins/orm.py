from faster_app.models.discover import ModelDiscover
from faster_app.settings import logger
from faster_app.settings.config import configs

# 发现所有模型并按 app 分组
models_discover = ModelDiscover().discover()

# 收集所有发现的模型路径
all_model_paths = []
for app_name, model_paths in models_discover.items():
    all_model_paths.extend(model_paths)

# 构建 Tortoise ORM 配置
# 将所有用户模型放在 "models" app 下, 这样 aerich 可以统一管理所有模型的迁移
# aerich.models 也在 "models" app 中, 用于存储迁移历史
apps_config = {
    "models": {
        "models": ["aerich.models"] + all_model_paths,
        "default_connection": "default",
    },
}

TORTOISE_ORM = {
    "connections": {"default": configs.database.url},
    "apps": apps_config,
}

logger.debug(f"Tortoise ORM config: {TORTOISE_ORM}")
