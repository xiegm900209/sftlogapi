# sftlogapi - 纯 Flask 应用镜像
# 版本：v1.0.0
# 基于 Python 3.9

FROM python:3.9-slim

LABEL maintainer="xiegm900209"
LABEL version="1.0.0"
LABEL description="sftlogapi - 交易日志链路追踪系统（纯 Flask 应用）"

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app_main.py

# 创建工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制配置文件
COPY config/ ./config/

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/ai/health || exit 1

# 启动命令
CMD ["python3", "backend/app_main.py"]
