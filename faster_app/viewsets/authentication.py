"""
认证系统

提供用户认证功能，支持多种认证方式。
"""

from abc import ABC, abstractmethod
from typing import Any

from fastapi import Request
from fastapi.security import HTTPBearer


class BaseAuthentication(ABC):
    """
    认证基类

    所有认证类都应继承此类，实现认证逻辑。
    """

    @abstractmethod
    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        """
        认证用户

        Args:
            request: FastAPI 请求对象

        Returns:
            (user, token) 元组，如果认证失败返回 None

        Note:
            - user: 认证后的用户对象
            - token: 认证令牌（可选，用于某些认证方式）
        """
        pass


class NoAuthentication(BaseAuthentication):
    """
    不进行认证

    所有请求都允许，不设置用户信息。
    """

    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        return None


class JWTAuthentication(BaseAuthentication):
    """
    JWT 认证

    从 Authorization header 中提取 JWT token 并验证。
    """

    def __init__(self, secret_key: str | None = None, algorithm: str = "HS256"):
        """
        初始化 JWT 认证

        Args:
            secret_key: JWT 密钥，如果为 None 则从配置中读取
            algorithm: JWT 算法，默认 HS256
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()

    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        """
        从 JWT token 中认证用户

        Args:
            request: FastAPI 请求对象

        Returns:
            (user, token) 元组，如果认证失败返回 None
        """
        try:
            import jwt

            from faster_app.settings import configs

            # 从 Authorization header 获取 token
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None

            # 提取 Bearer token
            if authorization.startswith("Bearer "):
                token = authorization[7:]
            else:
                return None

            # 验证 token
            secret_key = self.secret_key or getattr(configs, "SECRET_KEY", None)
            if not secret_key:
                return None

            try:
                payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None

            # 从 payload 中获取用户信息
            # 这里假设 payload 中包含 user_id 或 user 信息
            # 实际使用时需要根据 JWT payload 结构调整
            user_id = payload.get("user_id") or payload.get("sub")
            if not user_id:
                return None

            # 创建用户对象（简化版，实际应该从数据库查询）
            # 这里返回一个简单的用户对象，实际使用时需要根据需求调整
            user_data = {
                "id": user_id,
                "username": payload.get("username"),
                "is_admin": payload.get("is_admin", False),
                "is_superuser": payload.get("is_superuser", False),
                "role": payload.get("role"),
            }
            user = type("User", (), user_data)()

            return (user, token)

        except ImportError:
            # 如果没有安装 PyJWT，返回 None
            return None
        except Exception:
            return None


class TokenAuthentication(BaseAuthentication):
    """
    Token 认证

    从 Authorization header 或查询参数中提取 token 并验证。
    """

    def __init__(self, token_header: str = "Authorization", token_param: str = "token"):
        """
        初始化 Token 认证

        Args:
            token_header: Token header 名称，默认 "Authorization"
            token_param: Token 查询参数名称，默认 "token"
        """
        self.token_header = token_header
        self.token_param = token_param

    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        """
        从 token 中认证用户

        Args:
            request: FastAPI 请求对象

        Returns:
            (user, token) 元组，如果认证失败返回 None

        Note:
            实际使用时需要实现 token 验证逻辑，这里只是示例
        """
        # 从 header 获取 token
        token = request.headers.get(self.token_header)
        if token and token.startswith("Token "):
            token = token[6:]

        # 从查询参数获取 token
        if not token:
            token = request.query_params.get(self.token_param)

        if not token:
            return None

        # Token 验证逻辑需要根据实际需求实现
        # 建议的实现方式：
        # 1. 从数据库查询 token 记录
        # 2. 验证 token 是否有效（未过期、未撤销等）
        # 3. 获取关联的用户信息
        # 4. 返回 (user, token) 元组
        #
        # 示例实现：
        # from faster_app.models import Token
        # token_obj = await Token.get_or_none(token=token, is_active=True)
        # if token_obj and not token_obj.is_expired():
        #     user = await token_obj.user
        #     return (user, token)

        return None


class SessionAuthentication(BaseAuthentication):
    """
    Session 认证

    从 session 中获取用户信息。
    """

    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        """
        从 session 中认证用户

        Args:
            request: FastAPI 请求对象

        Returns:
            (user, None) 元组，如果认证失败返回 None

        Note:
            实际使用时需要实现 session 管理逻辑，这里只是示例
        """
        # 检查 session 中是否有用户信息
        if hasattr(request, "session"):
            user_id = request.session.get("user_id")
            if user_id:
                # Session 认证需要根据实际需求实现
                # 建议的实现方式：
                # 1. 从数据库查询用户
                # 2. 验证用户是否仍然有效（未删除、未禁用等）
                # 3. 返回 (user, None) 元组
                #
                # 示例实现：
                # from faster_app.models import User
                # user = await User.get_or_none(id=user_id, is_active=True)
                # if user:
                #     return (user, None)
                pass

        return None
