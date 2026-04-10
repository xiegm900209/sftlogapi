#!/bin/bash
# sftlogapi Docker 入口脚本
# 同时启动 Nginx 和 Flask

set -e

echo "🚀 启动 sftlogapi..."

# 启动 Flask 后端
echo "📦 启动 Flask 后端..."
cd /app/backend
python3 app_main.py &
FLASK_PID=$!

# 等待 Flask 启动
sleep 3

# 检查 Flask 是否启动成功
if ! ps -p $FLASK_PID > /dev/null; then
    echo "❌ Flask 启动失败"
    exit 1
fi
echo "✅ Flask 后端已启动 (PID: $FLASK_PID)"

# 启动 Nginx
echo "🌐 启动 Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# 检查 Nginx 是否启动成功
if ! ps -p $NGINX_PID > /dev/null; then
    echo "❌ Nginx 启动失败"
    exit 1
fi
echo "✅ Nginx 已启动 (PID: $NGINX_PID)"

echo "✅ sftlogapi 已就绪"
echo "🌐 访问地址：http://localhost/sftlogapi/"

# 等待所有进程
wait
