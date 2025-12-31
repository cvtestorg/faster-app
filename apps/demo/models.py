from tortoise import fields

from faster_app.models.base import DateTimeModel, StatusModel, UUIDModel


class DemoModel(UUIDModel, DateTimeModel, StatusModel):
    """demo model"""

    name = fields.CharField(max_length=255)

    class Meta:
        app = "models"  # 指定模型所属的 app，对应 TORTOISE_ORM 配置中的 "models" app
        table = "demo"
        table_description = "demo model"

    def __str__(self):
        return self.name
