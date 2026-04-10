#!/bin/bash
# Docker 容器启动脚本
# 同时启动 Nginx 和 Flask 应用

set -e

echo "🚀 启动交易日志链路追踪系统..."

# 启动 Flask 后端（后台运行）
echo "📦 启动 Flask 后端..."
cd /app/backend
nohup python3 app_main.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!
echo "✅ Flask 后端已启动 (PID: $FLASK_PID)"

# 等待 Flask 启动
sleep 3

# 检查 Flask 是否正常运行
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "❌ Flask 启动失败，查看日志:"
    cat /tmp/flask.log
    exit 1
fi

# 启动 Nginx
echo "🌐 启动 Nginx..."
nginx -g 'daemon off;' &
NGINX_PID=$!
echo "✅ Nginx 已启动 (PID: $NGINX_PID)"

# 等待进程
wait
