from tortoise import fields

from faster_app.models.base import DateTimeModel, StatusModel, UUIDModel


class DemoModel(UUIDModel, DateTimeModel, StatusModel):
    """demo model"""

    name = fields.CharField(max_length=255)

    class Meta:
        table = "demo"
        table_description = "demo model"

    def __str__(self):
        return self.name
