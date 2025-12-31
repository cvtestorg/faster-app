"""
异常基类

定义统一的异常基类, 所有应用异常都应继承此类。
"""

from http import HTTPStatus


class FasterAppError(Exception):
    """Faster APP 统一异常基类

    所有应用异常都应继承此类, 确保统一的错误响应格式。

    Attributes:
        message: 错误消息
        code: 业务错误码 (默认与 HTTP 状态码相同)
        status_code: HTTP 状态码
        error_detail: 详细错误信息 (可选)
        data: 附加数据 (可选)
    """

    def __init__(
        self,
        message: str = "操作失败",
        code: int | None = None,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_detail: str | None = None,
        data: dict | None = None,
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            code: 业务错误码, 如果为 None 则使用 status_code
            status_code: HTTP 状态码
            error_detail: 详细错误信息
            data: 附加数据
        """
        self.message = message
        self.code = code if code is not None else status_code
        self.status_code = status_code
        self.error_detail = error_detail
        self.data = data
        super().__init__(self.message)

    def __str__(self) -> str:
        """返回异常字符串表示"""
        return f"{self.__class__.__name__}: {self.message}"

    def to_dict(self) -> dict:
        """转换为字典格式, 用于错误响应"""
        result = {
            "success": False,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }

        if self.error_detail:
            result["error_detail"] = self.error_detail

        return result
