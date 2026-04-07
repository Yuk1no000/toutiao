from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from crud import news_cache

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news_cache.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories
    }


@router.get("/list")
async def get_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, le=100, alias="pageSize"),
        db: AsyncSession = Depends(get_db),
):
    news_list = await news_cache.get_news_list(db, category_id, (page - 1) * page_size, page_size)
    total = await news.get_news_count(db, category_id)
    # （跳过的 + 当前列表里面的数量) < 总量
    has_more = (len(news_list) + (page - 1) * page_size) < total

    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more,
        }
    }


@router.get("/detail")
async def get_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_db),
):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news_cache.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    # 浏览量+1
    views_res = await news.increase_news_views(db, news_id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    # 相关新闻
    related_news = await news_cache.get_related_news(db, news_detail.category_id, news_id)
    return {
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
