import urllib.parse
import random
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger("BiliSurfer")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

class BiliSurfer:
    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout

    async def _get_json(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 412:
                    logger.warning(f"B站触发 412 风控，建议增加游弋间隔: {url}")
        except Exception as e:
            logger.debug(f"HTTP GET 请求异常 [{url}]: {e}")
        return None

    async def get_popular_videos(self) -> List[Dict[str, Any]]:
        """获取全站热门视频"""
        url = "https://api.bilibili.com/x/web-interface/popular?pn=1&ps=20"
        res = await self._get_json(url)
        if res and res.get("code") == 0 and "data" in res and "list" in res["data"]:
            clean_list = []
            for v in res["data"]["list"]:
                clean_list.append({
                    "bvid": v.get("bvid"),
                    "cid": v.get("cid", 0),
                    "title": v.get("title", ""),
                    "pic": v.get("pic", ""),
                    "owner": v.get("owner", {}),
                    "desc": v.get("desc", ""),
                    "tname": v.get("tname", "")
                })
            return clean_list
        return []

    async def get_related_videos(self, bvid: str) -> List[Dict[str, Any]]:
        """顺藤摸瓜：获取相关推荐视频"""
        url = f"https://api.bilibili.com/x/web-interface/archive/related?bvid={bvid}"
        res = await self._get_json(url)
        if res and res.get("code") == 0 and "data" in res:
            data = res["data"]
            clean_list = []
            for v in data:
                clean_list.append({
                    "bvid": v.get("bvid"),
                    "cid": v.get("cid", 0),
                    "title": v.get("title", ""),
                    "pic": v.get("pic", ""),
                    "owner": v.get("owner", {}),
                    "desc": v.get("desc", ""),
                    "tname": v.get("tname", "")
                })
            return clean_list
        return []

    async def search_videos(self, keyword: str) -> List[Dict[str, Any]]:
        """根据大肥鱼自主想出的关键词进行全站搜索"""
        if not keyword:
            return []
        encoded = urllib.parse.quote(keyword)
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={encoded}&page=1"
        res = await self._get_json(url)
        if res and res.get("code") == 0 and "data" in res and "result" in res["data"]:
            raw_list = res["data"]["result"]
            clean_list = []
            for v in raw_list[:8]:
                raw_title = v.get("title", "")
                clean_title = raw_title.replace('<em class="keyword">', "").replace('</em>', "")
                clean_list.append({
                    "bvid": v.get("bvid"),
                    "cid": 0,
                    "title": clean_title,
                    "pic": v.get("pic", ""),
                    "owner": {"name": v.get("author", "未知UP")},
                    "desc": v.get("description", ""),
                    "tname": v.get("typename", "")
                })
            return clean_list
        return []

    async def get_subtitles(self, bvid: str, cid: int) -> str:
        """获取视频字幕/旁白摘要"""
        if not cid:
            # 尝试通过 bvid 获取 cid
            detail_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            view_res = await self._get_json(detail_url)
            if view_res and view_res.get("code") == 0 and "data" in view_res:
                cid = view_res["data"].get("cid", 0)

        if not cid:
            return ""

        url = f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}"
        res = await self._get_json(url)
        if not res or res.get("code") != 0 or "data" not in res:
            return ""

        sub_list = res["data"].get("subtitle", {}).get("subtitles", [])
        if not sub_list:
            return ""

        sub_url = sub_list[0].get("subtitle_url")
        if not sub_url:
            return ""

        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=5.0) as client:
                sub_res = await client.get(sub_url)
                if sub_res.status_code == 200:
                    sub_json = sub_res.json()
                    lines = [item.get("content", "") for item in sub_json.get("body", [])]
                    return " ".join(lines)[:1800]  # 适度取前 1800 字，兼顾深度与 Token 节约
        except Exception:
            pass
        return ""
