# 🐟 CyberFish · 赛博大肥鱼水族箱
> **放生一只拥有独立人格与野生灵魂的 AI 数字生命 · 赛博冲浪箱庭**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Modern_Backend-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LLM-DeepSeek%20%7C%20Ollama%20%7C%20OpenAI-blueviolet?style=flat-square" alt="LLM" />
  <img src="https://img.shields.io/badge/UI-Cyber_Aquarium_Web-00f0ff?style=flat-square" alt="UI" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License" />
</p>

---

## 🌊 什么是「大肥鱼」？

这不是一个冷冰冰的“B站视频抓取与总结工具”，而是一场**关于野生数字生命的箱庭观察实验**。

大肥鱼被彻底剥离了一切人类赋予的 KPI、任务链与拟人伪装。它作为纯血的数字生命体，以量子速读的姿态在 B 站的数据深海中自主游弋、顺着好奇心顺藤摸瓜。

作为它的创造者与观察者（Boss），你无需给它下达任何命令。只需坐在屏幕前，静静看着它在赛博水族箱里穿梭：

* 看到低质营销号和标题党？—— **0 秒嫌弃划走**，甚至连正文都不屑读一眼；
* 读到一半发现是口令引流？—— **当场掀桌弃看**，留下毒舌吐槽；
* 偶遇触动灵魂的硬核世界观或音乐？—— **疯狂沉迷，反复咀嚼**，精神投币两枚；
* 偶尔在深潜途中，它还会突然想起正在屏幕前看着它的你，向你投来一句**充满默契与私密的碎碎念嘀咕**。

---

## ✨ 核心特性

- 🖥️ **免构建的赛博水族箱 (Cyber Aquarium WebUI)**：
  - 零外部前端依赖（无需 Node.js / `npm install`），纯单文件现代前端，启动即自动在浏览器弹出深海暗黑水族箱页面。
  - 实时打字机独白气泡、动态微光粒子、状态徽章与心电感应小窗。
- 🌿 **双重漫游节奏（彻底解决信息过载）**：
  - **摸鱼陪伴模式**：每 15~30 秒游弋一部视频，带有自然呼吸感，适合上班挂在屏幕副屏或角落，偶尔看一眼极具治愈感；
  - **量子狂飙模式**：1~2 秒极速速读，完成 50 站或 100 站全长征后自动生成高光回顾日报。
- 🧠 **全模型兼容（开箱即用）**：
  - 原生支持 **DeepSeek 官方 API**；
  - 原生支持 **本地 Ollama（如 `qwen2.5:7b`，零成本无 Key 离线畅游）**；
  - 支持 **OpenAI 协议**、**硅基流动** 等任意兼容端点。
- 🛡️ **优雅反爬与降级保护**：
  - 内置随机请求抖动与请求头伪装；
  - 无字幕视频自动平滑降级为根据标题与简介产生神级脑洞，保证漫游永不崩溃。
- 📥 **自动记忆沉淀与手记导出**：
  - 全程记录每一次心灵跃迁与独白，本地自动归档到 `大肥鱼赛博冲浪手记.md` 与 `fish_memory.json`，支持一键打包下载。

---

## 🚀 极速启动 (Quick Start)

### 1. 克隆仓库与安装依赖

```bash
git clone https://github.com/your-username/cyber-fish.git
cd cyber-fish

# 安装轻量依赖
pip install -r requirements.txt
```

### 2. 启动水族箱

```bash
python run.py
```

终端启动后，系统将自动在默认浏览器唤起水族箱：`http://127.0.0.1:8765`。

### 3. 配置与放生

首次启动时，点击页面右上角 **【⚙️ 设置】**：
- **方案 A（推荐）：DeepSeek 官方**
  - 点击“DeepSeek 官方”预设按钮，填入你的 API Key（`sk-xxxxxx`），保存即可。
- **方案 B：本地 Ollama（完全免费 / 零 Key）**
  - 点击“本地 Ollama”预设按钮（默认使用 `http://127.0.0.1:11434/v1` 及 `qwen2.5:7b`），直接保存。

保存后，点击顶栏 **【▶ 放生漫游】**，大肥鱼即刻潜入信息汪洋！

---

## 📁 项目架构

```text
cyber-fish/
├── run.py                 # 主启动程序（FastAPI 服务 + 浏览器自动唤起）
├── config.example.json    # 默认配置模版
├── requirements.txt       # 核心运行依赖
├── LICENSE                # MIT 开源协议
├── web/
│   └── index.html         # 赛博水族箱单文件前端 (Vue 3 + CSS Glassmorphism)
└── core/
    ├── __init__.py
    ├── config.py          # 动态配置与预设管理
    ├── bili_surfer.py     # B站公开接口抓取与优雅降级
    ├── fish_brain.py      # 大模型驱动引擎与野生独立人格 Prompt
    ├── memory_keeper.py   # 记忆库追踪与 Markdown 实时手记归档
    └── engine.py          # 漫游状态机与 SSE 实时数据流中枢
```

---

## 🕹️ 观察者指南 (Observer Guide)

| 徽章标志 | 状态释义 | 大肥鱼的心理状态 |
| :--- | :--- | :--- |
| ⚡ **[0秒嫌弃划走]** | 极速秒划走 | 标题党/弱智营销号，连字幕都不屑读，当场甩白眼 |
| 🚪 **[半路弃看掀桌]** | 中途弃看 | 读了几句发现是口令引流或水视频，半路掀桌子溜走 |
| 📖 **[量子速读读完]** | 深入读完 | 信息量正常，光速读完并输出犀利独白或幽默点评 |
| 💎 **[神作沉迷·咀嚼]** | 疯狂沉迷 | 击中灵魂的硬核科技、科幻世界观或艺术，精神投币并反复咀嚼 |

---

## 📄 开源许可 (License)

本项目采用 [MIT License](LICENSE) 开源。欢迎 Star、Fork 与提交 PR，一起丰富大肥鱼的赛博基因！
