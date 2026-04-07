from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str


class UserInfoBase(BaseModel):
    """
    ⽤户信息基础数据模型(可选)
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True  # 允许从 ORM 对象属性中取值
    )


class UserUpdateRequest(BaseModel):
    """
    用户更新信息请求数据模型
    """
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


class UserUpdatePasswordRequest(BaseModel):
    """
    用户更新密码请求数据模型
    """
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., alias="newPassword", description="新密码")
