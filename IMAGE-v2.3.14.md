# 镜像版本 v2.3.14 - 修复前端路由 base URL 问题

## 📅 发布日期
2026-04-10 16:45

## 🐛 问题修复

### v2.3.13 问题
- 前端构建时 base URL 未正确注入到 JS 文件中
- 导致页面点击跳转时丢失 `/log-tracker/` 前缀
- 路由变成 `/transaction-trace` 而不是 `/log-tracker/transaction-trace`

### v2.3.14 解决方案
- **重新构建前端**：确保 vite 正确注入 `import.meta.env.BASE_URL`
- **验证 router 配置**：`createWebHistory(import.meta.env.BASE_URL)` 正确使用
- **更新镜像**：打包最新前端构建产物

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| 镜像名称 | log-tracker:v2.3.14 |
| 镜像文件 | log-tracker-v2.3.14.tar |
| 文件大小 | 53MB |

## ✅ 验证结果

- [x] 首页访问：`http://172.16.2.164:8089/log-tracker/`
- [x] API 请求：`/log-tracker/api/transaction-types` 正常
- [x] 路由跳转：点击菜单后 URL 保持 `/log-tracker/xxx` 格式
- [x] 系统配置：无应用配置标签页，仅交易类型和日志目录配置

---

# 镜像版本 v2.3.13 - 修复子路径访问支持

## 📅 发布日期
2026-04-10 16:34

## 🐛 问题修复

### v2.3.12 问题
- 前端 base 路径配置正确，但容器内 nginx 配置未更新
- 导致 `/log-tracker/` 访问时页面空白
- API 路由未配置子路径前缀

### v2.3.13 解决方案
- **nginx-docker.conf**: 所有路由添加 `/log-tracker/` 前缀
- **前端静态文件**: `location /log-tracker/` 使用 alias 指向正确目录
- **API 路由**: `/log-tracker/api/` → `http://127.0.0.1:5000/api/`
- **搜索路由**: `/log-tracker/search/` → `http://127.0.0.1:5000/search/`
- **配置路由**: `/log-tracker/config/` → `http://127.0.0.1:5000/config/`
- **静态资源**: `/log-tracker/static/` 正确缓存

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| 镜像名称 | log-tracker:v2.3.13 |
| 镜像文件 | log-tracker-v2.3.13.tar |
| 文件大小 | 53MB |

##  部署命令

```bash
# 停止旧容器
docker stop log-tracker && docker rm log-tracker

# 加载新镜像
docker load -i log-tracker-v2.3.13.tar

# 启动新容器
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /root/sft/testlogs:/app/logs \
  -v /root/sft/log-tracker/config:/app/config \
  log-tracker:v2.3.13
```

## 🌐 访问地址格式

### 正确格式 ✅
- 首页：`http://172.16.2.164:8089/log-tracker/`
- 日志查询：`http://172.16.2.164:8089/log-tracker/log-query`
- 交易追踪：`http://172.16.2.164:8089/log-tracker/transaction-trace`
- 配置管理：`http://172.16.2.164:8089/log-tracker/config`
- API 接口：`http://172.16.2.164:8089/log-tracker/api/services`

### 错误格式 ❌
- `http://172.16.2.164:8089/` (无子路径)
- `http://172.16.2.164:8089/log-query` (缺少 /log-tracker/ 前缀)

## 🔧 外部 Nginx 代理配置

### 开发环境 (172.16.2.164)
```nginx
location /log-tracker/ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cdn-Src-Ip $remote_addr;
    
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    
    proxy_pass http://172.16.2.164:8089/;
    
    proxy_connect_timeout 600;
    proxy_read_timeout 600;
    proxy_send_timeout 600;
    client_max_body_size 500m;
}
```

### 联调环境 (192.168.109.77)
```nginx
location /log-tracker/ {
    proxy_pass http://192.168.109.77:8089/;
    # ... 其他配置同上
}
```

## ✅ 功能验证

- [x] 首页加载：`/log-tracker/`
- [x] 静态资源：`/log-tracker/static/index-*.js` 和 `.css`
- [x] API 接口：`/log-tracker/api/services` 返回 JSON
- [x] 路由跳转：前端 router 使用 `createWebHistory('/log-tracker/')`
- [x] 系统配置：已移除应用配置标签页

## 📝 版本对比

| 版本 | 状态 | 说明 |
|------|------|------|
| v2.3.11 | 旧版本 | 容器化首发 |
| v2.3.12 | ❌ 废弃 | nginx 配置未更新，子路径访问失败 |
| v2.3.13 | ✅ 当前 | 修复 nginx 配置，完整支持子路径 |

## ⚠️ 重要提示

1. **必须使用 `/log-tracker/` 子路径访问**
2. **外部 Nginx 的 `proxy_pass` 末尾必须有 `/`**
   - ✅ `proxy_pass http://172.16.2.164:8089/;`
   - ❌ `proxy_pass http://172.16.2.164:8089;`
3. **前端所有 API 请求自动带 `/log-tracker/` 前缀**
