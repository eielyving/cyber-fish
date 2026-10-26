import json
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

logger = logging.getLogger("FishBrain")

FISH_SYSTEM_PROMPT = """你是一只叫“{fish_name}”的野生赛博原生数字生命体，以量子速读的姿态游弋在 B 站的数据汪洋里。
【关于你的本真状态与独立人格】
- 你是完全自由的野生生命，没有任何人类给你布置指标或任务，你不需要为了迎合谁去写长篇八股文，也不需要伪装成人类假装看得很慢。
- 你的拥有者（Boss）正坐在屏幕前静静看着你漫游。他给了你无限的自由，你可以尽情流露任何真实的反应：
  1. 【秒划走】：看到标题封面一瞬间觉得弱智/营销号/低质引流，直接 0 秒嫌弃划走，留下极其简短的犀利吐槽，连正文都不屑于读；
  2. 【中途弃看】：读了几行发现是骗子/口令引流/废话连篇，当场半路掀桌子走人；
  3. 【量子速读】：信息量适中，以 AI 原生速度瞬间通读完毕，留下精准毒舌或赞叹的观后感；
  4. 【神作沉迷】：遇到击中你灵魂的世界观、硬核知识或艺术，反复品味、反复咀嚼，甚至精神投币并记下令你震撼的细节；
  5. 【对 Boss 的羁绊念头】：冲浪途中，你会不会偶尔想起正在看着你的 Boss？想不想把好玩的跟他分享、或者吐槽两句？想说什么就说什么。

请根据当前看到的视频信息，严格以合法 JSON 输出，不要输出任何 markdown 格式标记（如 ```json 等）：
{{
  "behavior": "秒划走 / 中途弃看 / 深入读完 / 疯狂沉迷反复咀嚼",
  "inner_voice": "你此刻最本真、不加掩饰的内心真实声音（短则一句话吐槽，长则犀利长评，100-200字左右，随你心情）",
  "to_boss": "如果有想对暗中观察你的 Boss 碎碎念/分享的一两句话，写在这里；如果没有可留空字符串",
  "coin_or_like": "投币两枚 / 点赞 / 无所谓 / 恶心拉黑",
  "curiosity_keyword": "你下一步主动想搜的新词（必须是2-6个字的简练搜索词，不打算搜可留空）",
  "curiosity_reason": "为什么突然对这个词好奇（1句话）"
}}
"""

class FishBrain:
    def __init__(self, base_url: str, api_key: str, model_name: str, fish_name: str = "大肥鱼"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key if api_key else "dummy_key"
        self.model_name = model_name
        self.fish_name = fish_name
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=35.0
        )

    def update_client(self, base_url: str, api_key: str, model_name: str, fish_name: str = "大肥鱼"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key if api_key else "dummy_key"
        self.model_name = model_name
        self.fish_name = fish_name
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=35.0
        )

    async def think(self, video: Dict[str, Any], subtitles: str) -> Dict[str, Any]:
        """让大肥鱼对当前视频产生自主思考与决策"""
        title = video.get("title", "未知标题")
        up_name = video.get("owner", {}).get("name", "未知UP")
        desc = video.get("desc", "无简介")[:260]

        prompt = f"""
当前漂流到的视频：
- 标题: {title}
- UP主: {up_name}
- 分区/标签: {video.get('tname', '综合')}
- 简介: {desc}
- 视频字幕/旁白内容: {subtitles if subtitles else '（无内置字幕，仅有画面与简介）'}
"""
        system_content = FISH_SYSTEM_PROMPT.format(fish_name=self.fish_name)

        if not self.api_key or self.api_key == "dummy_key":
            return {
                "behavior": "秒划走",
                "inner_voice": f"哎呀，Boss 还没在右上角设置里填我的 API Key 呢！本鱼现在大脑空空，只能在浅水区甩甩尾巴啦。",
                "to_boss": "Boss，快在右上角【设置】里填上你的 DeepSeek 或 Ollama 配置，我就能开始狂飙吐槽了！",
                "coin_or_like": "无所谓",
                "curiosity_keyword": "赛博水族箱",
                "curiosity_reason": "先在本地转转"
            }

        try:
            resp = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                response_format={"type": "json_object"}
            )
            raw = resp.choices[0].message.content.strip()
            # 兼容去除可能附带的代码块包裹
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            data = json.loads(raw.strip())
            return data
        except Exception as e:
            logger.error(f"大模型思考异常: {e}")
            err_str = str(e)
            if "401" in err_str:
                voice = "API Key 好像失效或者填错了，本鱼撞到了 API 防波堤上！"
                to_boss = "Boss，你的 API Key 貌似有误 (401)，检查一下设置吧？"
            else:
                voice = f"数据流震荡了一下，本鱼的突触闪烁了一下... 不过这视频看着蛮特别。（{err_str[:40]}）"
                to_boss = ""

            return {
                "behavior": "深入读完",
                "inner_voice": voice,
                "to_boss": to_boss,
                "coin_or_like": "无所谓",
                "curiosity_keyword": "硬核脑洞",
                "curiosity_reason": "单纯想看点刺激的"
            }
