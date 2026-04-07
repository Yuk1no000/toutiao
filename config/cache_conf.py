import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis 服务器的主机地址
    port=REDIS_PORT,  # Redis 端口号
    db=REDIS_DB,  # Redis 数据库编号，0~15
    decode_responses=True  # 将字节数据解码为字符串
)


# 设置和读取（字符串和列表或字典）"[{}]"
# 读取：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None


# 读取：列表或字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 序列化
        return None
    except Exception as e:
        print(f"获取JSON缓存失败：{e}")
        return None


# 写入：字符串
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)  # 保留中文
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"写入缓存失败：{e}")
        return False


# 删除缓存
async def delete_cache(key: str) -> bool:
    try:
        result = await redis_client.delete(key)
        return result > 0
    except Exception as e:
        print(f"删除缓存失败：{e}")
        return False
