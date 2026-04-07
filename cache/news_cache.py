# 新闻相关的缓存文件
# key - value
from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache, delete_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list:"


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存:缓存的数据、过期时间
async def set_cached_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 写入缓存-新闻列表
# Key = "news:list:{category_id}:{page}:{size}"
async def set_cached_news_list(category_id: Optional[int], page: int, size: int, news_list: List[Dict[str, Any]],
                               expire: int = 600):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_id}:{page}:{size}"
    return await set_cache(key, news_list, expire)


# 读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int], page: int, size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_id}:{page}:{size}"
    return await get_json_cache(key)


# 写入缓存-新闻详情
async def set_cached_news_detail(news_id: int, news_detail: Dict[str, Any], expire: int = 600):
    key = f"news:detail:{news_id}"
    return await set_cache(key, news_detail, expire)


# 读取缓存-新闻详情
async def get_cached_news_detail(news_id: int) -> Optional[Dict[str, Any]]:
    return await get_json_cache(f"news:detail:{news_id}")


# 删除缓存-新闻详情（当浏览量变化时需要清除）
async def delete_news_detail(news_id: int) -> bool:
    return await delete_cache(f"news:detail:{news_id}")


# 写入缓存-相关推荐
async def cache_related_news(news_id: int, category_id: int, related_list: List[Dict[str, Any]],
                             expire: int = 1800) -> bool:
    key = f"news:related:{news_id}:{category_id}"
    return await set_cache(key, related_list, expire)


# 读取缓存-相关推荐
async def get_cached_related_news(news_id: int, category_id: int) -> Optional[List[Dict[str, Any]]]:
    key = f"news:related:{news_id}:{category_id}"
    return await get_json_cache(key)
