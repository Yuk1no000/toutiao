from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    """
    收藏检查响应数据模型
    """
    is_favorite: bool = Field(..., alias="isFavorite", description="是否已收藏")


class FavoriteAddRequest(BaseModel):
    """
    收藏添加响应数据模型
    """
    news_id: int = Field(..., alias="newsId", description="新闻ID")


# 规划两个类 - 一个是新闻模型类(base.py)，一个是收藏模型类
class FavoriteNewsItemResponse(NewsItemBase):
    """
    收藏新闻项响应数据模型
    """
    favorite_time: datetime = Field(..., alias="favoriteTime", description="收藏时间")
    favorite_id: int = Field(..., alias="favoriteId", description="收藏ID")

    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 模型属性中取值
    )


class FavoriteListResponse(BaseModel):
    """
    收藏列表响应数据模型
    """
    list: List[FavoriteNewsItemResponse] = Field(..., description="收藏列表")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多")
    total: int = Field(..., description="总条数")

    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 模型属性中取值
    )
