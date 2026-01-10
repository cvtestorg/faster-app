# 迁移指南

## 从原生 FastAPI 迁移

### 1. 安装 Faster APP

```bash
uv add faster-app
```

### 2. 调整项目结构

```
# 原结构
main.py
models.py
routes.py

# 新结构  
apps/
  users/
    models.py
    routes.py
config/
  settings.py
.env
```

### 3. 迁移路由

**原代码：**
```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/users")
async def get_users():
    return []
```

**新代码：** 保持不变，自动发现！

### 4. 迁移模型

**原代码：**
```python
from tortoise.models import Model

class User(Model):
    id = fields.UUIDField(pk=True)
```

**新代码：**
```python
from faster_app.models.base import UUIDModel

class User(UUIDModel):
    # id 自动提供
    pass
```

### 5. 使用 ViewSet（可选）

```python
from faster_app.viewsets import ModelViewSet

class UserViewSet(ModelViewSet):
    model = User
    schema = UserResponse
```

## 从 Django REST Framework 迁移

### 相似概念

| DRF | Faster APP |
|-----|------------|
| ModelViewSet | ModelViewSet |
| Serializer | Pydantic Schema |
| permission_classes | permission_classes |
| authentication_classes | authentication_classes |
| filter_backends | filterset_class |

### 示例对比

**DRF：**
```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
```

**Faster APP：**
```python
class UserViewSet(ModelViewSet):
    model = User
    schema = UserResponse
    permission_classes = [IsAuthenticated]
```

## 版本升级

### 从 0.1.x 到 0.2.x

主要变更：
- 配置结构变为嵌套
- 中间件配置调整
- ViewSet 改进

迁移步骤：
1. 更新配置访问方式
2. 调整中间件配置  
3. 测试 API 功能
