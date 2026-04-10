# sftlogapi 部署指南

## 📦 部署架构

```
用户请求
    ↓
Nginx/Tengine (192.168.109.54:80)
    ├─ 前端静态文件：/var/www/sftlogapi/
    └─ API 反向代理
              ↓
         Docker 容器 (192.168.109.77:5000)
              ├─ Flask API
              ├─ 日志目录：/app/logs (挂载)
              └─ 配置目录：/app/config (挂载)
```

---

## 🚀 快速部署

### 环境要求

- **应用服务器**: 192.168.109.77 (运行 Docker 容器)
- **Nginx 服务器**: 192.168.109.54 (反向代理 + 前端静态文件)
- **Docker**: 20.10+
- **Python**: 3.9+
- **Node.js**: 18+ (仅开发需要)

---

### 步骤一：应用服务器部署 (192.168.109.77)

#### 1. 准备目录

```bash
# 创建日志目录
mkdir -p /app/sharenfs/sft-logs
chmod 555 /app/sharenfs/sft-logs

# 创建配置目录
mkdir -p /app/sftlogapi-config
```

#### 2. 加载镜像

```bash
docker load -i sftlogapi-flask-v1.0.3.tar
```

#### 3. 复制配置文件

```bash
# 从部署包复制配置文件
cp /mnt/usb/config/*.json /app/sftlogapi-config/

# 验证配置
ls -la /app/sftlogapi-config/
# 应包含：
# - log_dirs.json (34 个应用)
# - transaction_types.json (12 个交易类型)
# - api_keys.json (API Key 配置)
```

#### 4. 启动容器

```bash
docker run -d \
  --name sftlogapi \
  -p 5000:5000 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  -v /app/sftlogapi-config:/app/config \
  --restart unless-stopped \
  sftlogapi-flask:v1.0.3
```

#### 5. 验证部署

```bash
# 查看容器状态
docker ps | grep sftlogapi

# 测试健康检查
curl http://127.0.0.1:5000/api/ai/health

# 测试 API（需要 API Key）
curl -H "Authorization: Bearer zhiduoxing-prod" http://127.0.0.1:5000/api/ai/services
```

---

### 步骤二：Nginx 服务器部署 (192.168.109.54)

#### 1. 部署前端静态文件

```bash
# 创建目录
mkdir -p /var/www/sftlogapi

# 解压前端文件
tar -xzvf sftlogapi-frontend.tar.gz -C /var/www/sftlogapi/

# 验证文件
ls -la /var/www/sftlogapi/
# 应包含：
# - index.html
# - static/
```

#### 2. 配置 Nginx

创建配置文件 `/etc/nginx/conf.d/sftlogapi.conf`：

```nginx
upstream sftlogapi_backend {
    server 192.168.109.77:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location /sftlogapi/ {
        root /var/www;
        index index.html;
        try_files $uri $uri/ /sftlogapi/index.html;
    }

    # API 反向代理
    location /sftlogapi/api/ {
        proxy_pass http://sftlogapi_backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态资源缓存
    location ~* /sftlogapi/static/ {
        root /var/www;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 3. 测试并重载

```bash
# 测试配置
nginx -t

# 重载配置
nginx -s reload

# 验证服务状态
systemctl status nginx
```

#### 4. 验证部署

```bash
# 测试前端页面
curl http://192.168.109.54/sftlogapi/

# 测试 API
curl http://192.168.109.54/sftlogapi/api/ai/health

# 测试 API（带鉴权）
curl -H "Authorization: Bearer zhiduoxing-prod" \
     http://192.168.109.54/sftlogapi/api/ai/services
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

# 查看容器状态
docker ps | grep sftlogapi

# 查看容器日志
docker logs -f sftlogapi

# 进入容器
docker exec -it sftlogapi /bin/bash

# 删除容器
docker rm -f sftlogapi
```

### Nginx 管理

```bash
# 测试配置
nginx -t

# 重载配置
nginx -s reload

# 重启服务
systemctl restart nginx

# 查看状态
systemctl status nginx

# 查看日志
tail -f /var/log/nginx/error.log
```

---

## 📊 验证清单

### 应用服务器

- [ ] 镜像已加载 (`docker images | grep sftlogapi`)
- [ ] 容器已启动 (`docker ps | grep sftlogapi`)
- [ ] 健康检查通过 (`curl :5000/api/ai/health`)
- [ ] API Key 配置正确 (`curl -H "Authorization: Bearer zhiduoxing-prod" :5000/api/ai/services`)
- [ ] 日志目录已挂载 (`docker exec sftlogapi ls /app/logs`)
- [ ] 配置文件已挂载 (`docker exec sftlogapi cat /app/config/log_dirs.json`)

### Nginx 服务器

- [ ] 前端文件已部署 (`ls /var/www/sftlogapi/`)
- [ ] Nginx 配置已创建 (`cat /etc/nginx/conf.d/sftlogapi.conf`)
- [ ] 配置测试通过 (`nginx -t`)
- [ ] Nginx 已重载 (`nginx -s reload`)
- [ ] 前端页面可访问 (`curl :80/sftlogapi/`)
- [ ] API 代理正常 (`curl :80/sftlogapi/api/ai/health`)

---

## 🔐 安全建议

### 1. 防火墙配置

```bash
# 应用服务器 - 仅允许 Nginx 服务器访问
iptables -A INPUT -p tcp --dport 5000 -s 192.168.109.54 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### 2. 日志目录权限

```bash
# 设置只读权限
chmod 555 /app/sharenfs/sft-logs
chown root:root /app/sharenfs/sft-logs
```

### 3. Docker 安全选项

```bash
docker run -d \
  --name sftlogapi \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  -p 5000:5000 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  -v /app/sftlogapi-config:/app/config \
  --restart unless-stopped \
  sftlogapi-flask:v1.0.3
```

---

## 🔍 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs sftlogapi

# 检查配置文件
docker exec sftlogapi cat /app/config/log_dirs.json

# 检查日志目录
docker exec sftlogapi ls -la /app/logs
```

### Nginx 返回 502

```bash
# 检查后端连接
curl http://192.168.109.77:5000/api/ai/health

# 检查网络连通性
ping 192.168.109.77
telnet 192.168.109.77 5000

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### API 返回 401

```bash
# 检查 API Key 配置
docker exec sftlogapi cat /app/config/api_keys.json

# 测试带 API Key 的请求
curl -H "Authorization: Bearer zhiduoxing-prod" http://127.0.0.1:5000/api/ai/services
```

---

## 📞 技术支持

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/xiegm900209/sftlogapi |
| **镜像版本** | v1.0.3 |
| **创建时间** | 2026-04-10 |
| **文档版本** | v1.0 |

---

**部署完成！🎉**
