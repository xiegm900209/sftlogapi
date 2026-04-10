# sftlogapi Docker 部署指南

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| **镜像名称** | sftlogapi:v1.0.0 |
| **镜像文件** | sftlogapi-v1.0.0.tar |
| **镜像大小** | ~180MB |
| **基础镜像** | Python 3.9-slim + Node 18-alpine |
| **端口** | 80 (容器内) |

---

## 🚀 部署方式

### 方式 1: 使用镜像文件部署（推荐）

#### 1. 加载镜像

```bash
# 传输镜像文件到目标服务器
scp sftlogapi-v1.0.0.tar root@target-server:/root/

# 加载镜像
docker load -i sftlogapi-v1.0.0.tar
```

#### 2. 准备日志目录

```bash
# 确保日志目录存在
mkdir -p /root/sft/testlogs

# 设置只读权限（可选）
chmod -R 555 /root/sft/testlogs
```

#### 3. 启动容器

```bash
docker run -d \
  --name sftlogapi \
  -p 8090:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  --restart unless-stopped \
  sftlogapi:v1.0.0
```

#### 4. 验证部署

```bash
# 查看容器状态
docker ps | grep sftlogapi

# 查看日志
docker logs -f sftlogapi

# 测试健康检查
curl http://localhost:8090/sftlogapi/api/ai/health
```

---

### 方式 2: 使用 Docker Compose 部署

#### 1. 加载镜像

```bash
docker load -i sftlogapi-v1.0.0.tar
```

#### 2. 启动服务

```bash
cd /root/sft/sftlogapi
docker-compose up -d
```

#### 3. 查看状态

```bash
docker-compose ps
docker-compose logs -f
```

---

### 方式 3: 从 Dockerfile 构建

#### 1. 克隆项目

```bash
git clone git@github.com:xiegm900209/sftlogapi.git
cd sftlogapi
```

#### 2. 构建镜像

```bash
docker build -t sftlogapi:v1.0.0 .
```

#### 3. 启动容器

```bash
docker run -d \
  --name sftlogapi \
  -p 8090:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  sftlogapi:v1.0.0
```

---

## 🌐 访问地址

### 直接访问容器

```
http://localhost:8090/sftlogapi/
```

### 通过外部 Nginx 反向代理

#### Nginx 配置示例

```nginx
location /sftlogapi/ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cdn-Src-Ip $remote_addr;
    
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
# 启动容器
docker start sftlogapi

# 停止容器
docker stop sftlogapi

# 重启容器
docker restart sftlogapi

# 删除容器
docker rm -f sftlogapi
```

### 日志查看

```bash
# 查看实时日志
docker logs -f sftlogapi

# 查看最近 100 行
docker logs --tail 100 sftlogapi

# 查看特定时间日志
docker logs --since 2026-04-10T10:00:00 sftlogapi
```

### 进入容器

```bash
# 进入容器 shell
docker exec -it sftlogapi /bin/bash

# 查看容器内文件
docker exec -it sftlogapi ls -la /app

# 测试 API
docker exec -it sftlogapi curl http://localhost/api/ai/health
```

---

## 📊 资源限制

### Docker Compose 配置

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Docker Run 命令

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

## 🔐 安全建议

### 1. 日志目录只读挂载

```bash
-v /root/sft/testlogs:/app/logs:ro
```

### 2. 限制容器权限

```bash
--read-only
--tmpfs /tmp
--cap-drop=ALL
--cap-add=NET_BIND_SERVICE
```

### 3. 使用非 root 用户

修改 Dockerfile:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 4. 定期更新镜像

```bash
# 拉取最新镜像
docker pull sftlogapi:v1.0.0

# 重启容器
docker rm -f sftlogapi
docker run ... (同上)
```

---

## 🧪 健康检查

### 手动检查

```bash
# 健康检查接口
curl http://localhost:8090/sftlogapi/api/ai/health

# 预期响应
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-04-10T10:00:00Z",
  "api_version": "v1"
}
```

### Docker 健康状态

```bash
docker inspect --format='{{.State.Health.Status}}' sftlogapi
```

---

## 📝 配置文件说明

### 日志目录配置

文件：`/app/config/log_dirs.json`

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry"
}
```

### 交易类型配置

文件：`/app/config/transaction_types.json`

```json
{
  "310011": {
    "name": "协议支付",
    "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
  }
}
```

### API Key 配置

文件：`/app/config/api_keys.json`

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

## 🔧 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs sftlogapi

# 检查端口占用
netstat -tlnp | grep 8090

# 检查配置文件
docker exec sftlogapi cat /app/config/log_dirs.json
```

### API 无法访问

```bash
# 测试容器内 Flask
docker exec sftlogapi curl http://127.0.0.1:5000/api/ai/health

# 测试容器内 Nginx
docker exec sftlogapi curl http://localhost/api/ai/health

# 检查 Nginx 配置
docker exec sftlogapi cat /etc/nginx/conf.d/default.conf
```

### 日志查询失败

```bash
# 检查日志目录挂载
docker exec sftlogapi ls -la /app/logs

# 检查日志目录配置
docker exec sftlogapi cat /app/config/log_dirs.json

# 检查日志文件
docker exec sftlogapi ls /app/logs/sft-aipg/
```

---

## 📈 性能优化

### 1. 使用 volumes 而非 bind mounts

```yaml
volumes:
  - logs-data:/app/logs

volumes:
  logs-data:
```

### 2. 启用 Nginx 缓存

```nginx
location /sftlogapi/static/ {
    alias /var/www/sftlogapi/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 调整 Flask worker 数量

```bash
# 修改 docker-entrypoint.sh
gunicorn -w 4 -b 0.0.0.0:5000 app_main:app
```

---

## 📞 技术支持

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/xiegm900209/sftlogapi |
| **镜像版本** | v1.0.0 |
| **创建时间** | 2026-04-10 |
| **文档版本** | v1.0 |

---

## ✅ 部署检查清单

- [ ] 镜像已加载 (`docker images | grep sftlogapi`)
- [ ] 日志目录已准备 (`ls -la /root/sft/testlogs`)
- [ ] 容器已启动 (`docker ps | grep sftlogapi`)
- [ ] 健康检查通过 (`curl http://localhost:8090/sftlogapi/api/ai/health`)
- [ ] 日志可查询 (访问前端测试查询功能)
- [ ] 外部 Nginx 已配置（如需要）
- [ ] 监控告警已配置（如需要）

---

**部署完成！🎉**
