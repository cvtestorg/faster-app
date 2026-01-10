# 权限

## 内置权限

### IsAuthenticated

要求用户已认证：

```python
from faster_app.viewsets.permissions import IsAuthenticated

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    # 所有操作都需要认证
```

### AllowAny

允许任何人访问：

```python
from faster_app.viewsets.permissions import AllowAny

class ArticleViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    # 所有操作都公开
```

### IsAdminUser

要求管理员权限：

```python
from faster_app.viewsets.permissions import IsAdminUser

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    # 仅管理员可访问
```

## 按操作设置权限

不同操作使用不同权限：

```python
class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]  # 默认
    
    permission_classes_by_action = {
        "list": [AllowAny],            # 公开列表
        "retrieve": [AllowAny],        # 公开查看
        "create": [IsAuthenticated],   # 需要认证才能创建
        "update": [IsOwner],           # 仅所有者可更新
        "destroy": [IsAdminUser],      # 仅管理员可删除
    }
```

## 自定义权限

### 所有者权限

```python
from faster_app.viewsets.permissions import BasePermission
from fastapi import Request

class IsOwner(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        if not obj:
            return True  # 允许列表/创建
        
        # 检查用户是否拥有该对象
        user_id = request.state.user.get("user_id")
        return obj.owner_id == user_id
```

### 角色权限

```python
class CanPublish(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        user = request.state.user
        return user.get("role") in ["editor", "admin"]
```

### 基于字段的权限

```python
class CanEditStatus(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        if request.method != "PUT":
            return True
        
        data = await request.json()
        if "status" in data:
            # 只有管理员可以修改状态
            user = request.state.user
            return user.get("role") == "admin"
        return True
```

## 组合权限

多个权限同时检查（AND）：

```python
class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    # 必须同时满足：已认证 AND 是所有者
```

## 自定义操作权限

为特定操作设置权限：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAdminUser]
    )
    async def feature(self, request: Request, pk: str):
        """仅管理员可以推荐文章"""
        article = await self.get_object(pk)
        article.is_featured = True
        await article.save()
        return {"status": "featured"}
```

## 权限检查时机

权限在以下时机检查：

1. **请求开始时** - 检查基础权限
2. **获取对象后** - 检查对象级权限（如 IsOwner）
3. **自定义操作前** - 检查操作特定权限
