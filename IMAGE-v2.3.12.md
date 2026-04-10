# 镜像版本 v2.3.12 - 系统配置优化 + 子路径访问支持

## 📅 发布日期
2026-04-10

## 🎯 主要修改

### 1. 前端配置优化
- **vite.config.js**: `base: '/log-tracker/'` 已正确配置
- 支持子路径访问：`http://172.16.2.164:8089/log-tracker/`

### 2. 系统配置页面精简
- **移除**: 应用配置标签页（原 `activeTab: 'app'`）
- **保留**: 交易类型配置、日志目录配置
- **Config.vue**: 删除 appConfig 相关数据和方法

### 3. 前端重新构建
- 使用正确的 base 路径 `/log-tracker/`
- 构建产物已打包到镜像中

## 📦 镜像信息

| 项目 | 值 |
|------|-----|
| 镜像名称 | log-tracker:v2.3.12 |
| 镜像文件 | log-tracker-v2.3.12.tar |
| 文件大小 | 53MB |
| 基础镜像 | python:3.9-slim + node:18-alpine |

## 🚀 部署方式

### 方式一：直接运行
```bash
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /path/to/logs:/app/logs \
  log-tracker:v2.3.12
```

### 方式二：使用 docker-compose
```bash
docker-compose up -d
```

## 🌐 访问地址

### 开发环境 (172.16.2.164)
- 内网：http://172.16.2.164:8089/log-tracker/

### 联调环境 (192.168.109.77)
- 内网：http://192.168.109.77:8089/log-tracker/
- 公网：https://sft-test.allinpay.com/log-tracker/

## 🔧 Nginx 代理配置

```nginx
location /log-tracker/ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Cdn-Src-Ip $remote_addr;
    
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    
    proxy_pass http://172.16.2.164:8089/;  # 开发环境
    # proxy_pass http://192.168.109.77:8089/;  # 联调环境
    
    proxy_connect_timeout 600;
    proxy_read_timeout 600;
    proxy_send_timeout 600;
    client_max_body_size 500m;
}
```

## ✅ 功能验证

- [ ] 首页加载正常
- [ ] 日志追踪查询正常
- [ ] 交易类型追踪正常
- [ ] 配置管理页面正常（无应用配置标签页）
- [ ] 交易类型管理正常
- [ ] 应用日志配置正常
- [ ] 系统配置正常（仅交易类型配置 + 日志目录配置）
- [ ] 静态资源加载正常（带 /log-tracker/ 前缀）

## 📝 变更对比

| 版本 | 主要变更 |
|------|---------|
| v2.3.11 | Docker 容器化首发，配置路径修复 |
| v2.3.12 | 系统配置精简，移除应用配置标签页 |

## ⚠️ 注意事项

1. 前端已配置 base 路径为 `/log-tracker/`，必须通过子路径访问
2. 外部 Nginx 需配置正确的 `proxy_pass` 目标地址
3. 系统配置页面不再包含应用配置，仅保留交易类型配置和日志目录配置
