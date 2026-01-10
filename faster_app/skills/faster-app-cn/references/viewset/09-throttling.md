# 限流

## 基础限流

### 用户和匿名限流

```python
from faster_app.viewsets.throttling import (
    UserRateThrottle,
    AnonRateThrottle,
)

class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
```

### 配置速率

```bash
# .env
THROTTLE_RATES={"user":"100/hour","anon":"20/hour"}
```

## 速率格式

```bash
# 每秒
"10/second"

# 每分钟
"60/minute"

# 每小时
"100/hour"

# 每天
"1000/day"
```

## 作用域限流

### 配置作用域

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]
    throttle_scope = "articles"
```

```bash
# .env
THROTTLE_RATES={"articles":"50/hour"}
```

### 多个作用域

```bash
THROTTLE_RATES={
  "user":"100/hour",
  "anon":"20/hour",
  "articles":"50/hour",
  "comments":"30/hour",
  "uploads":"10/hour"
}
```

## 按操作限流

不同操作使用不同限流：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]
    
    @action(
        detail=False,
        methods=["POST"],
        throttle_classes=[AnonRateThrottle]
    )
    async def newsletter(self, request: Request):
        """此操作使用更严格的限流"""
        pass
```

## 自定义限流

### 自定义速率

```python
from faster_app.viewsets.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    scope = "burst"
    rate = "10/minute"  # 硬编码速率
```

### 自定义缓存键

```python
class CustomThrottle(SimpleRateThrottle):
    scope = "custom"
    
    def get_cache_key(self, request: Request, view) -> str:
        # 基于 IP + 用户的组合键
        user_id = request.state.user.get("user_id", "anon")
        ip = request.client.host
        return f"throttle_custom_{user_id}_{ip}"
```

### 动态速率

```python
class DynamicRateThrottle(SimpleRateThrottle):
    def get_rate(self, view):
        # 根据用户等级返回不同速率
        user = self.request.state.user
        if user.get("is_premium"):
            return "1000/hour"
        return "100/hour"
```

## 限流响应

当超过限流时，返回 429 状态码：

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

## 禁用限流

### 整个 ViewSet

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = []  # 禁用所有限流
```

### 特定操作

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]
    
    @action(detail=False, methods=["GET"], throttle_classes=[])
    async def public_stats(self, request: Request):
        """此操作无限流"""
        pass
```

## 最佳实践

1. **合理设置速率**：根据实际负载能力
2. **区分用户类型**：付费用户更高限额
3. **关键操作限流**：如登录、注册、上传
4. **监控限流**：记录被限流的请求
5. **友好提示**：告知用户何时可以重试
