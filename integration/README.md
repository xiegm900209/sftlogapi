# 智多星集成代码说明

## 📦 安装

```bash
cd /root/sft/sftlogapi/integration
pip install -r requirements.txt
```

## 🚀 快速开始

### 方式 1: 自然语言查询

```python
from zhiduoxing_client import ZhiduoxingIntegration

# 初始化
zhiduoxing = ZhiduoxingIntegration()

# 自然语言查询
user_input = "帮我看下 310011 交易的日志，REQ_SN=LX260408090024C80C82F3，时间 2026040809"
result = zhiduoxing.natural_language_query(user_input)

# 输出结果
if result.get('success'):
    print(result['user_message'])
else:
    print(f"查询失败：{result['error']}")
```

### 方式 2: 直接查询

```python
from zhiduoxing_client import ZhiduoxingIntegration

zhiduoxing = ZhiduoxingIntegration()

result = zhiduoxing.query_and_analyze(
    transaction_type="310011",
    req_sn="LX260408090024C80C82F3",
    log_time="2026040809"
)

if result['success']:
    print(f"交易状态：{result['summary']['status']}")
    print(f"日志数量：{result['summary']['total_logs']}")
```

### 方式 3: 获取交易类型列表

```python
from zhiduoxing_client import ZhiduoxingIntegration

zhiduoxing = ZhiduoxingIntegration()

types = zhiduoxing.list_transaction_types()
for t in types:
    print(f"{t['code']}: {t['name']}")
```

## 📊 返回结果说明

### 自然语言查询结果

```json
{
  "success": true,
  "summary": {
    "transaction_type": "310011",
    "transaction_name": "协议支付",
    "trace_id": "TCEsVt60",
    "req_sn": "LX260408090024C80C82F3",
    "status": "success",
    "total_logs": 93,
    "service_count": 6,
    "duration_ms": 642,
    "start_time": "2026-04-08 09:00:25.025",
    "end_time": "2026-04-08 09:00:25.667",
    "services": ["sft-aipg", "sft-trxcharge", ...]
  },
  "transaction_info": {
    "req_sn": "LX260408090024C80C82F3",
    "merchant_id": "200604000011967",
    "amount": "100",
    "trx_code": "310011"
  },
  "flow_analysis": {
    "total_services": 6,
    "flow": [
      {
        "service": "sft-aipg",
        "description": "协议支付网关",
        "log_count": 22,
        "first_time": "2026-04-08 09:00:25.025",
        "last_time": "2026-04-08 09:00:25.667"
      }
    ]
  },
  "anomalies": [],
  "suggestions": ["✅ 交易正常，未发现明显问题"],
  "user_message": "✅ **交易查询结果**\n\n📋 **基本信息**\n..."
}
```

## 🔧 配置说明

### 自定义配置

```python
from zhiduoxing_client import ZhiduoxingIntegration, Config

config = Config(
    base_url="http://172.16.2.164:8090/sftlogapi",
    api_key="zhiduoxing-prod",
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)

zhiduoxing = ZhiduoxingIntegration(config)
```

### 环境变量

```bash
export SFTLOG_BASE_URL="http://172.16.2.164:8090/sftlogapi"
export SFTLOG_API_KEY="zhiduoxing-prod"
```

## 📝 自然语言解析规则

支持以下格式：

| 用户输入 | 提取结果 |
|----------|---------|
| "310011 交易" | transaction_type: "310011" |
| "REQ_SN=LX..." | req_sn: "LX..." |
| "req_sn: LX..." | req_sn: "LX..." |
| "交易号 LX..." | req_sn: "LX..." |
| "时间 2026040809" | log_time: "2026040809" |
| "2026040809" | log_time: "2026040809" |

## 🧪 测试

```bash
# 运行测试
python zhiduoxing_client.py

# 测试特定查询
python -c "
from zhiduoxing_client import ZhiduoxingIntegration
z = ZhiduoxingIntegration()
r = z.natural_language_query('帮我看下 310011 交易，LX260408090024C80C82F3，时间 2026040809')
print(r.get('user_message', r))
"
```

## 📞 技术支持

- **API 文档**: `/root/sft/sftlogapi/AI_API_INTEGRATION_GUIDE.md`
- **项目路径**: `/root/sft/sftlogapi`
- **日志文件**: `/var/log/sftlogapi_ai.log`

---

**版本**: v1.0  
**创建时间**: 2026-04-10
