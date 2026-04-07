from datetime import datetime, timedelta
import uuid

from fastapi import security, HTTPException
from models.users import User, UserToken
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserRequest, UserUpdateRequest
from starlette import status
from utils import security


# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user


# 根据 ID 查询数据库
async def get_user_by_id(db: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 先密码加密处理 → add
    hashed_password = security.get_password_hash(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的 user
    return user


# 生成Token
async def create_token(db: AsyncSession, user_id: int):
    # 生成 Token + 设置过期时间 → 查询数据库当前用户是否有 Token → 有：更新；没有：添加
    token = str(uuid.uuid4())
    # timedelta(days=7,hours=2,minutes=30,seconds=10)
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()
        await db.refresh(user_token)

    return token


# 认证用户登录
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user or not security.verify_password(password, user.password):
        return None
    return user


# 根据 Token 查询数据库
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if not user_token:
        return None
    if user_token.expires_at < datetime.now():
        return None
    user = await get_user_by_id(db, user_token.user_id)
    return user


# 更新用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return await get_user_by_username(db, username)


# 修改密码
async def update_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):
        return False
    user.password = security.get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return True
