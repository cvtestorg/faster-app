# 速查表

## 快速开始

```bash
# 安装
uv add faster-app

# 创建应用
faster app demo

# 数据库
faster db migrate --name="init"
faster db upgrade

# 启动
faster server start
```

## 模型定义

```python
# 标准模型
class Article(UUIDModel, DateTimeModel):
    title: str = Field(..., max_length=200)
    content: str = Field(...)
    status: str = Field(default="draft")

# ForeignKey
author: fields.ForeignKeyField = fields.ForeignKeyField(
    "models.Author", related_name="articles", on_delete=fields.CASCADE
)

# ManyToMany
tags: fields.ManyToManyField = fields.ManyToManyField(
    "models.Tag", related_name="articles"
)
```

## 查询

```python
# 基础查询
await Article.all()
await Article.get(id=id)
await Article.filter(status="published")
await Article.filter(view_count__gt=100)

# 排序+限制
await Article.all().order_by("-created_at").limit(10)

# 预取关系
await Article.all().prefetch_related("author", "tags")
```

## ViewSet

```python
# 完整 CRUD
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_class = ArticleFilterSet
    search_fields = ["title"]
    ordering = ["-created_at"]

# 自定义操作
@action(detail=True, methods=["POST"])
async def publish(self, request, pk):
    ...
```

## 配置

```bash
# .env
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key
DB_URL=sqlite://db.sqlite
CORS_ALLOW_ORIGINS=["*"]
```

```python
# 访问配置
from faster_app.settings import configs

configs.debug
configs.server.host
configs.jwt.secret_key
```
