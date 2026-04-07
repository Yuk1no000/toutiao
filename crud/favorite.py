from models.favorite import Favorite
from models.users import User
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News


async def is_news_favorite(new_id: int, user: User, db: AsyncSession):
    query = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == new_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def add_news_favorite(new_id: int, user: User, db: AsyncSession):
    favorite = Favorite(user_id=user.id, news_id=new_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def delete_news_favorite(new_id: int, user: User, db: AsyncSession):
    query = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == new_id)
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()
    if favorite is None:
        return False
    await db.delete(favorite)
    await db.commit()
    return True


async def get_favorite_list(
        page: int,
        page_size: int,
        user: User,
        db: AsyncSession
):
    count_query = select(func.count()).where(Favorite.user_id == user.id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user.id)
             .offset(offset).limit(page_size)
             .order_by(Favorite.created_at.desc())
             )
    result = await db.execute(query)
    return total, result.all()


async def clear_favorite(user: User, db: AsyncSession):
    stmt = delete(Favorite).where(Favorite.user_id == user.id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
