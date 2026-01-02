from faster_app.models.discover import discover_models
from faster_app.settings.config import configs

TORTOISE_ORM = {
    "connections": {"default": configs.DB_URL},
    "apps": {
        "models": {
            "models": discover_models(),
            "default_connection": "default",
        },
    },
}
