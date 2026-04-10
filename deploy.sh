#!/bin/bash
# 日志追踪系统 - 快速部署脚本

set -e

echo "============================================"
echo "🚀 交易日志链路追踪系统 - 快速部署"
echo "============================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

# 停止旧容器
echo "🧹 停止旧容器..."
docker rm -f log-tracker 2>/dev/null || true

# 启动容器
echo "🚀 启动容器..."
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.9

# 等待启动
echo "⏳ 等待服务启动..."
sleep 6

# 验证
echo ""
echo "=== 验证配置 ==="
CONTAINER_CONFIG=$(docker exec log-tracker cat /app/config/log_dirs.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "0")
echo "容器内配置：${CONTAINER_CONFIG} 个应用"

echo ""
echo "=== 测试 API ==="
API_SERVICES=$(curl -s http://localhost:8089/api/services 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('services', [])))" 2>/dev/null || echo "0")
echo "服务列表：${API_SERVICES} 个应用"

echo ""
if [ "$CONTAINER_CONFIG" -ge "30" ] && [ "$API_SERVICES" -ge "30" ]; then
    echo "✅ 部署成功！"
    echo ""
    echo "🌐 访问地址：http://localhost:8089"
    echo ""
    echo "📋 功能页面:"
    echo "  - 首页：http://localhost:8089/"
    echo "  - 日志追踪查询：http://localhost:8089/log-query"
    echo "  - 交易类型追踪：http://localhost:8089/transaction-trace"
    echo "  - 交易类型管理：http://localhost:8089/transaction-types"
    echo "  - 应用日志配置：http://localhost:8089/app-log-config"
    echo ""
else
    echo "⚠️  配置可能未正确加载，请检查:"
    echo "  docker logs log-tracker"
fi

echo "============================================"
