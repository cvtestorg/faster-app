"""异常基类"""

from http import HTTPStatus
from typing import Any


class FasterAppError(Exception):
    """应用统一异常基类
    
    所有应用异常都应继承此类，确保统一的错误响应格式。
    
    Attributes:
        message: 错误消息
        code: 业务错误码
        status_code: HTTP 状态码
        error_detail: 详细错误信息
        data: 附加数据
    """
    
    default_status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    default_message: str = "操作失败"
    
    def __init__(
        self,
        message: str | None = None,
        *,
        code: int | None = None,
        status_code: int | None = None,
        error_detail: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code or self.default_status_code
        self.message = message or self.default_message
        self.code = code or self.status_code
        self.error_detail = error_detail
        self.data = data
        super().__init__(self.message)
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code}, "
            f"status_code={self.status_code})"
        )
    
    def to_dict(self, *, include_detail: bool = True) -> dict[str, Any]:
        """转换为字典格式
        
        Args:
            include_detail: 是否包含详细错误信息
        
        Returns:
            错误响应字典
        """
        result: dict[str, Any] = {
            "success": False,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }
        
        if include_detail and self.error_detail:
            result["error_detail"] = self.error_detail
        
        return result
