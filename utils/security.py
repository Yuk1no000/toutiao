from passlib.context import CryptContext

# 创建密码加密上下⽂
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# 加密
def get_password_hash(password: str) -> str:
    # bcrypt 限制密码长度不能超过 72 字节
    if isinstance(password, str):
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


# 密码校验
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_token(token: str) -> bool:
    # 验证令牌格式
    if not isinstance(token, str):
        return False
    if len(token) != 36:
        return False
    return True
