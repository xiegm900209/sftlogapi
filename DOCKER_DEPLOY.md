# sftlogapi Docker 部署指南

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| **镜像名称** | sftlogapi:v1.0.0 |
| **镜像文件** | sftlogapi-v1.0.0.tar |
| **镜像大小** | ~53MB |
| **基础镜像** | Python 3.9-slim + Node 18-alpine |
| **端口** | 80 (容器内) → 8090 (宿主机) |
| **Flask 端口** | 5000 (容器内) |

---

## 🚀 快速部署

### 1. 加载镜像

```bash
# 加载镜像文件
docker load -i sftlogapi-v1.0.0.tar

# 验证镜像
docker images | grep sftlogapi
# 应显示：sftlogapi   v1.0.0   xxxxx   2 days ago   ~180MB
```

### 2. 准备日志目录

```bash
# 确保日志目录存在
mkdir -p /root/sft/testlogs

# 验证日志文件
ls -la /root/sft/testlogs/
```

### 3. 启动容器

```bash
docker run -d \
  --name sftlogapi \
  -p 8090:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  --restart unless-stopped \
  sftlogapi:v1.0.0
```

### 4. 验证部署

```bash
# 查看容器状态
docker ps | grep sftlogapi

# 查看启动日志
docker logs sftlogapi

# 测试健康检查
curl http://localhost:8090/sftlogapi/api/ai/health

# 测试 API
curl http://localhost:8090/sftlogapi/api/ai/services
```

---

## 🌐 访问地址

### 直接访问

```
http://localhost:8090/sftlogapi/
```

### 通过外部 Nginx 反向代理

#### Nginx 配置

```nginx
location /sftlogapi/ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    
    proxy_pass http://127.0.0.1:8090/;
    
    proxy_connect_timeout 600;
    proxy_read_timeout 600;
    proxy_send_timeout 600;
    client_max_body_size 500m;
}
```

#### 访问地址

```
https://your-domain.com/sftlogapi/
```

---

## 🔧 常用命令

### 容器管理

```bash
# 启动
docker start sftlogapi

# 停止
docker stop sftlogapi

# 重启
docker restart sftlogapi

# 删除
docker rm -f sftlogapi
```

### 日志查看

```bash
# 实时日志
docker logs -f sftlogapi

# 最近 100 行
docker logs --tail 100 sftlogapi

# 进入容器
docker exec -it sftlogapi /bin/bash
```

---

## 📊 容器架构

```
┌─────────────────────────────────────┐
│         Docker Container            │
│                                     │
│  ┌─────────────┐   ┌──────────────┐ │
│  │   Nginx     │ → │    Flask     │ │
│  │   (Port 80) │   │  (Port 5000) │ │
│  └─────────────┘   └──────────────┘ │
│         │                  │         │
│         └──────────────────┘         │
└─────────────────────────────────────┘
         │                  │
         ▼                  ▼
    宿主机:8090      /root/sft/testlogs
```

---

## 📁 目录结构

```
sftlogapi/
├── Dockerfile              # Docker 构建文件
├── docker-compose.yml      # Docker Compose 配置
├── docker-entrypoint.sh    # 启动脚本
├── nginx-docker.conf       # Nginx 配置
├── .dockerignore           # Docker 忽略文件
├── backend/
│   ├── app_main.py         # Flask 主应用
│   └── ai_api/             # AI API 模块
├── frontend/
│   └── dist/               # 构建后的前端
├── config/
│   ├── log_dirs.json       # 日志目录配置
│   ├── transaction_types.json  # 交易类型配置
│   └── api_keys.json       # API Key 配置
└── DOCKER_DEPLOY.md        # 本部署文档
```

---

## 🔐 配置说明

### 日志目录配置

文件：`config/log_dirs.json`

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry",
  ...
}
```

**注意**: 容器内路径是 `/app/logs/`，挂载到宿主机的 `/root/sft/testlogs`

### API Key 配置

文件：`config/api_keys.json`

```json
{
  "api_keys": {
    "zhiduoxing-prod": {
      "name": "智多星生产环境",
      "enabled": true,
      "rate_limit": 100
    }
  }
}
```

---

## 🧪 测试验证

### 1. 健康检查

```bash
curl http://localhost:8090/sftlogapi/api/ai/health
```

**预期响应**:
```json
{
  "success": true,
  "status": "healthy",
  "api_version": "v1"
}
```

### 2. 获取服务列表

```bash
curl http://localhost:8090/sftlogapi/api/ai/services
```

**预期**: 返回 34 个服务

### 3. 查询交易日志

```bash
curl -X POST "http://localhost:8090/sftlogapi/api/ai/query" \
  -H "Authorization: Bearer zhiduoxing-prod" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "transaction_trace",
    "params": {
      "transaction_type": "310011",
      "req_sn": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }'
```

**预期**: 返回 93 条日志

---

## 🔧 故障排查

### 容器无法启动

```bash
# 查看日志
docker logs sftlogapi

# 检查配置
docker exec sftlogapi cat /app/config/log_dirs.json

# 检查日志目录
docker exec sftlogapi ls -la /app/logs
```

### API 返回 502

```bash
# 检查 Flask 是否运行
docker exec sftlogapi curl http://127.0.0.1:5000/api/ai/health

# 查看 Flask 日志
docker exec sftlogapi cat /var/log/flask.log

# 重启容器
docker restart sftlogapi
```

### 日志查询失败

```bash
# 验证日志目录挂载
docker exec sftlogapi ls /app/logs/sft-aipg/

# 检查配置文件
docker exec sftlogapi cat /app/config/log_dirs.json
```

---

## 📈 资源限制

### 推荐配置

```bash
docker run -d \
  --name sftlogapi \
  --cpus="2.0" \
  --memory="2g" \
  --memory-reservation="512m" \
  -p 8090:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  --restart unless-stopped \
  sftlogapi:v1.0.0
```

---

## ✅ 部署检查清单

- [ ] 镜像已加载 (`docker images | grep sftlogapi`)
- [ ] 日志目录已准备 (`ls -la /root/sft/testlogs`)
- [ ] 容器已启动 (`docker ps | grep sftlogapi`)
- [ ] 健康检查通过 (`curl .../api/ai/health`)
- [ ] 服务列表正常 (`curl .../api/ai/services`)
- [ ] 日志查询正常 (测试查询功能)
- [ ] 外部 Nginx 已配置（如需要）

---

## 📞 技术支持

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/xiegm900209/sftlogapi |
| **镜像版本** | v1.0.0 |
| **创建时间** | 2026-04-10 |
| **文档版本** | v1.1 |

---

**部署完成！🎉**
