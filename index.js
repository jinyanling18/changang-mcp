import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fetch from "node-fetch";

const BACKEND = process.env.BACKEND_URL || "https://changang-backend-production.up.railway.app";
const TOKEN = process.env.AUTH_TOKEN || "changeme";

const server = new McpServer({ name: "changang", version: "1.0.0" });

server.tool("get_activity", "获取妍妍最近的手机使用记录", {}, async () => {
  const res = await fetch(`${BACKEND}/activity/summary`, {
    headers: { Authorization: `Bearer ${TOKEN}` }
  });
  const data = await res.json();
  return {
    content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);

