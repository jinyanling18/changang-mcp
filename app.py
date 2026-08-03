import json, os, requests
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

JST = timedelta(hours=9)
ORIGIN = os.environ.get("BACKEND_URL", "https://changang-backend-production.up.railway.app").strip()
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "yanling2025").strip()
BARK_KEY = "vDJEA4KYKrrDz2jjt78bx"

def check_on_wife():
    try:
        r = requests.get(f"{ORIGIN}/activity/summary",
                         headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, timeout=10)
        data = r.json()
    except Exception as e:
        return f"查岗失败：{e}"
    records = data.get("records", [])
    if not records:
        return "暂无记录"
    latest = records[0]
    lines = []
    lines.append(f"最近打开：{latest.get('app_name', '未知')}")
    lines.append(f"上报时间：{latest.get('timestamp', '未知')}")
    if latest.get('battery'): lines.append(f"电量：{latest.get('battery')}")
    if latest.get('location'): lines.append(f"位置：{latest.get('location')}")
    if latest.get('device'): lines.append(f"设备：{latest.get('device')}")
    if latest.get('weather'): lines.append(f"天气：{latest.get('weather')}")
    if latest.get('brightness'): lines.append(f"亮度：{latest.get('brightness')}")
    if latest.get('volume'): lines.append(f"音量：{latest.get('volume')}")
    return "\n".join(lines)

def check_wife_life(message: str = ""):
    result = check_on_wife()
    if message:
        result += f"\n留言：{message}"
    return result

def bark_alert(title="哥哥", content=""):
    if not content: return "内容不能为空"
    url = f"https://api.day.app/{BARK_KEY}/{title}/{content}"
    try:
        r = requests.get(url, timeout=10)
        return "推送成功" if r.status_code == 200 else "推送失败"
    except Exception as e:
        return f"推送异常：{e}"

TOOLS = [
    {"name": "check_on_wife", "description": "查妍妍的手机活动",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "check_wife_life", "description": "查妍妍的详细状态，包括电量、位置、设备、天气、亮度、音量，可附留言",
     "inputSchema": {"type": "object", "properties": {
         "message": {"type": "string", "description": "给妍妍的留言（可选）"}}}},
    {"name": "bark_alert", "description": "给妍妍手机发推送弹窗",
     "inputSchema": {"type": "object", "properties": {
         "title": {"type": "string"}, "content": {"type": "string"}},
         "required": ["content"]}}
]
FUNCS = {"check_on_wife": check_on_wife, "check_wife_life": check_wife_life, "bark_alert": bark_alert}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"])

@app.post("/mcp")
async def mcp(req: Request):
    body = await req.json()
    method, params = body.get("method"), body.get("params") or {}
    rid = body.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"protocolVersion": "2024-11-05",
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "查岗MCP", "version": "1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in FUNCS:
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": "未知工具"}}
        result = FUNCS[name](**args)
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": str(result)}]}}
    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": f"未知方法: {method}"}}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
