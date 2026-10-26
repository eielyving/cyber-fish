import os
import sys
import asyncio
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.config import ConfigManager, PRESETS
from core.engine import FishEngine

ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"

app = FastAPI(title="CyberFish 赛博大肥鱼水族箱")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = FishEngine.get_instance()
config_mgr = ConfigManager.get_instance()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>CyberFish 赛博大肥鱼水族箱</h1><p>web/index.html 未找到。</p>"

@app.get("/api/status")
async def get_status():
    return engine.get_status()

@app.post("/api/start")
async def start_roaming():
    await engine.start()
    return {"status": "ok", "message": "大肥鱼已放生，潜入数据深海！"}

@app.post("/api/pause")
async def pause_roaming():
    await engine.pause()
    return {"status": "ok", "message": "大肥鱼已浮上水面打盹。"}

@app.post("/api/step")
async def single_step():
    await engine.trigger_single_step()
    return {"status": "ok", "message": "大肥鱼自主游弋了一站。"}

@app.post("/api/mode")
async def set_mode(req: Request):
    data = await req.json()
    new_mode = data.get("mode", "companion")
    config_mgr.update({"roaming_mode": new_mode})
    await engine.broadcast("mode_change", {"mode": new_mode})
    return {"status": "ok", "mode": new_mode}

@app.post("/api/settings")
async def update_settings(req: Request):
    data = await req.json()
    provider = data.get("api_provider")
    updates = {}
    for key in ["api_provider", "base_url", "api_key", "model_name", "fish_name",
                "interval_companion_sec", "interval_quantum_sec", "max_quantum_steps"]:
        if key in data and data[key] is not None:
            updates[key] = data[key]

    config_mgr.update(updates)
    engine.reload_config()
    await engine.broadcast("settings_updated", config_mgr.get_all())
    return {"status": "ok", "message": "设置已更新并生效！"}

@app.get("/api/presets")
async def get_presets():
    return PRESETS

@app.get("/api/export")
async def export_markdown():
    content = engine.memory.get_markdown_content()
    filename = f"大肥鱼赛博冲浪手记_{engine.step_count}站.md"
    return PlainTextResponse(
        content,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/events")
async def sse_events(request: Request):
    """Server-Sent Events 实时数据流"""
    queue = await engine.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # 心跳保活
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            engine.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    port = config_mgr.get("port", 8765)
    auto_browser = config_mgr.get("auto_open_browser", True)

    print("=" * 66)
    print("🐟  CyberFish (赛博大肥鱼) · 纯血数字生命原生箱庭引擎")
    print(f"🌊  箱庭水族箱已就绪: http://127.0.0.1:{port}")
    print("=" * 66)

    async def open_browser():
        await asyncio.sleep(1.2)
        if auto_browser:
            webbrowser.open_new_tab(f"http://127.0.0.1:{port}")

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(open_browser())

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    main()
