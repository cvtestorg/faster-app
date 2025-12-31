# ViewSet 实例管理和配置管理优化

## 一、ViewSet 实例管理优化

### 问题分析

**原始实现**：
- ViewSet 实例在路由注册时创建（`get_router()` 方法中）
- 所有请求共享同一个 ViewSet 实例
- 如果 ViewSet 有状态，会导致并发问题

**优化方案**：
- 每次请求创建新的 ViewSet 实例
- 确保 ViewSet 是无状态的
- 提高并发安全性

### 实现细节

#### 1. 路由注册优化

**修改前**：
```python
def get_router(self) -> APIRouter:
    router = APIRouter(prefix=self.prefix, tags=self.tags)
    viewset_instance = self.viewset_class()  # 创建一次，所有请求共享
    
    # 注册路由时使用共享实例
    @router.get("/")
    async def list_view(request: Request, pagination: Params = Depends()):
        return await viewset_instance.list(request, pagination)  # 共享实例
```

**修改后**：
```python
def get_router(self) -> APIRouter:
    router = APIRouter(prefix=self.prefix, tags=self.tags)
    
    # 只创建临时实例用于类型检查和获取序列化器类
    temp_instance = self.viewset_class()
    
    # 注册路由时传递类，而不是实例
    @router.get("/")
    async def list_view(request: Request, pagination: Params = Depends()):
        viewset = viewset_class()  # 每次请求创建新实例
        return await viewset.list(request, pagination)
```

#### 2. 确保 ViewSet 无状态

ViewSet 的所有属性都应该是：
- **类属性**：配置信息（如 `model`, `permission_classes`）
- **请求相关**：通过 `request` 参数传递
- **不存储状态**：不在实例中存储请求相关的状态

**示例**：
```python
class DemoViewSet(ModelViewSet):
    # ✅ 类属性 - 配置信息
    model = DemoModel
    permission_classes = [IsAuthenticated]
    
    # ❌ 不要这样做 - 实例属性存储状态
    def __init__(self):
        self.current_user = None  # 错误：会污染状态
    
    # ✅ 正确做法 - 从 request 获取
    async def list(self, request: Request, ...):
        user = request.state.user  # 从 request 获取
```

### 优势

1. **并发安全**：每个请求有独立的 ViewSet 实例，不会相互干扰
2. **无状态设计**：符合 RESTful API 设计原则
3. **易于测试**：每个请求独立，测试更容易
4. **内存管理**：请求结束后实例可被回收

### 性能考虑

- **创建开销**：每次请求创建新实例会有轻微开销
- **优化**：ViewSet 初始化主要是设置类属性，开销很小
- **权衡**：为了并发安全，这个开销是值得的

## 二、配置管理优化

### 问题分析

**原始实现**：
- 限流速率硬编码在代码中
- 修改配置需要修改代码
- 不同环境使用不同配置困难

**优化方案**：
- 将限流配置提取到 `settings.py`
- 支持从环境变量读取
- 提供默认值和作用域配置

### 实现细节

#### 1. 配置文件添加

**`faster_app/settings/builtins/settings.py`**：
```python
class DefaultSettings(BaseSettings):
    # 限流配置
    THROTTLE_RATES: dict[str, str] = {
        "user": "100/hour",  # 已认证用户默认限流速率
        "anon": "20/hour",   # 匿名用户默认限流速率
        "default": "100/hour",  # 默认限流速率
    }
```

#### 2. 限流类从配置读取

**`faster_app/viewsets/throttling.py`**：
```python
from faster_app.settings import configs

class SimpleRateThrottle(BaseThrottle):
    def get_rate(self, view: Any) -> str:
        # 如果直接指定了 rate，优先使用
        if self.rate:
            return self.rate
        
        # 如果有 scope，从配置中获取速率
        if self.scope:
            throttle_rates = getattr(configs, "THROTTLE_RATES", {})
            if self.scope in throttle_rates:
                return throttle_rates[self.scope]
        
        # 如果 ViewSet 有 throttle_scope，从配置中获取
        if hasattr(view, "throttle_scope") and view.throttle_scope:
            throttle_rates = getattr(configs, "THROTTLE_RATES", {})
            if view.throttle_scope in throttle_rates:
                return throttle_rates[view.throttle_scope]
        
        # 使用默认速率
        throttle_rates = getattr(configs, "THROTTLE_RATES", {})
        return throttle_rates.get("default", "")
```

### 使用示例

#### 1. 使用默认配置

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 使用默认配置（从 settings.THROTTLE_RATES 读取）
    throttle_classes = [
        UserRateThrottle(),  # 使用 "user" 作用域的配置
        AnonRateThrottle(),  # 使用 "anon" 作用域的配置
    ]
```

#### 2. 使用自定义作用域

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 使用自定义作用域
    throttle_scope = "demo"  # 从配置中读取 "demo" 作用域的速率
    throttle_classes = [ScopedRateThrottle()]
```

#### 3. 直接指定速率（覆盖配置）

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 直接指定速率，覆盖配置
    throttle_classes = [
        UserRateThrottle(rate="200/hour"),  # 直接指定，不使用配置
    ]
```

#### 4. 环境变量配置

**`.env` 文件**：
```env
# 限流配置（JSON 格式）
THROTTLE_RATES={"user": "200/hour", "anon": "50/hour", "demo": "500/hour"}
```

### 配置优先级

1. **直接指定**：`UserRateThrottle(rate="200/hour")` - 最高优先级
2. **ViewSet 作用域**：`throttle_scope = "demo"` - 从配置读取
3. **限流类作用域**：`scope = "user"` - 从配置读取
4. **默认配置**：`"default"` - 最低优先级

### 优势

1. **灵活性**：支持代码配置、配置文件、环境变量
2. **环境隔离**：不同环境可以使用不同配置
3. **易于维护**：配置集中管理，修改方便
4. **向后兼容**：仍然支持直接指定速率

## 三、最佳实践

### 1. ViewSet 设计原则

- ✅ **无状态**：不在实例中存储请求相关状态
- ✅ **类属性配置**：使用类属性定义配置
- ✅ **请求参数**：从 `request` 参数获取请求信息
- ❌ **避免实例状态**：不要存储用户、会话等状态

### 2. 配置管理原则

- ✅ **集中配置**：在 `settings.py` 中统一管理
- ✅ **环境变量**：支持通过环境变量覆盖
- ✅ **默认值**：提供合理的默认值
- ✅ **文档化**：在配置文件中添加注释说明

### 3. 限流配置建议

```python
# 开发环境
THROTTLE_RATES = {
    "user": "1000/hour",
    "anon": "500/hour",
}

# 生产环境
THROTTLE_RATES = {
    "user": "100/hour",
    "anon": "20/hour",
    "api": "1000/hour",
    "admin": "10000/hour",
}
```

## 四、总结

通过这两项优化：

1. **ViewSet 实例管理**：
   - ✅ 每次请求创建新实例
   - ✅ 确保无状态性
   - ✅ 提高并发安全性

2. **配置管理**：
   - ✅ 配置集中管理
   - ✅ 支持环境变量
   - ✅ 灵活的作用域配置

这些优化提高了系统的可维护性、灵活性和安全性。
