from datetime import datetime
from typing import List

from pydantic import Field, BaseModel, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    """
    收藏添加响应数据模型
    """
    news_id: int = Field(..., alias="newsId", description="新闻ID")


class HistoryNewsItemResponse(NewsItemBase):
    """
    收藏新闻列表项响应数据模型
    """
    view_time: datetime = Field(alias="viewTime")
    history_id: int = Field(alias="historyId")

    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 模型属性中取值
    )


class HistoryListResponse(BaseModel):
    """
    收藏列表响应数据模型
    """
    list: List[HistoryNewsItemResponse] = Field(..., description="收藏列表")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多")
    total: int = Field(..., description="总条数")

    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 模型属性中取值
    )
