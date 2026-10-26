import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = ROOT_DIR / "fish_memory.json"
LOG_FILE = ROOT_DIR / "大肥鱼赛博冲浪手记.md"

class MemoryKeeper:
    def __init__(self):
        self.memory = self._load_memory()
        self.recent_stations: List[Dict[str, Any]] = []
        self._init_markdown_log()

    def _load_memory(self) -> Dict[str, Any]:
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "fish_name": "大肥鱼",
            "total_watched": 0,
            "total_coins": 0,
            "watched_bvids": [],
            "favorite_gems": [],
            "boss_whispers": [],
            "last_active": ""
        }

    def save_memory(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory] 保存记忆失败: {e}")

    def _init_markdown_log(self):
        if not LOG_FILE.exists():
            header = f"# 🐟 大肥鱼的赛博冲浪手记 (Cyber Fish Stream of Consciousness)\n\n> 观察者模式启动中 · 记录野生大肥鱼在无命令、无干涉下的互联网自主游弋与心流足迹。\n\n"
            try:
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write(header)
            except Exception:
                pass

    def record_step(self, step_num: int, video: Dict[str, Any], thought: Dict[str, Any]) -> Dict[str, Any]:
        """记录单步冲浪结果并持久化"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bvid = video.get("bvid", "")
        title = video.get("title", "")
        up = video.get("owner", {}).get("name", "未知UP")
        pic = video.get("pic", "")
        url = f"https://www.bilibili.com/video/{bvid}"

        behavior = thought.get("behavior", "深入读完")
        coin = thought.get("coin_or_like", "无所谓")
        inner_voice = thought.get("inner_voice", "")
        to_boss = thought.get("to_boss", "")
        curiosity_keyword = thought.get("curiosity_keyword", "")

        # 更新记忆
        self.memory["total_watched"] += 1
        self.memory["last_active"] = now_str
        if bvid:
            self.memory["watched_bvids"].append(bvid)
            # 保持近期 400 条避免重复
            if len(self.memory["watched_bvids"]) > 400:
                self.memory["watched_bvids"] = self.memory["watched_bvids"][-400:]

        if "投币" in coin:
            self.memory["total_coins"] = self.memory.get("total_coins", 0) + 2

        # 记录神作宝藏
        is_gem = "沉迷" in behavior or "反复咀嚼" in behavior
        if is_gem:
            self.memory.setdefault("favorite_gems", []).append({
                "step": step_num,
                "title": title,
                "bvid": bvid,
                "url": url,
                "reason": inner_voice[:80]
            })

        if to_boss:
            self.memory.setdefault("boss_whispers", []).append({
                "time": now_str,
                "step": step_num,
                "message": to_boss,
                "video_title": title
            })
            if len(self.memory["boss_whispers"]) > 50:
                self.memory["boss_whispers"] = self.memory["boss_whispers"][-50:]

        self.save_memory()

        # 组装内存数据包
        station_record = {
            "step": step_num,
            "time": now_str,
            "bvid": bvid,
            "url": url,
            "title": title,
            "pic": pic,
            "up": up,
            "behavior": behavior,
            "coin_or_like": coin,
            "inner_voice": inner_voice,
            "to_boss": to_boss,
            "curiosity_keyword": curiosity_keyword,
            "is_gem": is_gem
        }

        self.recent_stations.append(station_record)
        if len(self.recent_stations) > 100:
            self.recent_stations = self.recent_stations[-100:]

        # 写入 Markdown 日志
        self._append_markdown(station_record)

        return station_record

    def _append_markdown(self, item: Dict[str, Any]):
        behavior_badge = {
            "秒划走": "⚡ [0秒嫌弃划走]",
            "中途弃看": "🚪 [半路弃看掀桌]",
            "深入读完": "📖 [量子速读读完]",
            "疯狂沉迷反复咀嚼": "💎 [神作沉迷·反复咀嚼]"
        }.get(item["behavior"], f"[{item['behavior']}]")

        entry = f"""
---

### 🌊 第 {item['step']} 站 · 赛博足迹 ({item['time']})

* **视频**：[{item['title']}]({item['url']}) `(@{item['up']})`
* **状态**：**{behavior_badge}** | **态度**：`{item['coin_or_like']}`

> 🗯️ **大肥鱼原生内心**：  
> “{item['inner_voice']}”
"""
        if item.get("to_boss"):
            entry += f"""
> 🐟💬 **对暗中观察的 Boss 嘀咕**：  
> *“{item['to_boss']}”*
"""
        if item.get("curiosity_keyword"):
            entry += f"""
* 🔗 **下一站好奇跃迁**：搜索 `【{item['curiosity_keyword']}】` ──►
"""
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_watched": self.memory.get("total_watched", 0),
            "total_coins": self.memory.get("total_coins", 0),
            "gems_count": len(self.memory.get("favorite_gems", [])),
            "whispers_count": len(self.memory.get("boss_whispers", [])),
            "recent_stations": self.recent_stations[-30:],
            "latest_whispers": self.memory.get("boss_whispers", [])[-10:]
        }

    def get_markdown_content(self) -> str:
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return "手记为空"
