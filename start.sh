#!/bin/bash
# sftlogapi 一键启动脚本（本地部署）

set -e

echo "🚀 启动 sftlogapi..."

# 检查是否已有进程运行
EXISTING_PID=$(ps aux | grep "[p]ython3 app_main.py" | grep "sftlogapi" | awk '{print $2}' | head -1)
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️  检测到已有进程运行 (PID: $EXISTING_PID)，停止中..."
    kill $EXISTING_PID 2>/dev/null || true
    sleep 1
fi

# 复制前端静态文件到 Web 目录
echo "📦 部署前端静态文件..."
mkdir -p /var/www/sftlogapi
cp -r /root/sft/sftlogapi/frontend/dist/* /var/www/sftlogapi/

# 启动 Flask 后端
echo "🌐 启动 Flask 后端 (端口 5001)..."
cd /root/sft/sftlogapi/backend
nohup python3 app_main.py > /var/log/sftlogapi.log 2>&1 &
FLASK_PID=$!

sleep 2

# 检查进程是否启动成功
if ps -p $FLASK_PID > /dev/null; then
    echo "✅ sftlogapi 已启动!"
    echo "🌐 访问地址：http://172.16.2.164:8090/sftlogapi/"
    echo "📋 查看日志：tail -f /var/log/sftlogapi.log"
    echo "🔧 后端进程 PID: $FLASK_PID"
else
    echo "❌ 启动失败，请检查日志：/var/log/sftlogapi.log"
    exit 1
fi
