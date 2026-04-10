#!/bin/bash
# sftlogapi AI API 测试脚本

BASE_URL="http://172.16.2.164:8090/sftlogapi"
API_KEY="zhiduoxing-prod"

echo "======================================"
echo "sftlogapi AI API 测试"
echo "======================================"
echo

# 1. 健康检查
echo "1. 健康检查..."
curl -s "${BASE_URL}/api/ai/health" | python3 -m json.tool
echo

# 2. 获取交易类型列表
echo "2. 获取交易类型列表..."
curl -s -X GET "${BASE_URL}/api/ai/transaction-types" \
  -H "Authorization: Bearer ${API_KEY}" | python3 -m json.tool | head -30
echo

# 3. 获取服务列表
echo "3. 获取服务列表..."
curl -s -X GET "${BASE_URL}/api/ai/services" \
  -H "Authorization: Bearer ${API_KEY}" | python3 -m json.tool
echo

# 4. 交易类型追踪查询
echo "4. 交易类型追踪查询..."
curl -s -X POST "${BASE_URL}/api/ai/query" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "transaction_trace",
    "params": {
      "transaction_type": "310011",
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }' | python3 -m json.tool
echo

# 5. 单服务查询
echo "5. 单服务查询..."
curl -s -X POST "${BASE_URL}/api/ai/query" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "single_service",
    "params": {
      "service": "sft-aipg",
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }' | python3 -m json.tool
echo

# 6. TraceID 搜索
echo "6. TraceID 搜索..."
curl -s -X POST "${BASE_URL}/api/ai/query" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "trace_id_search",
    "params": {
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }' | python3 -m json.tool
echo

# 7. 测试无 API Key
echo "7. 测试无 API Key（应返回 401）..."
curl -s -X POST "${BASE_URL}/api/ai/query" \
  -H "Content-Type: application/json" \
  -d '{"query_type":"transaction_trace","params":{}}' | python3 -m json.tool
echo

# 8. 测试无效 API Key
echo "8. 测试无效 API Key（应返回 401）..."
curl -s -X POST "${BASE_URL}/api/ai/query" \
  -H "Authorization: Bearer invalid-key" \
  -H "Content-Type: application/json" \
  -d '{"query_type":"transaction_trace","params":{}}' | python3 -m json.tool
echo

echo "======================================"
echo "测试完成"
echo "======================================"
