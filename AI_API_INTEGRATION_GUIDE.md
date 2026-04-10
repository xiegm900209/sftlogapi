# sftlogapi AI API 集成指南

## 📚 文档概述

本文档为智多星 AI 提供完整的 API 集成说明，包括接口详情、代码示例、最佳实践。

**版本**: v1.0  
**更新时间**: 2026-04-10  
**适用对象**: 智多星 AI 开发团队

---

## 🔐 1. 认证与鉴权

### 1.1 API Key 获取

| 环境 | API Key | 速率限制 |
|------|--------|---------|
| 生产环境 | `zhiduoxing-prod` | 100 次/分钟 |
| 测试环境 | `zhiduoxing-test` | 20 次/分钟 |

### 1.2 鉴权方式

**方式 1: Authorization Header（推荐）**
```http
Authorization: Bearer zhiduoxing-prod
```

**方式 2: Query 参数**
```
?api_key=zhiduoxing-prod
```

### 1.3 速率限制响应

```json
{
  "success": false,
  "error": "请求频率超限",
  "code": "RATE_LIMIT_EXCEEDED",
  "metadata": {
    "rate_limit": {
      "limit": 100,
      "period": "minute",
      "remaining": 0
    }
  }
}
```

---

## 🚀 2. 核心接口

### 2.1 统一查询接口（主要使用）

**接口**: `POST /api/ai/query`

**URL**: `http://172.16.2.164:8090/sftlogapi/api/ai/query`

#### 请求格式

```http
POST /api/ai/query
Host: 172.16.2.164:8090
Authorization: Bearer zhiduoxing-prod
Content-Type: application/json
```

```json
{
  "query_type": "transaction_trace",
  "params": {
    "transaction_type": "310011",
    "req_sn": "LX260408090024C80C82F3",
    "log_time": "2026040809",
    "service": "sft-aipg"
  }
}
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query_type` | string | ✅ | 查询类型：`transaction_trace`, `single_service`, `trace_id_search` |
| `params.transaction_type` | string | ⚠️ | 交易类型代码（transaction_trace 必填） |
| `params.req_sn` | string | ⚠️ | 交易序列号（与 trace_id 二选一） |
| `params.trace_id` | string | ⚠️ | TraceID（与 req_sn 二选一） |
| `params.log_time` | string | ✅ | 日志时间，10 位数字 YYYYMMDDHH |
| `params.service` | string | ❌ | 指定服务，不指定则查询所有关联服务 |

#### 响应格式

```json
{
  "success": true,
  "query_type": "transaction_trace",
  "data": {
    "transaction_type": "310011",
    "transaction_name": "协议支付",
    "transaction_code": "310011",
    "trace_id": "TCEsVt60",
    "total_logs": 93,
    "services": ["sft-aipg", "sft-trxcharge", "sft-merapi"],
    "service_count": 6,
    "logs": [
      {
        "timestamp": "2026-04-08 09:00:25.025",
        "service": "sft-aipg",
        "thread": "http-apr-8195-exec-2252",
        "level": "INFO",
        "content": "<?xml version=\"1.0\" encoding=\"GBK\"?><AIPG>...",
        "parsed": {
          "req_sn": "LX260408090024C80C82F3",
          "trx_code": "310011",
          "merchant_id": "200604000011967",
          "amount": "100"
        }
      }
    ],
    "service_results": {
      "sft-aipg": [...],
      "sft-trxcharge": [...]
    },
    "summary": {
      "start_time": "2026-04-08 09:00:25.025",
      "end_time": "2026-04-08 09:00:25.667",
      "service_count": 6,
      "log_count": 93,
      "status": "success",
      "has_error": false
    }
  },
  "metadata": {
    "query_time_ms": 10458,
    "api_version": "v1",
    "rate_limit": {
      "remaining": 99,
      "limit": 100,
      "period": "minute"
    }
  },
  "timestamp": "2026-04-10T10:00:00Z"
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.transaction_type` | string | 交易类型代码 |
| `data.transaction_name` | string | 交易类型名称 |
| `data.trace_id` | string | 实际 TraceID（从 REQ_SN 自动提取） |
| `data.total_logs` | number | 日志总数 |
| `data.services` | array | 涉及的服务列表 |
| `data.logs` | array | **完整的日志列表（所有日志）** |
| `data.service_results` | object | 按服务分组的日志 |
| `data.summary.status` | string | 交易状态：`success`, `failed`, `no_logs` |
| `metadata.query_time_ms` | number | 查询耗时（毫秒） |
| `metadata.rate_limit.remaining` | number | 剩余请求次数 |

---

### 2.2 获取交易类型列表

**接口**: `GET /api/ai/transaction-types`

**用途**: 获取所有可用的交易类型配置，用于智多星 NLP 解析

```http
GET /api/ai/transaction-types
Authorization: Bearer zhiduoxing-prod
```

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
  "timestamp": "2026-04-10T10:00:00Z"
}
```

---

### 2.3 获取服务列表

**接口**: `GET /api/ai/services`

**用途**: 获取所有可用的服务名称

```http
GET /api/ai/services
Authorization: Bearer zhiduoxing-prod
```

```json
{
  "success": true,
  "data": ["sft-aipg", "sft-trxqry", "sft-pay", "sft-merapi"],
  "count": 34,
  "timestamp": "2026-04-10T10:00:00Z"
}
```

---

### 2.4 健康检查

**接口**: `GET /api/ai/health`

**用途**: 检查 API 服务状态（无需鉴权）

```http
GET /api/ai/health
```

```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-04-10T10:00:00Z",
  "api_version": "v1"
}
```

---

## ❌ 3. 错误处理

### 3.1 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "code": "错误代码",
  "message": "详细消息",
  "timestamp": "2026-04-10T10:00:00Z"
}
```

### 3.2 错误代码列表

| 错误代码 | HTTP 状态码 | 说明 | 处理建议 |
|----------|-----------|------|---------|
| `MISSING_API_KEY` | 401 | 缺少 API Key | 添加 Authorization 头 |
| `INVALID_API_KEY` | 401 | API Key 无效 | 检查 API Key 是否正确 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 | 等待后重试 |
| `INVALID_JSON` | 400 | JSON 格式错误 | 检查请求体格式 |
| `MISSING_QUERY_TYPE` | 400 | 缺少 query_type | 添加 query_type 参数 |
| `UNSUPPORTED_QUERY_TYPE` | 400 | 不支持的查询类型 | 使用支持的类型 |
| `MISSING_TRANSACTION_TYPE` | 400 | 缺少交易类型 | 添加 transaction_type |
| `MISSING_TRACE_ID` | 400 | 缺少 TraceID/REQ_SN | 添加 trace_id 或 req_sn |
| `MISSING_LOG_TIME` | 400 | 缺少日志时间 | 添加 log_time（必填） |
| `INVALID_TRANSACTION_TYPE` | 400 | 交易类型不存在 | 检查交易类型代码 |
| `TRACE_ID_NOT_FOUND` | 400 | 无法从 REQ_SN 提取 TraceID | 检查 REQ_SN 是否正确 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 | 联系技术支持 |

---

## 📊 4. 查询类型详解

### 4.1 transaction_trace（推荐）

**用途**: 根据交易类型配置，查询全链路日志

**特点**:
- ✅ 自动从 REQ_SN 提取 TraceID
- ✅ 自动查询所有关联应用
- ✅ 返回完整交易链路

**示例**:
```json
{
  "query_type": "transaction_trace",
  "params": {
    "transaction_type": "310011",
    "req_sn": "LX260408090024C80C82F3",
    "log_time": "2026040809"
  }
}
```

---

### 4.2 single_service

**用途**: 查询单个服务的日志

**示例**:
```json
{
  "query_type": "single_service",
  "params": {
    "service": "sft-aipg",
    "trace_id": "TCEsVt60",
    "log_time": "2026040809"
  }
}
```

---

### 4.3 trace_id_search

**用途**: 搜索所有包含指定 TraceID 的日志

**示例**:
```json
{
  "query_type": "trace_id_search",
  "params": {
    "trace_id": "TCEsVt60",
    "log_time": "2026040809"
  }
}
```

---

## 💡 5. 最佳实践

### 5.1 自然语言解析流程

```
用户输入
  ↓
智多星 NLP 解析
  ↓
提取关键参数
  ↓
调用 sftlogapi API
  ↓
获取完整日志
  ↓
知识库分析
  ↓
生成用户回复
```

### 5.2 参数提取规则

| 用户输入 | 提取参数 |
|----------|---------|
| "310011 交易" | `transaction_type: "310011"` |
| "REQ_SN=LX..." | `req_sn: "LX..."` |
| "时间 2026040809" | `log_time: "2026040809"` |
| "sft-aipg 服务" | `service: "sft-aipg"` |

### 5.3 重试策略

```python
def query_with_retry(params, max_retries=3):
    for i in range(max_retries):
        response = requests.post(API_URL, json=params, headers=headers)
        
        if response.status_code == 429:  # 速率限制
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            continue
        
        if response.status_code == 500:  # 服务器错误
            time.sleep(2 ** i)  # 指数退避
            continue
        
        return response.json()
    
    raise Exception("查询失败，超过最大重试次数")
```

### 5.4 日志分析建议

```python
def analyze_logs(logs):
    """分析日志，提取关键信息"""
    
    # 1. 提取交易关键信息
    transaction_info = {}
    for log in logs:
        parsed = log.get('parsed', {})
        if parsed.get('req_sn'):
            transaction_info['req_sn'] = parsed['req_sn']
        if parsed.get('amount'):
            transaction_info['amount'] = parsed['amount']
        if parsed.get('merchant_id'):
            transaction_info['merchant_id'] = parsed['merchant_id']
    
    # 2. 判断交易状态
    status = 'success'
    for log in logs:
        if log.get('level') in ['ERROR', 'FATAL']:
            status = 'failed'
            break
        if 'error' in log.get('content', '').lower():
            status = 'failed'
            break
    
    # 3. 计算耗时
    timestamps = [log.get('timestamp') for log in logs]
    duration = calculate_duration(timestamps[0], timestamps[-1])
    
    return {
        'transaction_info': transaction_info,
        'status': status,
        'duration': duration,
        'service_count': len(set(log.get('service') for log in logs))
    }
```

---

## 🔒 6. 安全建议

1. **API Key 保管**: 不要将 API Key 硬编码在代码中，使用环境变量
2. **HTTPS**: 生产环境建议使用 HTTPS
3. **速率限制**: 实现客户端速率限制，避免触发 429
4. **错误日志**: 记录所有 API 调用错误，便于排查问题
5. **数据脱敏**: 智多星回复用户时，注意脱敏敏感信息

---

## 📞 7. 技术支持

- **项目路径**: `/root/sft/sftlogapi`
- **API 文档**: `/root/sft/sftlogapi/AI_API_README.md`
- **测试脚本**: `/root/sft/sftlogapi/AI_API_TEST.sh`
- **日志文件**: `/var/log/sftlogapi_ai.log`

---

**文档版本**: v1.0  
**创建时间**: 2026-04-10  
**作者**: sftlogapi 团队
