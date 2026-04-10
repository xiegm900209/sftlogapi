# sftlogapi - 交易日志链路追踪系统

<div align="center">

📊 **Log Tracker** - 帮助开发和运维团队快速定位分布式系统中的交易流转问题

[![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)](https://github.com/xiegm900209/sftlogapi)
[![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 项目简介

交易日志链路追踪系统（sftlogapi）是一个基于 Web 的日志分析工具，专为金融交易系统设计。通过 REQ_SN（交易序列号）或 TraceID 快速定位交易日志，可视化展示交易在各应用间的流转过程。

### 核心能力

- 🔍 **快速定位** - 通过 REQ_SN、商户号、日志时间组合查询
- 🔗 **链路追踪** - 自动提取 TraceID，展示完整交易链路
- 📊 **可视化展示** - 时序图形式展示交易流转过程
- ⚡ **高性能搜索** - 支持 GB 级日志文件，流式处理
- 🗜️ **压缩支持** - 直接读取 .gz 压缩文件，无需解压
- 🔤 **多编码支持** - GBK/UTF-8 自动检测，中文无乱码
- 🤖 **AI API** - 为智多星等 AI 系统提供自然语言查询接口

---

## 🏗️ 技术架构

### 前端

- **框架**: Vue 3.x
- **构建工具**: Vite 5.x
- **UI 库**: Element Plus
- **图表**: ECharts 5.x
- **HTTP 客户端**: Axios

### 后端

- **框架**: Flask 2.3
- **语言**: Python 3.9
- **日志解析**: 自研日志解析引擎
- **索引机制**: TraceID 索引加速

### 部署架构

```
用户请求
    ↓
Nginx/Tengine (前端静态文件 + 反向代理)
    ↓
Docker 容器 (Flask API)
    ↓
日志文件 (/app/logs)
```

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 准备环境

```bash
# 应用服务器
mkdir -p /app/sharenfs/sft-logs
mkdir -p /app/sftlogapi-config

# Nginx 服务器
mkdir -p /var/www/sftlogapi
```

#### 2. 加载镜像

```bash
docker load -i sftlogapi-flask-v1.0.3.tar
```

#### 3. 启动容器

```bash
docker run -d \
  --name sftlogapi \
  -p 5000:5000 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  -v /app/sftlogapi-config:/app/config \
  --restart unless-stopped \
  sftlogapi-flask:v1.0.3
```

#### 4. 配置 Nginx

```nginx
upstream sftlogapi_backend {
    server 192.168.109.77:5000;
}

server {
    listen 80;

    location /sftlogapi/ {
        root /var/www;
        index index.html;
        try_files $uri $uri/ /sftlogapi/index.html;
    }

    location /sftlogapi/api/ {
        proxy_pass http://sftlogapi_backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### 5. 验证部署

```bash
curl http://localhost:5000/api/ai/health
curl http://nginx-server/sftlogapi/
```

---

### 方式二：本地开发

#### 1. 克隆项目

```bash
git clone git@github.com:xiegm900209/sftlogapi.git
cd sftlogapi
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 配置日志目录

编辑 `config/log_dirs.json`：

```json
{
  "sft-aipg": "/path/to/your/logs/sft-aipg",
  "sft-trxqry": "/path/to/your/logs/sft-trxqry"
}
```

#### 5. 启动后端

```bash
cd backend
python app_main.py
```

#### 6. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

---

## 📊 功能模块

### 1. 日志追踪查询

**路径**: `/sftlogapi/log-query`

通过 REQ_SN、商户号、日志时间组合查询交易链路。

**主要特性**:
- ✅ REQ_SN 精准查询
- ✅ 商户号过滤
- ✅ 日志时间定位（YYYYMMDDHH 格式）
- ✅ 自动 TraceID 提取
- ✅ 多 TraceID 分组展示
- ✅ CSV 导出
- ✅ 多行日志解析（XML 报文）
- ✅ 多编码支持（GBK/UTF-8）

### 2. 交易类型日志追踪

**路径**: `/sftlogapi/transaction-trace`

根据交易类型配置的关联应用，依次展示完整交易链路。

**主要特性**:
- ✅ 交易类型选择（自动加载应用列表）
- ✅ 入口应用提取 TraceID
- ✅ 全链路追踪（所有关联应用）
- ✅ 可视化链路图（步骤条展示）
- ✅ 按应用分组查看
- ✅ 多 TraceID 支持（折叠面板）
- ✅ 压缩文件支持（.gz）
- ✅ 时间范围扩展（前后 1 小时）

### 3. 配置管理

#### 3.1 交易类型管理

**路径**: `/sftlogapi/transaction-types`

配置交易类型及其关联的应用模块。

- ✅ 新增/编辑/删除交易类型
- ✅ 配置交易代码和名称
- ✅ 关联多个应用
- ✅ 实时保存到配置文件

#### 3.2 应用日志配置

**路径**: `/sftlogapi/app-log-config`

配置每个交易应用的日志目录路径。

- ✅ 新增/编辑/删除应用配置
- ✅ 路径验证功能
- ✅ 实时检测路径状态
- ✅ 支持 34+ 个应用配置

---

## 🤖 AI API 接口

### 接口列表

| 接口 | 方法 | 鉴权 | 说明 |
|------|------|------|------|
| `/api/ai/health` | GET | ❌ | 健康检查 |
| `/api/ai/query` | POST | ✅ | 统一查询接口 |
| `/api/ai/transaction-types` | GET | ✅ | 获取交易类型 |
| `/api/ai/services` | GET | ✅ | 获取服务列表 |

### API Key 鉴权

**请求头**:
```http
Authorization: Bearer zhiduoxing-prod
```

**或查询参数**:
```
?api_key=zhiduoxing-prod
```

### 查询示例

```bash
curl -X POST "http://localhost:5000/api/ai/query" \
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

**响应**:
```json
{
  "success": true,
  "data": {
    "transaction_type": "310011",
    "transaction_name": "协议支付",
    "trace_id": "TCEsVt60",
    "total_logs": 93,
    "services": ["sft-aipg", "sft-trxcharge", "sft-merapi"],
    "logs": [...],
    "summary": {
      "status": "success",
      "start_time": "2026-04-08 09:00:25",
      "end_time": "2026-04-08 09:00:26"
    }
  }
}
```

---

## 📁 项目结构

```
sftlogapi/
├── backend/                 # Flask 后端项目
│   ├── ai_api/              # AI API 模块
│   │   ├── __init__.py
│   │   ├── auth.py          # API Key 鉴权
│   │   ├── query_handler.py # 查询处理器
│   │   └── response_formatter.py
│   ├── app_main.py          # 应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # 数据模型
│   │   ├── log_parser.py    # 日志解析器
│   │   ├── indexer.py       # 索引构建器
│   │   └── trace_analyzer.py # 链路追踪分析器
│   └── requirements.txt     # Python 依赖
├── frontend/                # Vue.js 前端项目
│   ├── src/
│   │   ├── views/           # 页面视图
│   │   ├── components/      # 通用组件
│   │   ├── router/          # 路由配置
│   │   └── App.vue          # 根组件
│   ├── package.json         # 依赖配置
│   └── vite.config.js       # Vite 配置
├── config/                  # 配置文件
│   ├── app_config.json      # 应用配置
│   ├── transaction_types.json # 交易类型配置
│   ├── log_dirs.json        # 日志目录配置
│   └── api_keys.json        # API Key 配置
├── Dockerfile               # Docker 构建文件
├── docker-compose.yml       # Docker Compose 配置
├── README.md                # 项目说明
└── LICENSE                  # 许可证
```

---

## 🔐 配置说明

### 日志目录配置

文件：`config/log_dirs.json`

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry",
  "sft-pay": "/app/logs/sft-pay"
}
```

### 交易类型配置

文件：`config/transaction_types.json`

```json
{
  "310011": {
    "name": "协议支付",
    "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
  },
  "310016": {
    "name": "批量协议支付",
    "apps": ["sft-aipg", "sft-trxqry", "sft-batchpay"]
  }
}
```

### API Key 配置

文件：`config/api_keys.json`

```json
{
  "api_keys": {
    "zhiduoxing-prod": {
      "name": "智多星生产环境",
      "enabled": true,
      "rate_limit": 100
    },
    "zhiduoxing-test": {
      "name": "智多星测试环境",
      "enabled": true,
      "rate_limit": 20
    }
  }
}
```

---

## 🧪 测试

### API 测试

```bash
# 健康检查
curl http://localhost:5000/api/ai/health

# 获取服务列表
curl -H "Authorization: Bearer zhiduoxing-prod" http://localhost:5000/api/ai/services

# 获取交易类型
curl -H "Authorization: Bearer zhiduoxing-prod" http://localhost:5000/api/ai/transaction-types

# 查询交易日志
curl -X POST "http://localhost:5000/api/ai/query" \
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

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

- **作者**: xiegm900209
- **GitHub**: https://github.com/xiegm900209/sftlogapi
- **Issues**: https://github.com/xiegm900209/sftlogapi/issues

---

<div align="center">

**Made with ❤️ by sftlogapi Team**

[⬆ 返回顶部](#sftlogapi---交易日志链路追踪系统)

</div>
