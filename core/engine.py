import asyncio
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import ConfigManager
from .bili_surfer import BiliSurfer  # wait, import as .bili_surfer
from .fish_brain import FishBrain
from .memory_keeper import MemoryKeeper

logger = logging.getLogger("FishEngine")

class FishEngine:
    _instance = None

    def __init__(self):
        self.config_mgr = ConfigManager.get_instance()
        conf = self.config_mgr.get_all()

        self.surfer = BiliSurfer()
        self.brain = FishBrain(
            base_url=conf.get("base_url", "https://api.deepseek.com/v1"),
            api_key=conf.get("api_key", ""),
            model_name=conf.get("model_name", "deepseek-chat"),
            fish_name=conf.get("fish_name", "大肥鱼")
        )
        self.memory = MemoryKeeper()

        self.is_running = False
        self.is_paused = False
        self.current_keyword: Optional[str] = None
        self.last_bvid: Optional[str] = None
        self.step_count = self.memory.memory.get("total_watched", 0)
        self.current_roaming_task: Optional[asyncio.Task] = None

        # SSE 广播客户端集合
        self.subscribers: List[asyncio.Queue] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FishEngine()
        return cls._instance

    def reload_config(self):
        conf = self.config_mgr.get_all()
        self.brain.update_client(
            base_url=conf.get("base_url", "https://api.deepseek.com/v1"),
            api_key=conf.get("api_key", ""),
            model_name=conf.get("model_name", "deepseek-chat"),
            fish_name=conf.get("fish_name", "大肥鱼")
        )

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subscribers.append(q)
        # 发送初始状态包
        init_data = self.get_status()
        await q.put({"type": "init", "data": init_data})
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    async def broadcast(self, event_type: str, data: Any):
        dead_queues = []
        msg = {"type": event_type, "data": data}
        for q in self.subscribers:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                dead_queues.append(q)
        for q in dead_queues:
            self.unsubscribe(q)

    def get_status(self) -> Dict[str, Any]:
        conf = self.config_mgr.get_all()
        summary = self.memory.get_summary()
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "mode": conf.get("roaming_mode", "companion"),
            "current_step": self.step_count,
            "current_keyword": self.current_keyword or "信息流自然浮潜",
            "stats": {
                "total_watched": summary["total_watched"],
                "total_coins": summary["total_coins"],
                "gems_count": summary["gems_count"],
                "whispers_count": summary["whispers_count"]
            },
            "recent_stations": summary["recent_stations"],
            "latest_whispers": summary["latest_whispers"],
            "config": {
                "api_provider": conf.get("api_provider"),
                "base_url": conf.get("base_url"),
                "model_name": conf.get("model_name"),
                "fish_name": conf.get("fish_name"),
                "has_api_key": bool(conf.get("api_key")),
                "interval_companion_sec": conf.get("interval_companion_sec", 15),
                "interval_quantum_sec": conf.get("interval_quantum_sec", 2.0),
                "max_quantum_steps": conf.get("max_quantum_steps", 50)
            }
        }

    async def start(self):
        if self.is_running and not self.is_paused:
            return
        if self.is_paused:
            self.is_paused = False
            await self.broadcast("status_change", {"is_running": True, "is_paused": False})
            return

        self.is_running = True
        self.is_paused = False
        await self.broadcast("status_change", {"is_running": True, "is_paused": False})

        if self.current_roaming_task is None or self.current_roaming_task.done():
            self.current_roaming_task = asyncio.create_task(self._roaming_loop())

    async def pause(self):
        self.is_paused = True
        await self.broadcast("status_change", {"is_running": self.is_running, "is_paused": True})

    async def trigger_single_step(self):
        """手动催大肥鱼游一步"""
        if not self.is_running:
            self.is_running = True
        await self._roam_one_station()

    async def _pick_target_video(self) -> Optional[Dict[str, Any]]:
        watched_set = set(self.memory.memory.get("watched_bvids", []))
        video = None

        # 1. 如果有好奇心搜索词，优先尝试搜索
        if self.current_keyword:
            searched = await self.surfer.search_videos(self.current_keyword)
            unseen = [v for v in searched if v.get("bvid") not in watched_set]
            if unseen:
                video = random.choice(unseen)

        # 2. 如果没搜索到，且有上一个视频，尝试从相关推荐里游走
        if not video and self.last_bvid:
            related = await self.surfer.get_related_videos(self.last_bvid)
            unseen_rel = [v for v in related if v.get("bvid") not in watched_set]
            if unseen_rel:
                video = random.choice(unseen_rel[:6])

        # 3. 兜底从全站热门里抓取
        if not video:
            popular = await self.surfer.get_popular_videos()
            unseen_pop = [v for v in popular if v.get("bvid") not in watched_set]
            if unseen_pop:
                video = random.choice(unseen_pop[:12])
            elif popular:
                video = random.choice(popular[:12])

        return video

    async def _roam_one_station(self):
        conf = self.config_mgr.get_all()
        video = await self._pick_target_video()
        if not video:
            await self.broadcast("engine_log", {"message": "正在深潜寻找水域中..."})
            return

        bvid = video.get("bvid", "")
        cid = video.get("cid", 0)
        self.last_bvid = bvid
        self.step_count += 1

        # 通知前端：发现新视频，正在解析
        await self.broadcast("video_spotted", {
            "step": self.step_count,
            "video": video,
            "keyword": self.current_keyword
        })

        # 抓取字幕
        subtitles = await self.surfer.get_subtitles(bvid, cid)

        # 产生神经元独白
        thought = await self.brain.think(video, subtitles)

        # 记录记忆并生成记录
        record = self.memory.record_step(self.step_count, video, thought)

        # 设置下一次好奇心关键词
        self.current_keyword = thought.get("curiosity_keyword")

        # 广播给前端呈现水族箱最新心跳
        await self.broadcast("new_station", {
            "record": record,
            "stats": {
                "total_watched": self.memory.memory.get("total_watched", 0),
                "total_coins": self.memory.memory.get("total_coins", 0),
                "gems_count": len(self.memory.memory.get("favorite_gems", [])),
                "whispers_count": len(self.memory.memory.get("boss_whispers", []))
            }
        })

    async def _roaming_loop(self):
        try:
            quantum_count = 0
            while self.is_running:
                if self.is_paused:
                    await asyncio.sleep(1.0)
                    continue

                conf = self.config_mgr.get_all()
                mode = conf.get("roaming_mode", "companion")
                quantum_limit = conf.get("max_quantum_steps", 50)

                await self._roam_one_station()

                if mode == "quantum":
                    quantum_count += 1
                    if quantum_count >= quantum_limit:
                        self.is_paused = True
                        await self.broadcast("quantum_finished", {
                            "message": f"🎉 大肥鱼已达成 {quantum_limit} 站量子巡游，圆满靠岸休眠！",
                            "stats": self.memory.get_summary()
                        })
                        break
                    # 量子模式极速间隔
                    interval = float(conf.get("interval_quantum_sec", 2.0))
                else:
                    # 摸鱼陪伴模式舒适间隔
                    interval = float(conf.get("interval_companion_sec", 15.0))

                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"冲浪主循环异常: {e}", exc_info=True)
        finally:
            self.is_running = False
