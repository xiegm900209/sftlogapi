# AI 调用接口设计方案

## 📋 需求概述

为公司智多星 AI 提供自然语言查询交易日志的能力，用户可以用自然语言查询，智多星解析后调用 sftlogapi 接口，返回结构化 JSON 数据。

### 使用场景示例

**用户输入**：
> 请给我 310011 交易的日志，LX260408090024C80C82F3 时间 2026040809

**智多星解析**：
- 交易类型：`310011`（协议支付）
- TraceID/REQ_SN：`LX260408090024C80C82F3`
- 日志时间：`2026040809`

**调用接口**：`POST /api/ai/query`

**返回**：整笔交易的全链路日志（JSON 格式）

---

## 🏗️ 架构设计

```
┌─────────────┐    自然语言    ┌─────────────┐   HTTP+JSON    ┌──────────────────┐
│   用户       │ ────────────> │   智多星 AI  │ ────────────> │   sftlogapi      │
│             │               │             │                │   (交易日志系统)  │
└─────────────┘               └─────────────┘                └──────────────────┘
                                                           │
                                                           │ 查询日志
                                                           ▼
                                                    ┌──────────────────┐
                                                    │  /root/sft/      │
                                                    │  testlogs/       │
                                                    └──────────────────┘
```

---

## 🔐 1. API Key 鉴权机制

### 1.1 配置文件

创建 `/root/sft/sftlogapi/config/api_keys.json`：

```json
{
  "api_keys": {
    "zhiduoxing-prod": {
      "name": "智多星生产环境",
      "enabled": true,
      "created_at": "2026-04-10T00:00:00Z",
      "rate_limit": 100,
      "rate_limit_period": "minute"
    },
    "zhiduoxing-test": {
      "name": "智多星测试环境",
      "enabled": true,
      "created_at": "2026-04-10T00:00:00Z",
      "rate_limit": 10,
      "rate_limit_period": "minute"
    }
  }
}
```

### 1.2 鉴权方式

**Header 传递**：
```
Authorization: Bearer <api_key>
```

**或 Query 参数**：
```
?api_key=<api_key>
```

### 1.3 鉴权中间件

```python
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从 Header 或 Query 获取 API Key
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not api_key:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': '缺少 API Key', 'code': 'MISSING_API_KEY'}), 401
        
        # 验证 API Key
        if not validate_api_key(api_key):
            return jsonify({'error': '无效的 API Key', 'code': 'INVALID_API_KEY'}), 401
        
        # 检查速率限制
        if not check_rate_limit(api_key):
            return jsonify({'error': '请求频率超限', 'code': 'RATE_LIMIT_EXCEEDED'}), 429
        
        return f(*args, **kwargs)
    return decorated
```

---

## 🚀 2. AI 专用接口设计

### 2.1 统一查询接口（推荐）

**接口**：`POST /api/ai/query`

**请求**：
```json
{
  "query_type": "transaction_trace",
  "params": {
    "transaction_type": "310011",
    "trace_id": "LX260408090024C80C82F3",
    "log_time": "2026040809",
    "service": "sft-aipg"
  }
}
```

**响应**：
```json
{
  "success": true,
  "query_type": "transaction_trace",
  "data": {
    "transaction_type": "310011",
    "transaction_name": "协议支付",
    "trace_id": "LX260408090024C80C82F3",
    "total_logs": 15,
    "services": ["sft-aipg", "sft-trxqry", "sft-pay"],
    "logs": [
      {
        "service": "sft-aipg",
        "timestamp": "2026-04-08 09:00:01.123",
        "level": "INFO",
        "content": "...",
        "parsed": {...}
      }
    ]
  },
  "metadata": {
    "query_time_ms": 234,
    "api_version": "v1"
  }
}
```

### 2.2 自然语言解析接口（可选）

**接口**：`POST /api/ai/parse`

**用途**：智多星可以先调用此接口验证解析结果

**请求**：
```json
{
  "natural_language": "请给我 310011 交易的日志，LX260408090024C80C82F3 时间 2026040809"
}
```

**响应**：
```json
{
  "success": true,
  "parsed": {
    "query_type": "transaction_trace",
    "params": {
      "transaction_type": "310011",
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  },
  "confidence": 0.95
}
```

---

## 📊 3. 支持的查询类型

### 3.1 交易类型追踪 (`transaction_trace`)

**参数**：
- `transaction_type` (必填): 交易类型代码，如 `310011`
- `trace_id` 或 `req_sn` (必填): 交易标识
- `log_time` (必填): 日志时间，10 位数字
- `service` (可选): 指定服务

**返回**：全链路日志，按服务分组

### 3.2 单应用查询 (`single_service`)

**参数**：
- `service` (必填): 服务名称，如 `sft-aipg`
- `trace_id` 或 `req_sn` (必填): 交易标识
- `log_time` (必填): 日志时间

**返回**：单个服务的日志

### 3.3 TraceID 查询 (`trace_id_search`)

**参数**：
- `trace_id` (必填): TraceID
- `log_time` (必填): 日志时间
- `services` (可选): 服务列表

**返回**：所有匹配 TraceID 的日志

---

## 🔧 4. 后端改造清单

### 4.1 新增文件

```
backend/
├── ai_api/
│   ├── __init__.py          # AI API 初始化
│   ├── auth.py              # API Key 鉴权
│   ├── query_handler.py     # 查询处理逻辑
│   └── response_formatter.py # 响应格式化
config/
├── api_keys.json            # API Key 配置
└── api_keys.json.sample     # 配置模板
```

### 4.2 修改文件

```
backend/
└── app_main.py              # 添加 AI 路由
```

### 4.3 核心代码结构

```python
# backend/ai_api/auth.py
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

class APIKeyManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.api_keys = {}
        self.rate_limits = defaultdict(list)
        self.load_keys()
    
    def load_keys(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.api_keys = config.get('api_keys', {})
    
    def validate(self, api_key):
        if api_key not in self.api_keys:
            return False
        key_info = self.api_keys[api_key]
        return key_info.get('enabled', False)
    
    def check_rate_limit(self, api_key):
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        limit = key_info.get('rate_limit', 100)
        period = key_info.get('rate_limit_period', 'minute')
        
        # 实现速率限制逻辑
        now = datetime.now()
        window = timedelta(minutes=1) if period == 'minute' else timedelta(hours=1)
        
        # 清理过期记录
        self.rate_limits[api_key] = [
            t for t in self.rate_limits[api_key] 
            if now - t < window
        ]
        
        if len(self.rate_limits[api_key]) >= limit:
            return False
        
        self.rate_limits[api_key].append(now)
        return True

# backend/ai_api/query_handler.py
class AIQueryHandler:
    def __init__(self, analyzer, log_dir):
        self.analyzer = analyzer
        self.log_dir = log_dir
    
    def handle_transaction_trace(self, params):
        """处理交易类型追踪查询"""
        transaction_type = params.get('transaction_type')
        trace_id = params.get('trace_id') or params.get('req_sn')
        log_time = params.get('log_time')
        
        # 获取交易类型配置
        type_info = self.analyzer.transaction_types.get(transaction_type)
        if not type_info:
            return {'success': False, 'error': f'交易类型 {transaction_type} 不存在'}
        
        # 执行追踪
        result = self.analyzer.trace_transaction_chain(
            trace_id, 
            transaction_type,
            log_time=log_time
        )
        
        # 格式化响应
        return self.format_response(result, type_info)
    
    def format_response(self, result, type_info):
        """格式化为 AI 友好的响应"""
        return {
            'transaction_type': type_info.get('code'),
            'transaction_name': type_info.get('name'),
            'trace_id': result.get('trace_id'),
            'total_logs': len(result.get('logs', [])),
            'services': list(set(log.get('service') for log in result.get('logs', []))),
            'logs': result.get('logs', []),
            'summary': self.generate_summary(result)
        }
    
    def generate_summary(self, result):
        """生成交易摘要（给 AI 用）"""
        logs = result.get('logs', [])
        if not logs:
            return '未找到相关日志'
        
        first_log = logs[0]
        last_log = logs[-1]
        
        return {
            'start_time': first_log.get('timestamp'),
            'end_time': last_log.get('timestamp'),
            'service_count': len(set(log.get('service') for log in logs)),
            'status': self.infer_status(logs)
        }
    
    def infer_status(self, logs):
        """推断交易状态"""
        for log in logs:
            content = log.get('content', '').lower()
            if 'error' in content or 'fail' in content or 'exception' in content:
                return 'failed'
        return 'success'
```

---

## 📝 5. 接口文档

### 5.1 统一查询接口

**URL**: `POST /api/ai/query`

**Headers**:
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Request Body**:
```json
{
  "query_type": "transaction_trace",
  "params": {
    "transaction_type": "310011",
    "trace_id": "LX260408090024C80C82F3",
    "log_time": "2026040809"
  }
}
```

**Response Success**:
```json
{
  "success": true,
  "query_type": "transaction_trace",
  "data": {
    "transaction_type": "310011",
    "transaction_name": "协议支付",
    "trace_id": "LX260408090024C80C82F3",
    "total_logs": 15,
    "services": ["sft-aipg", "sft-trxqry", "sft-pay"],
    "logs": [...],
    "summary": {
      "start_time": "2026-04-08 09:00:01.123",
      "end_time": "2026-04-08 09:00:05.456",
      "service_count": 3,
      "status": "success"
    }
  },
  "metadata": {
    "query_time_ms": 234,
    "api_version": "v1",
    "timestamp": "2026-04-10T09:00:00Z"
  }
}
```

**Response Error**:
```json
{
  "success": false,
  "error": "交易类型 310011 不存在",
  "code": "INVALID_TRANSACTION_TYPE",
  "metadata": {
    "api_version": "v1",
    "timestamp": "2026-04-10T09:00:00Z"
  }
}
```

### 5.2 错误码定义

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `MISSING_API_KEY` | 401 | 缺少 API Key |
| `INVALID_API_KEY` | 401 | 无效的 API Key |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INVALID_PARAMS` | 400 | 参数错误 |
| `NOT_FOUND` | 404 | 未找到数据 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 🚀 6. 实施步骤

### Phase 1: 基础鉴权 (1 天)
- [ ] 创建 `api_keys.json` 配置文件
- [ ] 实现 API Key 验证中间件
- [ ] 实现速率限制
- [ ] 添加鉴权日志

### Phase 2: AI 查询接口 (2 天)
- [ ] 创建 `AIQueryHandler` 类
- [ ] 实现 `POST /api/ai/query` 接口
- [ ] 支持 `transaction_trace` 查询类型
- [ ] 格式化响应数据

### Phase 3: 增强功能 (1 天)
- [ ] 添加自然语言解析接口（可选）
- [ ] 支持更多查询类型
- [ ] 添加查询统计
- [ ] 优化响应性能

### Phase 4: 测试与文档 (1 天)
- [ ] 编写单元测试
- [ ] 编写 API 文档
- [ ] 智多星联调测试
- [ ] 性能压测

---

## 🔒 7. 安全考虑

### 7.1 API Key 管理
- API Key 使用 UUID 或随机字符串
- 支持 API Key 启用/禁用
- 支持 API Key 过期时间
- 定期轮换 API Key

### 7.2 速率限制
- 按 API Key 限制请求频率
- 防止恶意查询（如全量扫描）
- 日志时间范围限制（防止过载）

### 7.3 审计日志
```json
{
  "timestamp": "2026-04-10T09:00:00Z",
  "api_key": "zhiduoxing-prod",
  "query_type": "transaction_trace",
  "params": {...},
  "response_status": "success",
  "query_time_ms": 234,
  "client_ip": "192.168.1.100"
}
```

---

## 📊 8. 性能优化建议

1. **缓存热点数据**
   - 交易类型配置缓存
   - 常用 TraceID 查询结果缓存

2. **异步处理**
   - 大批量查询使用异步接口
   - 返回 `query_id`，轮询结果

3. **日志索引**
   - 为 TraceID 建立索引
   - 加速查询速度

---

## 📞 9. 智多星对接示例

```python
# 智多星侧调用示例
import requests

def query_transaction_logs(natural_query):
    # 1. 解析自然语言（智多星内部处理）
    params = parse_natural_language(natural_query)
    # params = {
    #   "transaction_type": "310011",
    #   "trace_id": "LX260408090024C80C82F3",
    #   "log_time": "2026040809"
    # }
    
    # 2. 调用 sftlogapi
    response = requests.post(
        'http://172.16.2.164:8090/sftlogapi/api/ai/query',
        json={
            "query_type": "transaction_trace",
            "params": params
        },
        headers={
            'Authorization': 'Bearer zhiduoxing-prod',
            'Content-Type': 'application/json'
        }
    )
    
    # 3. 解析响应
    result = response.json()
    if result['success']:
        return format_for_user(result['data'])
    else:
        return f"查询失败：{result['error']}"

def format_for_user(data):
    """格式化为用户友好的回复"""
    summary = data['summary']
    return f"""
找到 {data['total_logs']} 条日志，涉及 {summary['service_count']} 个服务。
交易状态：{summary['status']}
时间范围：{summary['start_time']} 至 {summary['end_time']}

详细日志：
{format_logs(data['logs'])}
"""
```

---

## ✅ 10. 验收标准

- [ ] API Key 鉴权正常工作
- [ ] 速率限制生效
- [ ] 交易类型追踪返回正确数据
- [ ] 响应时间 < 500ms（95% 请求）
- [ ] 错误处理完善
- [ ] 智多星联调成功
- [ ] 审计日志完整

---

**文档版本**: v1.0  
**创建时间**: 2026-04-10  
**作者**: sftlogapi 团队
