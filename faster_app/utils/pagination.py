"""
统一的分页功能模块

此模块提供了基于 fastapi-pagination 的统一分页方案，简化开发者使用分页功能的复杂度。

特性:
- 支持多种数据源的分页（列表、Tortoise ORM 查询）
- 提供便捷的参数和响应模型
- 遵循 FastAPI 最佳实践
- 开箱即用，学习成本低

Usage:
    from fastapi import APIRouter, Depends
    from faster_app.utils.pagination import Page, Params, paginate
    from faster_app.apps.demo.models import DemoModel

    router = APIRouter()

    # 示例 1: 对列表进行分页
    @router.get("/items", response_model=Page[dict])
    async def list_items(params: Params = Depends()):
        items = [{"id": i, "name": f"Item {i}"} for i in range(100)]
        return paginate(items, params)

    # 示例 2: 对 Tortoise ORM 查询进行分页
    @router.get("/demos", response_model=Page[DemoSchema])
    async def list_demos(params: Params = Depends()):
        return await paginate(DemoModel.all(), params)
"""

from collections.abc import Sequence
from typing import TypeVar

from fastapi import Query
from fastapi_pagination import Page as _Page
from fastapi_pagination import Params as _Params
from fastapi_pagination import paginate as _paginate
from fastapi_pagination.ext.tortoise import apaginate as _apaginate
from tortoise.queryset import QuerySet

T = TypeVar("T")


# 重新导出 Page 和 Params，方便使用
Page = _Page
Params = _Params


class CustomParams(_Params):
    """
    自定义分页参数

    可以根据项目需求调整默认值和最大值
    默认: page=1, size=20, max_size=100
    """

    size: int = Query(20, ge=1, le=100, description="每页数量")


def paginate(items: Sequence[T] | QuerySet, params: _Params | None = None) -> Page[T]:
    """
    统一的分页函数

    自动识别数据源类型并应用相应的分页策略:
    - 对于普通列表/序列: 使用内存分页，返回 Page[T]
    - 对于 Tortoise ORM QuerySet: 使用数据库分页，返回 Awaitable[Page[T]]

    ⚠️ 重要提示：
    - 当传入 QuerySet 时，此函数返回一个 awaitable，必须使用 await 调用
    - 当传入列表/序列时，此函数直接返回结果，不需要 await

    Args:
        items: 要分页的数据源（列表或 Tortoise QuerySet）
        params: 分页参数（page, size），如果为 None 则使用默认值

    Returns:
        Page[T]: 分页结果，包含 items 和分页元数据
                 (当传入 QuerySet 时返回 Awaitable[Page[T]])

    Example:
        # 对列表分页（同步）
        items = [1, 2, 3, 4, 5]
        result = paginate(items, params)

        # 对 QuerySet 分页（异步，需要 await）
        query = User.all()
        result = await paginate(query, params)

    Note:
        如果只需要数据库查询分页，推荐直接使用 apaginate() 函数，
        它有明确的异步签名。
    """
    # 如果是 Tortoise ORM QuerySet，返回 awaitable
    if isinstance(items, QuerySet):
        return _apaginate(items, params)

    # 否则直接分页
    return _paginate(items, params)


# 便捷别名
async def apaginate(query: QuerySet, params: _Params | None = None) -> Page[T]:
    """
    异步分页函数（专门用于 Tortoise ORM）

    这是 paginate 函数的异步版本，专门用于 Tortoise ORM QuerySet。

    Args:
        query: Tortoise ORM QuerySet
        params: 分页参数（page, size）

    Returns:
        Page[T]: 分页结果

    Example:
        from faster_app.apps.demo.models import DemoModel

        query = DemoModel.filter(status=1).order_by("-created_at")
        result = await apaginate(query)
    """
    return await _apaginate(query, params)


__all__ = [
    "Page",
    "Params",
    "CustomParams",
    "paginate",
    "apaginate",
]
