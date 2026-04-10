# sftlogapi Flask 纯应用镜像部署说明

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| **镜像文件** | `sftlogapi-flask-v1.0.0.tar` |
| **镜像大小** | 50MB |
| **镜像名称** | `sftlogapi-flask:v1.0.0` |
| **基础镜像** | Python 3.9-slim |
| **端口** | 5000 (Flask) |

---

## 🚀 部署步骤

### 1️⃣ 加载镜像

```bash
docker load -i sftlogapi-flask-v1.0.0.tar
```

### 2️⃣ 启动 Flask 容器

```bash
docker run -d \
  --name sftlogapi \
  -p 5000:5000 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  --restart unless-stopped \
  sftlogapi-flask:v1.0.0
```

### 3️⃣ 配置 Tengine 反向代理

配置文件：`/usr/local/tengine/conf/conf.d/sftlogapi.conf`

```nginx
server {
    listen       8090;
    server_name  172.16.2.164;

    # 前端静态文件
    location /sftlogapi/ {
        root /var/www;
        index index.html;
        try_files $uri $uri/ /sftlogapi/index.html;
    }

    # API 代理到 Flask 容器
    location /sftlogapi/api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* /sftlogapi/static/ {
        root /var/www;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4️⃣ 部署前端静态文件

```bash
mkdir -p /var/www/sftlogapi
cp -r /root/sft/sftlogapi/frontend/dist/* /var/www/sftlogapi/
```

### 5️⃣ 重启 Tengine

```bash
/usr/local/tengine/sbin/nginx -t
/usr/local/tengine/sbin/nginx -s reload
```

---

## 🌐 访问地址

| 功能 | 地址 |
|------|------|
| **前端页面** | `http://172.16.2.164:8090/sftlogapi/` |
| **AI API** | `http://172.16.2.164:8090/sftlogapi/api/ai/` |
| **Flask 直接访问** | `http://127.0.0.1:5000/` |

---

## 📊 架构优势

```
用户请求
    ↓
Tengine (宿主机 8090)
    ↓
Docker 容器 (Flask 5000)
    ↓
日志文件 (/root/sft/testlogs)
```

**优势**:
- ✅ 镜像更小（50MB vs 180MB）
- ✅ 复用宿主机 Tengine
- ✅ 统一 SSL 管理
- ✅ 更好的性能
- ✅ 更简单的运维

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

# 查看日志
docker logs -f sftlogapi

# 进入容器
docker exec -it sftlogapi /bin/bash
```

### 健康检查

```bash
# Flask 直接检查
curl http://127.0.0.1:5000/api/ai/health

# 通过 Tengine 检查
curl http://172.16.2.164:8090/sftlogapi/api/ai/health
```

---

## 📝 配置文件

### 日志目录配置

文件：`config/log_dirs.json`

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry"
}
```

### API Key 配置

文件：`config/api_keys.json`

```json
{
  "api_keys": {
    "zhiduoxing-prod": {
      "name": "智多星生产环境",
      "rate_limit": 100
    }
  }
}
```

---

## ✅ 验证清单

- [ ] 容器已启动 (`docker ps`)
- [ ] Flask 健康检查通过 (`curl :5000/api/ai/health`)
- [ ] Tengine 配置正确 (`nginx -t`)
- [ ] Tengine 已重载 (`nginx -s reload`)
- [ ] 前端页面可访问 (`curl :8090/sftlogapi/`)
- [ ] API 查询正常

---

**部署完成！🎉**
