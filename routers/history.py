from fastapi import APIRouter, Query, Depends, HTTPException
from crud import history

from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from utils.auth import get_current_user

from config.db_conf import get_db

from utils.response import success_response

from schemas.history import HistoryAddRequest

from schemas.history import HistoryListResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(data.news_id, user, db)
    return success_response(
        message="添加历史记录成功",
        data=result
    )


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    total, rows = await history.get_history_list(page, page_size, user, db)
    has_more = total > page * page_size
    history_list = [
        {
            **news.__dict__,
            "view_time": view_time,
            "history_id": history_id
        } for news, view_time, history_id in rows
    ]
    return success_response(
        message="获取历史记录成功",
        data=HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    )


@router.delete("/delete/{history_id}")
async def delete_one_history(
        history_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.delete_one_history(history_id, user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.clear_history(db, user.id)
    return success_response(message=f"清空了{result}条历史记录")
