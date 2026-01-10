# 认证

## JWT 认证

### 基础使用

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.authentication import JWTAuthentication

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    
    model = Article
    schema = ArticleResponse
```

### JWT 配置

```bash
# .env
SECRET_KEY=你的密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 生成 Token

```python
from datetime import datetime, timedelta
import jwt
from faster_app.settings import configs

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=configs.jwt.access_token_expire_minutes
    )
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(
        payload,
        configs.jwt.secret_key,
        algorithm=configs.jwt.algorithm
    )
```

### 使用 Token

```bash
# HTTP 请求头
Authorization: Bearer <token>
```

## 自定义认证

### API Key 认证

```python
from faster_app.viewsets.authentication import BaseAuthentication
from fastapi import Request

class APIKeyAuthentication(BaseAuthentication):
    async def authenticate(self, request: Request) -> dict | None:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None
        
        # 验证 API key
        user = await verify_api_key(api_key)
        if user:
            return {
                "user_id": user.id,
                "username": user.username
            }
        return None

class ArticleViewSet(ModelViewSet):
    authentication_classes = [APIKeyAuthentication]
```

### Session 认证

```python
class SessionAuthentication(BaseAuthentication):
    async def authenticate(self, request: Request) -> dict | None:
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None
        
        # 验证 session
        user = await get_user_from_session(session_id)
        if user:
            return {"user_id": user.id}
        return None
```

## 多重认证

按顺序尝试多种认证方式：

```python
class ArticleViewSet(ModelViewSet):
    authentication_classes = [
        JWTAuthentication,
        APIKeyAuthentication,
        SessionAuthentication
    ]
    # 先尝试 JWT，然后 API key，最后 Session
```

## 访问认证信息

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def my_articles(self, request: Request):
        """获取当前用户的文章"""
        user_id = request.state.user.get("user_id")
        articles = await self.model.filter(author_id=user_id)
        return articles
```

## 可选认证

某些操作可选认证：

```python
from faster_app.viewsets.permissions import AllowAny

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    
    permission_classes_by_action = {
        "list": [AllowAny],  # 列表无需认证
        "create": [IsAuthenticated],  # 创建需要认证
    }
```
