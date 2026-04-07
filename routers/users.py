from fastapi import APIRouter, Depends, HTTPException

from config.db_conf import get_db
from schemas.users import UserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from crud import users

from starlette import status

from schemas.users import UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserUpdatePasswordRequest
from utils.response import success_response
from utils.auth import get_current_user

from models.users import User

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def user_register(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_db),
):
    #  注册逻辑：验证用户是否存在 -> 创建用户 → 生成 Token  → 响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(
        message="注册成功",
        data=response_data
    )


@router.post("/login")
async def user_login(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_db)
):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user)
    )
    return success_response(
        message="登录成功",
        data=response_data
    )


@router.get("/info")
async def get_user_info(
        user: User = Depends(get_current_user)
):
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )


@router.put("/update")
async def user_update(
        user_data: UserUpdateRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await users.update_user(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )


@router.put("/password")
async def user_password(
        user_data: UserUpdatePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.update_password(db, user, user_data.old_password, user_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    return success_response(
        message="更新用户密码成功"
    )
