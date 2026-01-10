# ViewSet 基础

## 快速开始

```python
from faster_app.viewsets import ModelViewSet
from .models import Article
from .schemas import ArticleCreate, ArticleUpdate, ArticleResponse

class ArticleViewSet(ModelViewSet):
    model = Article                      # 必需：Tortoise 模型
    schema = ArticleResponse             # 必需：响应 schema
    create_schema = ArticleCreate        # 可选：创建 schema
    update_schema = ArticleUpdate        # 可选：更新 schema

# 注册路由
router = ArticleViewSet.as_router(prefix="/articles", tags=["文章"])
```

**生成的端点：**

- `GET /articles/` - 列出所有
- `POST /articles/` - 创建
- `GET /articles/{id}/` - 获取单个
- `PUT /articles/{id}/` - 更新
- `DELETE /articles/{id}/` - 删除

## 预构建的 ViewSet

### ModelViewSet - 完整 CRUD

```python
from faster_app.viewsets import ModelViewSet

class ArticleViewSet(ModelViewSet):
    # 包括：List + Create + Retrieve + Update + Destroy
    model = Article
    schema = ArticleResponse
```

### ReadOnlyModelViewSet - 只读

```python
from faster_app.viewsets import ReadOnlyModelViewSet

class ArticleViewSet(ReadOnlyModelViewSet):
    # 仅包括：List + Retrieve
    model = Article
    schema = ArticleResponse
```

## 自定义查询集

### 基础过滤

```python
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse

    def get_queryset(self):
        """仅返回已发布的文章"""
        return self.model.filter(status="published")
```

### 按操作过滤

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset_for_action(self, action: str):
        """不同操作使用不同的查询集"""
        if action == "list":
            return self.model.filter(status="published")
        return self.model.all()
```

### 基于用户过滤

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        """返回当前用户的文章"""
        user_id = self.request.state.user.get("user_id")
        return self.model.filter(author_id=user_id)
```
