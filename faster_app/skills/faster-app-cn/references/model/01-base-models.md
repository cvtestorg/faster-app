# 基础模型类

## UUIDModel

UUID 主键模型：

```python
from faster_app.models.base import UUIDModel

class Article(UUIDModel):
    title: str = Field(..., max_length=200)
    content: str = Field(...)
```

**提供功能：**
- `id` (UUID) - 自动生成的主键
- CRUD 方法：create, get, all, filter, save, delete

## DateTimeModel

自动时间戳跟踪：

```python
from faster_app.models.base import DateTimeModel

class Article(DateTimeModel):
    title: str = Field(...)
```

**提供字段：**
- `created_at` - 创建时间（自动）
- `updated_at` - 更新时间（自动）

## EnumModel

枚举字段支持：

```python
from faster_app.models.base import EnumModel
from enum import IntEnum

class PostStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1

class Post(EnumModel):
    status: int = Field(default=PostStatus.DRAFT)
    
    @property
    def status_name(self):
        return PostStatus(self.status).name
```

## ScopeModel

多租户支持：

```python
from faster_app.models.base import ScopeModel

class Article(ScopeModel):
    title: str = Field(...)
    
    class Meta:
        scope_field = "tenant_id"
```

**用法：**
```python
ScopeModel.set_scope("tenant_123")
articles = await Article.all()  # 自动过滤
```

## 组合使用

标准模式（推荐）：

```python
class Article(UUIDModel, DateTimeModel):
    """UUID + 时间戳"""
    title: str = Field(...)
```

多租户模式：

```python
class Article(UUIDModel, DateTimeModel, ScopeModel):
    """UUID + 时间戳 + 租户"""
    title: str = Field(...)
```
