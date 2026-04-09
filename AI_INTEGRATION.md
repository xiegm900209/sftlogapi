# AI 对接指南

**版本**: v2.4.0  
**更新日期**: 2026-04-09

---

## 📋 概述

本文档介绍如何让 AI 系统（如 Claude、ChatGPT、通义千问等）调用 Log Tracker 系统的功能。

### 核心思路

```
用户 → AI 对话 → 提取参数 → 调用 Log Tracker API → 返回结果 → AI 转自然语言 → 用户
```

**你只需要提供**:
1. ✅ RESTful API 接口
2. ✅ OpenAPI/Swagger 规范文档
3. ✅ Function Calling 描述

**AI 负责**:
- 理解用户自然语言
- 提取参数（交易类型、REQ_SN、时间）
- 调用你的 API
- 将结果转换为友好的自然语言

---

## 🔌 API 接口

### 1. 交易类型日志追踪

**接口**: `GET /api/transaction-trace`

**描述**: 根据交易类型、REQ_SN、时间查询完整交易链路

**参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `transaction_type` | string | ✅ | 交易类型代码 | `310011` |
| `req_sn` | string | ✅ | 交易序列号 | `LX260408090024C80C82F3` |
| `log_time` | string | ❌ | 日志时间（YYYYMMDDHH） | `2026040809` |

**请求示例**:

```bash
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=LX260408090024C80C82F3&log_time=2026040809"
```

**响应示例**:

```json
{
  "success": true,
  "trace_groups": [
    {
      "trace_id": "TC5PCfGK",
      "req_sn_count": 1,
      "total_logs": 27,
      "first_timestamp": "2026-04-08 09:00:00.304",
      "app_logs": {
        "sft-aipg": [...],
        "sft-trxqry": [...],
        "sft-pay": [...]
      },
      "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
    }
  ],
  "total_logs": 27,
  "trace_count": 1
}
```

---

### 2. 日志追踪查询

**接口**: `GET /api/log-query`

**描述**: 综合日志查询（支持 REQ_SN、商户号、时间）

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `req_sn` | string | ❌ | 交易序列号 |
| `merchant_no` | string | ❌ | 商户号 |
| `log_time` | string | ❌ | 日志时间 |
| `service` | string | ❌ | 服务名称 |

**请求示例**:

```bash
curl "http://localhost:5000/api/log-query?req_sn=LX260408090024C80C82F3&log_time=2026040809"
```

---

### 3. 获取交易类型列表

**接口**: `GET /api/transaction-types`

**描述**: 获取所有可用的交易类型配置

**响应示例**:

```json
{
  "success": true,
  "transaction_types": {
    "310011": {
      "name": "协议支付",
      "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
    },
    "310016": {
      "name": "批量协议支付",
      "apps": ["sft-aipg", "sft-trxqry", "sft-batchpay"]
    }
  }
}
```

---

## 🤖 AI 集成方式

### 方式一：Function Calling（推荐）

适用于：Claude、ChatGPT、通义千问等支持 Function Calling 的 AI

#### 1. Function 描述

```json
{
  "name": "transaction_trace",
  "description": "追踪交易类型的完整链路，根据交易类型、REQ_SN 和时间查询所有关联应用的日志",
  "parameters": {
    "type": "object",
    "properties": {
      "transaction_type": {
        "type": "string",
        "description": "交易类型代码，如 310011（协议支付）、310016（批量协议支付）"
      },
      "req_sn": {
        "type": "string",
        "description": "交易序列号"
      },
      "log_time": {
        "type": "string",
        "description": "日志时间，格式 YYYYMMDDHH，如 2026040809"
      }
    },
    "required": ["transaction_type", "req_sn"]
  }
}
```

#### 2. AI 调用流程

```
1. 用户输入："帮我查一笔协议支付的交易，REQ_SN=LX260408090024C80C82F3 时间是：2026040809"

2. AI 提取参数:
   - transaction_type: "310011" (协议支付)
   - req_sn: "LX260408090024C80C82F3"
   - log_time: "2026040809"

3. AI 调用 Function:
   POST /api/transaction-trace?transaction_type=310011&req_sn=LX260408090024C80C82F3&log_time=2026040809

4. AI 接收响应，转换为自然语言:
   "已找到该交易的完整链路，共 27 条日志记录，涉及 3 个应用：
    - sft-aipg: 15 条日志
    - sft-trxqry: 8 条日志
    - sft-pay: 4 条日志
    TraceID: TC5PCfGK"
```

---

### 方式二：OpenAPI/Swagger

适用于：支持 OpenAPI 规范的 AI 平台

#### 1. OpenAPI 规范

```yaml
openapi: 3.0.0
info:
  title: Log Tracker API
  version: 2.4.0
  description: 交易日志链路追踪系统 API

servers:
  - url: http://localhost:5000

paths:
  /api/transaction-trace:
    get:
      summary: 交易类型日志追踪
      description: 根据交易类型、REQ_SN、时间查询完整交易链路
      parameters:
        - name: transaction_type
          in: query
          required: true
          schema:
            type: string
          description: 交易类型代码（如：310011 协议支付）
        - name: req_sn
          in: query
          required: true
          schema:
            type: string
          description: 交易序列号
        - name: log_time
          in: query
          schema:
            type: string
          description: 日志时间（格式：YYYYMMDDHH）
      responses:
        '200':
          description: 成功

  /api/log-query:
    get:
      summary: 日志追踪查询
      description: 综合日志查询
      parameters:
        - name: req_sn
          in: query
          schema:
            type: string
        - name: merchant_no
          in: query
          schema:
            type: string
        - name: log_time
          in: query
          schema:
            type: string

  /api/transaction-types:
    get:
      summary: 获取交易类型列表
      description: 获取所有可用的交易类型配置
      responses:
        '200':
          description: 成功
```

#### 2. 部署 Swagger UI

```bash
# 安装 flask-swagger-ui
pip install flask-swagger-ui

# 在 app_main.py 中添加
from flask_swagger_ui import get_swaggerui_blueprint

app.register_blueprint(
    get_swaggerui_blueprint(
        '/api/docs',
        '/static/openapi.yaml'
    )
)
```

访问：http://localhost:5000/api/docs

---

### 方式三：MCP (Model Context Protocol)

适用于：支持 MCP 的 AI 客户端（如 Claude Desktop）

#### 1. 创建 MCP 服务器

```python
# mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import requests
import json

server = Server("log-tracker")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="transaction_trace",
            description="追踪交易类型的完整链路，根据交易类型、REQ_SN 和时间查询所有关联应用的日志",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "description": "交易类型代码，如 310011（协议支付）"
                    },
                    "req_sn": {
                        "type": "string",
                        "description": "交易序列号"
                    },
                    "log_time": {
                        "type": "string",
                        "description": "日志时间，格式 YYYYMMDDHH"
                    }
                },
                "required": ["transaction_type", "req_sn"]
            }
        ),
        Tool(
            name="log_query",
            description="综合日志查询，支持 REQ_SN、商户号、时间组合查询",
            inputSchema={
                "type": "object",
                "properties": {
                    "req_sn": {"type": "string"},
                    "merchant_no": {"type": "string"},
                    "log_time": {"type": "string"},
                    "service": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name, args):
    if name == "transaction_trace":
        response = requests.get(
            "http://localhost:5000/api/transaction-trace",
            params=args
        )
        return [TextContent(text=json.dumps(response.json(), ensure_ascii=False))]
    
    elif name == "log_query":
        response = requests.get(
            "http://localhost:5000/api/log-query",
            params=args
        )
        return [TextContent(text=json.dumps(response.json(), ensure_ascii=False))]

if __name__ == "__main__":
    from mcp.server.cli import run_server
    run_server(server)
```

#### 2. 配置 Claude Desktop

```json
{
  "mcpServers": {
    "log-tracker": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

---

## 📝 交易类型映射

AI 需要将用户说的交易名称映射到交易类型代码：

| 用户说法 | 交易类型代码 | 说明 |
|---------|-------------|------|
| 协议支付 | `310011` | 最常见的交易类型 |
| 批量协议支付 | `310016` | 批量处理 |
| 协议支付签约 | `310002` | 签约交易 |
| 交易查询 | `200004` | 查询交易 |

**AI 提示词示例**:

```
你是一个交易日志查询助手。当用户提到交易类型时，请使用以下映射：
- "协议支付" → "310011"
- "批量协议支付" → "310016"
- "协议支付签约" → "310002"
- "交易查询" → "200004"

如果用户说的交易类型不在列表中，请先调用 /api/transaction-types 获取完整的交易类型列表。
```

---

## 🔧 实现步骤

### 步骤 1: 准备 API 接口 ✅

你的系统已经有完整的 API 接口：
- `/api/transaction-trace` - 交易类型追踪
- `/api/log-query` - 日志查询
- `/api/transaction-types` - 交易类型列表

### 步骤 2: 创建 OpenAPI 文档

创建 `openapi.yaml` 文件（见上文）

### 步骤 3: 配置 AI 平台

根据你使用的 AI 平台选择集成方式：

#### Claude (Anthropic)
- 使用 Function Calling
- 提供 Function 描述 JSON

#### ChatGPT (OpenAI)
- 使用 Function Calling 或 Assistants API
- 提供 Function 描述 JSON

#### 通义千问 (阿里云)
- 使用 Function Calling
- 提供 Function 描述 JSON

#### Claude Desktop (本地)
- 使用 MCP 协议
- 部署 MCP 服务器

### 步骤 4: 测试

```bash
# 测试 API
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=xxx&log_time=2026040809"

# 测试 Function Calling
# 在 AI 对话中输入：
# "帮我查一笔协议支付的交易，REQ_SN=LX260408090024C80C82F3 时间是：2026040809"
```

---

## 📊 响应格式建议

为了让 AI 更容易理解和转换，建议统一响应格式：

```json
{
  "success": true,
  "data": {
    "trace_id": "TC5PCfGK",
    "total_logs": 27,
    "apps": [
      {"name": "sft-aipg", "count": 15},
      {"name": "sft-trxqry", "count": 8},
      {"name": "sft-pay", "count": 4}
    ],
    "summary": "找到 1 个 TraceID，共 27 条日志，涉及 3 个应用"
  }
}
```

---

## ⚠️ 注意事项

1. **API 认证**: 如果需要，添加 API Key 认证
2. **速率限制**: 限制 AI 调用频率，避免滥用
3. **错误处理**: 返回清晰的错误信息
4. **超时设置**: 设置合理的超时时间
5. **日志记录**: 记录 AI 调用日志，便于审计

---

## 🌐 示例对话

### 示例 1: 简单查询

```
用户：帮我查一笔协议支付的交易，REQ_SN=LX260408090024C80C82F3 时间是：2026040809

AI 思考：
- 交易类型：协议支付 → 310011
- REQ_SN: LX260408090024C80C82F3
- 时间：2026040809

AI 调用：
GET /api/transaction-trace?transaction_type=310011&req_sn=LX260408090024C80C82F3&log_time=2026040809

AI 回复：
已找到该笔协议支付交易的完整链路：

📊 追踪结果
- TraceID: TC5PCfGK
- 总日志数：27 条
- 涉及应用：3 个

📍 应用链路
1. sft-aipg (入口应用): 15 条日志
2. sft-trxqry: 8 条日志
3. sft-pay: 4 条日志

交易在各应用间流转正常，未发现异常。
```

### 示例 2: 重复查询

```
用户：查一下 REQ_SN 为 202604080800000001 的交易

AI 思考：
- 用户未指定交易类型，需要先查询
- 调用 /api/log-query 获取 TraceID
- 然后根据 TraceID 调用 /api/transaction-trace

AI 回复：
发现该 REQ_SN 有 2 次查询记录（可能是重复查询）：

🔄 第一次查询 (09:00:00.304)
- TraceID: TC5PCfGK
- 日志数：27 条
- 应用链路：aipg → trxqry → pay

🔄 第二次查询 (09:00:03.547)
- TraceID: TC07bG2Y
- 日志数：22 条
- 应用链路：aipg → trxqry → pay

两次查询间隔约 3 秒，建议检查是否存在重复提交。
```

---

## 📁 相关文件

- `openapi.yaml` - OpenAPI 规范文档
- `mcp_server.py` - MCP 服务器实现
- `AI_INTEGRATION.md` - 本文档

---

## 🚀 快速开始

1. **已有 API** ✅ - 你的系统已经有完整的 API
2. **创建 OpenAPI 文档** - 定义接口规范
3. **配置 AI 平台** - 添加 Function Calling 描述
4. **测试** - 验证 AI 能否正确调用

---

<div align="center">

**让 AI 成为你的日志查询助手！** 🤖

[查看 API 文档](/api/docs) | [Function Calling 示例](#方式一 function-calling推荐)

</div>
