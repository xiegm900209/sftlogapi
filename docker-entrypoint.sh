#!/bin/bash
# sftlogapi Docker 入口脚本
# 同时启动 Nginx 和 Flask

set -e

echo "🚀 启动 sftlogapi..."

# 启动 Flask 后端
echo "📦 启动 Flask 后端..."
cd /app/backend
nohup python3 app_main.py > /var/log/flask.log 2>&1 &
sleep 5

# 检查 Flask 是否启动
if curl -s http://127.0.0.1:5000/api/ai/health > /dev/null; then
    echo "✅ Flask 后端已启动"
else
    echo "❌ Flask 启动失败"
    cat /var/log/flask.log
    exit 1
fi

# 启动 Nginx
echo "🌐 启动 Nginx..."
nginx -g "daemon off;" &
echo "✅ Nginx 已启动"

echo "✅ sftlogapi 已就绪"
echo "🌐 访问地址：http://localhost/sftlogapi/"

# 等待所有进程
wait
