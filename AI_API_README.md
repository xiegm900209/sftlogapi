# sftlogapi AI API 接口文档

## 📚 概述

为智多星 AI 提供的交易日志查询接口，支持自然语言查询交易全链路日志。

**接口地址**: `http://172.16.2.164:8090/sftlogapi/api/ai`

---

## 🔐 鉴权方式

### API Key

所有 AI 接口（除健康检查外）都需要 API Key 鉴权。

**方式 1: Authorization Header（推荐）**
```http
Authorization: Bearer zhiduoxing-prod
```

**方式 2: Query 参数**
```
?api_key=zhiduoxing-prod
```

### 可用 API Key

| Key | 环境 | 速率限制 |
|-----|------|---------|
| `zhiduoxing-prod` | 生产环境 | 100 次/分钟 |
| `zhiduoxing-test` | 测试环境 | 20 次/分钟 |

---

## 🚀 接口列表

### 1. 健康检查（无需鉴权）

**接口**: `GET /api/ai/health`

**请求**:
```bash
curl http://172.16.2.164:8090/sftlogapi/api/ai/health
```

**响应**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-04-10T09:00:00Z",
  "api_version": "v1"
}
```

---

### 2. 统一查询接口

**接口**: `POST /api/ai/query`

**请求**:
```http
POST /api/ai/query
Authorization: Bearer zhiduoxing-prod
Content-Type: application/json
```

**请求体**:
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

**响应**:
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
      "start_time": "2026-04-08 09:00:01",
      "end_time": "2026-04-08 09:00:05",
      "status": "success"
    }
  },
  "metadata": {
    "query_time_ms": 234,
    "rate_limit": {
      "remaining": 99,
      "limit": 100,
      "period": "minute"
    }
  },
  "timestamp": "2026-04-10T09:00:00Z"
}
```

---

### 3. 获取交易类型列表

**接口**: `GET /api/ai/transaction-types`

**请求**:
```bash
curl -X GET "http://172.16.2.164:8090/sftlogapi/api/ai/transaction-types" \
  -H "Authorization: Bearer zhiduoxing-prod"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "310011": {
      "name": "协议支付",
      "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
    },
    "310016": {
      "name": "批量协议支付",
      "apps": ["sft-aipg", "sft-trxqry", "sft-batchpay"]
    }
  },
  "count": 12,
  "timestamp": "2026-04-10T09:00:00Z"
}
```

---

### 4. 获取服务列表

**接口**: `GET /api/ai/services`

**请求**:
```bash
curl -X GET "http://172.16.2.164:8090/sftlogapi/api/ai/services" \
  -H "Authorization: Bearer zhiduoxing-prod"
```

**响应**:
```json
{
  "success": true,
  "data": ["sft-aipg", "sft-trxqry", "sft-pay", ...],
  "count": 34,
  "timestamp": "2026-04-10T09:00:00Z"
}
```

---

## 📊 查询类型详解

### 1. transaction_trace（交易类型追踪）

**用途**: 根据交易类型配置，查询全链路日志

**参数**:
- `transaction_type` (必填): 交易类型代码，如 `310011`
- `trace_id` 或 `req_sn` (必填): 交易标识
- `log_time` (必填): 日志时间，10 位数字 (YYYYMMDDHH)
- `service` (可选): 指定服务，不指定则查询所有关联服务

**示例**:
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

---

### 2. single_service（单服务查询）

**用途**: 查询单个服务的日志

**参数**:
- `service` (必填): 服务名称，如 `sft-aipg`
- `trace_id` 或 `req_sn` (必填): 交易标识
- `log_time` (必填): 日志时间

**示例**:
```json
{
  "query_type": "single_service",
  "params": {
    "service": "sft-aipg",
    "trace_id": "LX260408090024C80C82F3",
    "log_time": "2026040809"
  }
}
```

---

### 3. trace_id_search（TraceID 搜索）

**用途**: 搜索所有包含指定 TraceID 的日志

**参数**:
- `trace_id` (必填): TraceID
- `log_time` (必填): 日志时间
- `services` (可选): 服务列表，不指定则查询所有服务

**示例**:
```json
{
  "query_type": "trace_id_search",
  "params": {
    "trace_id": "LX260408090024C80C82F3",
    "log_time": "2026040809"
  }
}
```

---

## ❌ 错误响应

**格式**:
```json
{
  "success": false,
  "error": "错误描述",
  "code": "错误代码",
  "timestamp": "2026-04-10T09:00:00Z"
}
```

**错误代码**:

| 代码 | HTTP 状态码 | 说明 |
|------|-----------|------|
| `MISSING_API_KEY` | 401 | 缺少 API Key |
| `INVALID_API_KEY` | 401 | 无效的 API Key |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INVALID_JSON` | 400 | JSON 格式错误 |
| `MISSING_QUERY_TYPE` | 400 | 缺少 query_type |
| `UNSUPPORTED_QUERY_TYPE` | 400 | 不支持的查询类型 |
| `MISSING_TRANSACTION_TYPE` | 400 | 缺少交易类型 |
| `MISSING_TRACE_ID` | 400 | 缺少 TraceID |
| `MISSING_LOG_TIME` | 400 | 缺少日志时间 |
| `INVALID_TRANSACTION_TYPE` | 400 | 交易类型不存在 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 💡 智多星集成示例

### Python 示例

```python
import requests

class SFTLogAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def query_transaction(self, transaction_type, trace_id, log_time):
        """查询交易全链路日志"""
        url = f"{self.base_url}/api/ai/query"
        
        payload = {
            "query_type": "transaction_trace",
            "params": {
                "transaction_type": transaction_type,
                "trace_id": trace_id,
                "log_time": log_time
            }
        }
        
        response = self.session.post(url, json=payload)
        result = response.json()
        
        if result['success']:
            return self.format_for_user(result['data'])
        else:
            return f"查询失败：{result['error']}"
    
    def format_for_user(self, data):
        """格式化为用户友好的回复"""
        summary = data.get('summary', {})
        
        response = f"""
📊 交易查询结果

交易类型：{data.get('transaction_name')}({data.get('transaction_type')})
TraceID: {data.get('trace_id')}
日志数量：{data.get('total_logs')} 条
涉及服务：{data.get('service_count')} 个

交易状态：{'✅ 成功' if summary.get('status') == 'success' else '❌ 失败'}
时间范围：{summary.get('start_time', 'N/A')} 至 {summary.get('end_time', 'N/A')}
"""
        
        # 添加详细日志
        if data.get('logs'):
            response += "\n📝 详细日志:\n"
            for log in data['logs'][:10]:  # 只显示前 10 条
                response += f"- [{log.get('timestamp')}] {log.get('service')} {log.get('level')}: {log.get('content')[:100]}...\n"
            
            if len(data['logs']) > 10:
                response += f"... 还有 {len(data['logs']) - 10} 条日志\n"
        
        return response

# 使用示例
api = SFTLogAPI(
    base_url="http://172.16.2.164:8090/sftlogapi",
    api_key="zhiduoxing-prod"
)

# 查询交易
result = api.query_transaction(
    transaction_type="310011",
    trace_id="LX260408090024C80C82F3",
    log_time="2026040809"
)

print(result)
```

---

## 🧪 测试

### 使用测试脚本

```bash
cd /root/sft/sftlogapi
./AI_API_TEST.sh
```

### 手动测试

```bash
# 健康检查
curl http://172.16.2.164:8090/sftlogapi/api/ai/health

# 查询交易
curl -X POST "http://172.16.2.164:8090/sftlogapi/api/ai/query" \
  -H "Authorization: Bearer zhiduoxing-prod" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "transaction_trace",
    "params": {
      "transaction_type": "310011",
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }'
```

---

## 📈 性能指标

- **平均响应时间**: < 500ms
- **速率限制**: 100 次/分钟（生产环境）
- **并发支持**: 支持多并发请求
- **日志容量**: 支持 GB 级日志文件查询

---

## 🔒 安全建议

1. **定期轮换 API Key**
2. **监控异常请求**
3. **限制查询时间范围**（防止全量扫描）
4. **记录审计日志**（所有请求都会记录）

---

## 📞 联系支持

- **项目路径**: `/root/sft/sftlogapi`
- **日志文件**: `/var/log/sftlogapi_ai.log`
- **配置文件**: `/root/sft/sftlogapi/config/api_keys.json`

---

**文档版本**: v1.0  
**更新时间**: 2026-04-10  
**作者**: sftlogapi 团队
