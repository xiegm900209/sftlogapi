# Tengine 反向代理配置指南

## 📋 架构说明

```
用户请求
    ↓
Tengine (宿主机 8090 端口)
    ↓
Docker 容器 (Flask 5000 端口)
    ↓
日志文件 (/root/sft/testlogs)
```

---

## 🔧 Tengine 配置

### 配置文件位置

`/usr/local/tengine/conf/conf.d/sftlogapi.conf`

### 配置内容

```nginx
# sftlogapi 交易日志链路追踪系统配置
# 端口：8090 (HTTP)
# 子路径：/sftlogapi/
# 后端：Docker Flask 容器 (127.0.0.1:5000)

server {
    listen       8090;
    server_name  172.16.2.164;

    # 前端静态文件 - 支持 /sftlogapi/ 子路径
    location /sftlogapi/ {
        root /var/www;
        index index.html;
        try_files $uri $uri/ /sftlogapi/index.html;
    }

    # API 路由 - 后端 Flask 应用
    location /sftlogapi/api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';

        # 增加超时时间，处理大文件搜索
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 搜索路由
    location /sftlogapi/search/ {
        proxy_pass http://127.0.0.1:5000/search/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';

        # 增加超时时间，处理大文件搜索
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 配置路由
    location /sftlogapi/config/ {
        proxy_pass http://127.0.0.1:5000/config/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
    }

    # 静态资源缓存 (JS/CSS/图片等)
    location ~* /sftlogapi/static/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 🚀 部署步骤

### 1. 启动 Flask 容器

```bash
# 加载镜像
docker load -i sftlogapi-v1.0.0.tar

# 启动容器（仅 Flask）
docker run -d \
  --name sftlogapi \
  -p 5000:5000 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  --restart unless-stopped \
  sftlogapi:v1.0.0
```

### 2. 部署前端静态文件

```bash
# 复制前端文件到 Tengine 目录
mkdir -p /var/www/sftlogapi
cp -r /root/sft/sftlogapi/frontend/dist/* /var/www/sftlogapi/
```

### 3. 配置 Tengine

```bash
# 创建配置文件
cat > /usr/local/tengine/conf/conf.d/sftlogapi.conf << 'EOF'
server {
    listen       8090;
    server_name  172.16.2.164;

    location /sftlogapi/ {
        root /var/www;
        index index.html;
        try_files $uri $uri/ /sftlogapi/index.html;
    }

    location /sftlogapi/api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 测试配置
/usr/local/tengine/sbin/nginx -t

# 重载配置
/usr/local/tengine/sbin/nginx -s reload
```

### 4. 验证部署

```bash
# 检查容器状态
docker ps | grep sftlogapi

# 测试 Flask 健康检查
curl http://127.0.0.1:5000/api/ai/health

# 测试 Tengine 代理
curl http://172.16.2.164:8090/sftlogapi/api/ai/health
```

---

## 📊 优势对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **纯 Flask 容器 + Tengine** | ✅ 镜像更小 (~150MB)<br>✅ 复用宿主机 Tengine<br>✅ 统一 SSL 管理<br>✅ 更好的性能 | ⚠️ 需要配置 Tengine |
| **Flask+Nginx 容器** | ✅ 开箱即用<br>✅ 完全隔离 | ❌ 镜像较大 (~180MB)<br>❌ 端口冲突风险<br>❌ SSL 配置复杂 |

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

### Tengine 管理

```bash
# 测试配置
/usr/local/tengine/sbin/nginx -t

# 重载配置
/usr/local/tengine/sbin/nginx -s reload

# 停止
/usr/local/tengine/sbin/nginx -s stop

# 启动
/usr/local/tengine/sbin/nginx
```

---

## 🌐 访问地址

| 功能 | 地址 |
|------|------|
| **前端页面** | `http://172.16.2.164:8090/sftlogapi/` |
| **AI API** | `http://172.16.2.164:8090/sftlogapi/api/ai/` |
| **健康检查** | `http://172.16.2.164:8090/sftlogapi/api/ai/health` |
| **Flask 直接访问** | `http://127.0.0.1:5000/` |

---

## 📝 配置文件说明

### 前端静态文件位置

```
/var/www/sftlogapi/
├── index.html
└── static/
    ├── index-*.js
    └── index-*.css
```

### 日志目录挂载

```bash
# 宿主机
/root/sft/testlogs/

# 容器内
/app/logs/
```

### 配置文件挂载

```bash
# 宿主机
/root/sft/sftlogapi/config/

# 容器内
/app/config/
```

---

## ✅ 部署检查清单

- [ ] Flask 容器已启动 (`docker ps`)
- [ ] 前端文件已复制 (`ls /var/www/sftlogapi/`)
- [ ] Tengine 配置已创建 (`cat /usr/local/tengine/conf/conf.d/sftlogapi.conf`)
- [ ] Tengine 配置测试通过 (`nginx -t`)
- [ ] Tengine 已重载 (`nginx -s reload`)
- [ ] 健康检查通过 (`curl .../api/ai/health`)
- [ ] 前端页面可访问 (`curl .../sftlogapi/`)

---

**部署完成！🎉**
