# Log Tracker 部署文档

## 部署完成 ✅

**部署时间**: 2026-04-09  
**访问地址**: http://172.16.2.164:8083

## 架构说明

```
┌─────────────────┐
│   用户浏览器     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Nginx (8083)   │  ← 静态文件 + 反向代理
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐  ┌──────────┐
│ Vue   │  │  Flask   │
│ 前端  │  │  后端    │
│(静态) │  │ (5000)   │
└───────┘  └────┬─────┘
               │
               ▼
        ┌──────────────┐
        │  /root/sft/  │
        │   testlogs   │
        └──────────────┘
```

## 组件状态

| 组件 | 状态 | 端口 | 说明 |
|------|------|------|------|
| Nginx | ✅ 运行中 | 8083 | Tengine，静态文件 + 反向代理 |
| Flask | ✅ 运行中 | 5000 | Python 后端 API |
| Vue | ✅ 已构建 | - | Vite 构建，dist 目录 |

## 目录结构

```
/root/sft/log-tracker/
├── backend/              # Flask 后端
│   ├── app_main.py      # 主应用入口
│   ├── models/          # 数据模型
│   └── routes/          # API 路由
├── frontend/            # Vue 前端
│   ├── dist/           # 构建输出 (已部署到 /var/www/log-tracker)
│   ├── src/            # 源代码
│   ├── index.html      # Vite 入口
│   ├── vite.config.js  # Vite 配置
│   └── package.json    # 依赖配置
├── config/             # 配置文件
│   ├── app_config.json
│   ├── log_dirs.json
│   └── transaction_types.json
└── DEPLOYMENT.md       # 本文档
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/services` | GET | 获取可用服务列表 |
| `/api/transaction-types` | GET | 获取交易类型配置 |
| `/api/search` | GET | 按 REQ_SN 搜索日志 |
| `/api/trace` | GET | 追踪交易链路 |
| `/api/trace-summary` | GET | 获取交易链路摘要 |
| `/api/search-by-trace` | GET | 按 TraceID 搜索 |

## 使用示例

```bash
# 获取服务列表
curl http://172.16.2.164:8083/api/services

# 获取交易类型
curl http://172.16.2.164:8083/api/transaction-types

# 搜索 REQ_SN
curl "http://172.16.2.164:8083/api/search?req_sn=12345&service=sft-aipg"

# 按 TraceID 搜索
curl "http://172.16.2.164:8083/api/search-by-trace?trace_id=abc123"
```

## 维护命令

### 重启后端
```bash
# 停止现有进程
pkill -f "python3 app_main.py"

# 启动新进程
cd /root/sft/log-tracker/backend
nohup python3 app_main.py > /tmp/log-tracker.log 2>&1 &
```

### 重新构建前端
```bash
cd /root/sft/log-tracker/frontend
npm run build
cp -r dist/* /var/www/log-tracker/
```

### 重载 Nginx 配置
```bash
/usr/local/tengine/sbin/nginx -t
/usr/local/tengine/sbin/nginx -s reload
```

## 日志文件

- **Flask 日志**: `/tmp/log-tracker.log`
- **Nginx 访问日志**: `/usr/local/tengine/logs/access.log`
- **Nginx 错误日志**: `/usr/local/tengine/logs/error.log`

## 注意事项

1. **权限**: 前端文件已复制到 `/var/www/log-tracker/` 以避免 nginx worker 用户 (nobody) 访问 `/root/` 目录的权限问题
2. **路径配置**: 所有日志路径已更新为绝对路径 `/root/sft/testlogs`
3. **构建工具**: 已从 Vue CLI 迁移到 Vite，构建速度更快，兼容性更好
4. **开发模式**: 如需本地开发，可在 frontend 目录运行 `npm run dev`，Vite 开发服务器将运行在 3000 端口并代理 API 请求
