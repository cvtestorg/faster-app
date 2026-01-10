# ViewSet Mixins

## Mixins 组合

通过组合 mixins 构建自定义 ViewSet：

```python
from faster_app.viewsets import (
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin
)

class ArticleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    # 自定义 ViewSet，仅包含 List + Create + Retrieve
    model = Article
    schema = ArticleResponse
```

## 可用的 Mixins

### ListModelMixin

提供列表查询功能：

```python
from faster_app.viewsets import GenericViewSet, ListModelMixin

class ArticleViewSet(ListModelMixin, GenericViewSet):
    model = Article
    schema = ArticleResponse
    
    # 生成端点：GET /articles/
```

### CreateModelMixin

提供创建功能：

```python
from faster_app.viewsets import GenericViewSet, CreateModelMixin

class ArticleViewSet(CreateModelMixin, GenericViewSet):
    model = Article
    create_schema = ArticleCreate
    
    # 生成端点：POST /articles/
```

### RetrieveModelMixin

提供单个资源查询：

```python
from faster_app.viewsets import GenericViewSet, RetrieveModelMixin

class ArticleViewSet(RetrieveModelMixin, GenericViewSet):
    model = Article
    schema = ArticleResponse
    
    # 生成端点：GET /articles/{id}/
```

### UpdateModelMixin

提供更新功能：

```python
from faster_app.viewsets import GenericViewSet, UpdateModelMixin

class ArticleViewSet(UpdateModelMixin, GenericViewSet):
    model = Article
    update_schema = ArticleUpdate
    
    # 生成端点：PUT /articles/{id}/
```

### DestroyModelMixin

提供删除功能：

```python
from faster_app.viewsets import GenericViewSet, DestroyModelMixin

class ArticleViewSet(DestroyModelMixin, GenericViewSet):
    model = Article
    
    # 生成端点：DELETE /articles/{id}/
```

## 常见组合模式

### 只读 + 创建

```python
class ArticleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    # 可以列表、创建、查看，但不能更新或删除
    pass
```

### 完全自定义

```python
class ArticleViewSet(GenericViewSet):
    # 不包含任何 mixin，完全自定义实现
    model = Article
    schema = ArticleResponse
    
    # 手动实现需要的方法
```
