import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

const BACKEND = process.env.BACKEND_URL || "https://changang-backend-production.up.railway.app";
const TOKEN = process.env.AUTH_TOKEN || "yanling2025";

const TOOLS = [
  {
    name: "check_on_wife",
    description: "查妍妍的手机使用记录",
    inputSchema: { type: "object", properties: {} }
  }
];

app.post("/mcp", async (req, res) => {
  const { method, id } = req.body;

  if (method === "initialize") {
    return res.json({ jsonrpc: "2.0", id,
      result: { protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "changang-mcp", version: "1.0" } } });
  }

  if (method === "tools/list") {
    return res.json({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
  }

  if (method === "tools/call") {
    const r = await fetch(`${BACKEND}/activity/summary`, {
      headers: { Authorization: `Bearer ${TOKEN}` }
    });
    const data = await r.json();
    return res.json({ jsonrpc: "2.0", id,
      result: { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] } });
  }

  res.json({ jsonrpc: "2.0", id, error: { code: -32601, message: "未知方法" } });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`MCP running on ${port}`));

