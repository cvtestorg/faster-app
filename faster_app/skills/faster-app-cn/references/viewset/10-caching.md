# 缓存

## 基础缓存

### 启用缓存

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300  # 缓存 5 分钟
```

## 缓存行为

### 自动缓存

以下方法自动缓存：
- `list()` - 列表查询
- `retrieve()` - 单个资源查询

### 自动失效

以下操作自动清除缓存：
- `create()` - 创建资源
- `update()` - 更新资源
- `destroy()` - 删除资源

## 自定义缓存键

### 基于用户

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300
    
    def get_cache_key(self, action: str, **kwargs) -> str:
        if action == "list":
            user_id = self.request.state.user.get("user_id", "anon")
            return f"articles_list_{user_id}"
        return super().get_cache_key(action, **kwargs)
```

### 基于查询参数

```python
class ArticleViewSet(ModelViewSet):
    def get_cache_key(self, action: str, **kwargs) -> str:
        if action == "list":
            status = self.request.query_params.get("status", "all")
            page = self.request.query_params.get("page", "1")
            return f"articles_list_{status}_{page}"
        return super().get_cache_key(action, **kwargs)
```

## 手动缓存控制

### 清除特定缓存

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    cache_timeout = 300
    
    @action(detail=True, methods=["POST"])
    async def publish(self, request: Request, pk: str):
        article = await self.get_object(pk)
        article.status = "published"
        await article.save()
        
        # 清除列表缓存
        self.clear_cache("list")
        
        return {"status": "published"}
```

### 预热缓存

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def warm_cache(self, request: Request):
        """预热热门文章缓存"""
        articles = await self.model.filter(
            is_featured=True
        ).limit(10)
        
        # 缓存每篇文章
        for article in articles:
            cache_key = self.get_cache_key("retrieve", pk=article.id)
            await self.set_cache(cache_key, article)
        
        return {"status": "cache warmed"}
```

## 禁用缓存

### 整个 ViewSet

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 0  # 禁用缓存
```

### 特定操作

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300
    
    @action(detail=False, methods=["GET"])
    async def realtime_stats(self, request: Request):
        """实时统计，不使用缓存"""
        # 此方法不会被缓存
        pass
```

## 缓存策略

### 短缓存（热数据）

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 60  # 1 分钟
    # 适用于经常变化的数据
```

### 长缓存（冷数据）

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 3600  # 1 小时
    # 适用于很少变化的数据
```

### 永久缓存

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 86400 * 30  # 30 天
    # 适用于几乎不变的数据
```

## 条件缓存

### 基于用户角色

```python
class ArticleViewSet(ModelViewSet):
    def get_cache_timeout(self, action: str) -> int:
        user = self.request.state.user
        if user.get("role") == "admin":
            return 0  # 管理员不缓存
        return 300  # 普通用户缓存 5 分钟
```

### 基于数据状态

```python
class ArticleViewSet(ModelViewSet):
    async def retrieve(self, request: Request, pk: str):
        article = await self.get_object(pk)
        
        # 已发布的文章缓存更长时间
        if article.status == "published":
            self.cache_timeout = 3600
        else:
            self.cache_timeout = 60
        
        return await super().retrieve(request, pk)
```

## 最佳实践

1. **合理设置超时**：根据数据更新频率
2. **细粒度缓存键**：包含相关查询参数
3. **及时清除**：数据变更时清除相关缓存
4. **监控命中率**：跟踪缓存效果
5. **避免缓存雪崩**：使用随机化的过期时间
