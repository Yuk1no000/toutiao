from datetime import datetime

from sqlalchemy import select, func, join, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from models.history import History

from models.news import News


# 添加浏览记录：检查是否浏览过当前新闻，
#               是 -》 更新浏览时间
#               否 -》 添加历史记录
async def add_history(
        news_id: int,
        user: User,
        db: AsyncSession
):
    query = select(History).where(news_id == History.news_id, History.user_id == user.id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user.id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


async def get_history_list(
        page: int,
        page_size: int,
        user: User,
        db: AsyncSession
):
    count_query = select(func.count()).where(History.user_id == user.id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (select(News, History.view_time, History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user.id).offset(offset).limit(page_size).order_by(History.view_time.desc()))
    result = await db.execute(query)
    return total, result.all()


async def delete_one_history(
        news_id: int,
        user: User,
        db: AsyncSession
):
    stmt = delete(History).where(History.user_id == user.id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def clear_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
