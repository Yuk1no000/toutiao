from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models.news import Category, News

from cache import news_cache

from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await news_cache.get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # 写入缓存
    if categories:
        categories_set = jsonable_encoder(categories)
        await news_cache.set_cached_categories(categories_set)

    # 返回数据
    return categories


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 尝试从缓存中获取数据
    page = skip // limit + 1
    cached_news_list = await news_cache.get_cache_news_list(category_id, page, limit)
    if cached_news_list:
        # cached_news_list是列表，需要转换成ORM
        return [News(**item) for item in cached_news_list]

    # 查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换 字典才能写入缓存
        # ORM转成Pydantic，再转成字典
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await news_cache.set_cached_news_list(category_id, skip, limit, news_data)

    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    # 查询的是指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，所以用scalar_one


async def get_news_detail(db: AsyncSession, news_id: int):
    # 先尝试从缓存中获取数据
    cached_news_detail = await news_cache.get_cached_news_detail(news_id)
    if cached_news_detail:
        return News(**cached_news_detail)

    # 获取新闻详情
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()

    # 写入缓存
    if news_detail:
        news_data = jsonable_encoder(news_detail)
        await news_cache.set_cached_news_detail(news_id, news_data)
    return news_detail


async def increase_news_views(db: AsyncSession, news_id: int):
    """
    增加新闻浏览量，并在更新后清除相关缓存
    """
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新成功后，清除该新闻的详情缓存（因为views字段变了）
    if result.rowcount == 1:
        await news_cache.delete_news_detail(news_id)
        return True
    return False


async def get_related_news(db: AsyncSession, category_id: int, news_id: int):
    """
    获取相关推荐新闻，带缓存策略
    """
    # 先尝试从缓存中获取数据
    cached_related = await news_cache.get_cached_related_news(news_id, category_id)
    if cached_related:
        return cached_related

    # 获取相关新闻
    stmt = select(News).where(News.category_id == category_id, News.id != news_id).order_by(func.rand()).limit(5)
    result = await db.execute(stmt)
    related_news = result.scalars().all()

    # 构建返回数据
    related_data = [{
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time.strftime("%Y-%m-%d %H:%M") if news.publish_time else None,
        "categoryId": news.category_id,
        "views": news.views
    } for news in related_news]

    # 写入缓存
    if related_data:
        await news_cache.cache_related_news(news_id, category_id, related_data)

    return related_data
