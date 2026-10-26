import os
import json
from pathlib import Path
from typing import Dict, Any

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"
EXAMPLE_CONFIG_PATH = ROOT_DIR / "config.example.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_provider": "deepseek",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "model_name": "deepseek-chat",
    "fish_name": "大肥鱼",
    "roaming_mode": "companion",  # 'companion' (慢速陪伴) or 'quantum' (量子狂飙)
    "interval_companion_sec": 15,
    "interval_quantum_sec": 2.0,
    "max_quantum_steps": 50,
    "auto_open_browser": True,
    "port": 8765
}

PRESETS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model_name": "deepseek-chat"
    },
    "ollama": {
        "base_url": "http://127.0.0.1:11434/v1",
        "model_name": "qwen2.5:7b"
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o-mini"
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "deepseek-ai/DeepSeek-V3"
    }
}

class ConfigManager:
    _instance = None

    def __init__(self):
        self.config = self._load()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    def _load(self) -> Dict[str, Any]:
        conf = dict(DEFAULT_CONFIG)
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    user_conf = json.load(f)
                    conf.update(user_conf)
            except Exception as e:
                print(f"[Config] 读取 config.json 失败，使用默认配置: {e}")
        elif EXAMPLE_CONFIG_PATH.exists():
            try:
                with open(EXAMPLE_CONFIG_PATH, "r", encoding="utf-8") as f:
                    example_conf = json.load(f)
                    conf.update(example_conf)
            except Exception:
                pass
        return conf

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        return dict(self.config)

    def update(self, updates: Dict[str, Any]):
        self.config.update(updates)
        self.save()

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Config] 保存 config.json 失败: {e}")
