from fastapi import APIRouter, Query, Depends, HTTPException

from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from utils.auth import get_current_user

from config.db_conf import get_db

from utils.response import success_response

from crud import favorite

from schemas.favorite import FavoriteCheckResponse, FavoriteListResponse

from crud.favorite import add_news_favorite
from schemas.favorite import FavoriteAddRequest

from crud.favorite import delete_news_favorite
from crud.favorite import clear_favorite

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def get_check(
        new_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    is_favorited = await favorite.is_news_favorite(new_id, user, db)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorited))


@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    favorite = await add_news_favorite(data.news_id, user, db)
    return success_response(
        message="添加收藏成功",
        data=favorite
    )


@router.delete("/remove")
async def delete_remove(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await delete_news_favorite(news_id, user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")
    return success_response(
        message="获取收藏列表成功",
    )


@router.get("/list")
async def get_favorite_list(
        page: int = 1,
        page_size: int = Query(10, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    total, result = await favorite.get_favorite_list(page, page_size, user, db)
    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id,
        } for news, favorite_time, favorite_id in result
    ]
    has_more = total > page * page_size
    return success_response(
        message="获取收藏列表成功",
        data=FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    )


@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await favorite.clear_favorite(user, db)
    return success_response(
        message=f"清空了{count}条收藏记录",
    )
