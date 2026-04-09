# 交易日志链路追踪系统

<div align="center">

📊 **Log Tracker** - 帮助开发和运维团队快速定位分布式系统中的交易流转问题

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/xiegm900209/log-tracker)
[![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 项目简介

交易日志链路追踪系统（Log Tracker）是一个基于 Web 的日志分析工具，专为金融交易系统设计。通过 REQ_SN（交易序列号）或 TraceID 快速定位交易日志，可视化展示交易在各应用间的流转过程。

### 核心能力

- 🔍 **快速定位** - 通过 REQ_SN、商户号、日志时间组合查询
- 🔗 **链路追踪** - 自动提取 TraceID，展示完整交易链路
- 📊 **可视化展示** - 时序图形式展示交易流转过程
- ⚡ **高性能搜索** - 支持 GB 级日志文件，流式处理
- 🗜️ **压缩支持** - 直接读取 .gz 压缩文件，无需解压
- 🔤 **多编码支持** - GBK/UTF-8 自动检测，中文无乱码

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:xiegm900209/log-tracker.git
cd log-tracker
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 配置日志目录

编辑 `config/log_dirs.json`，配置各应用的日志目录路径：

```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
  "sft-pay": "/root/sft/testlogs/sft-pay"
}
```

### 5. 启动后端服务

```bash
cd backend
python app_main.py
```

服务将在 `http://localhost:5000` 上运行。

### 6. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

开发服务器将在 `http://localhost:3000` 上运行。

### 7. 生产环境部署

#### 构建前端

```bash
cd frontend
npm run build
```

#### 配置 Nginx

参考 `nginx.conf` 配置反向代理：

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📋 功能模块

### 1. 日志追踪查询

**路径**: `/log-query`

通过 REQ_SN、商户号、日志时间组合查询交易链路。

**主要特性**:
- ✅ REQ_SN 精准查询
- ✅ 商户号过滤
- ✅ 日志时间定位（YYYYMMDDHH 格式）
- ✅ 自动 TraceID 提取
- ✅ 多 TraceID 分组展示（重复查询场景）
- ✅ CSV 导出
- ✅ 多行日志解析（XML 报文）
- ✅ 多编码支持（GBK/UTF-8）

### 2. 交易类型日志追踪

**路径**: `/transaction-trace`

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

**路径**: `/transaction-types`

配置交易类型及其关联的应用模块。

- ✅ 新增/编辑/删除交易类型
- ✅ 配置交易代码和名称
- ✅ 关联多个应用
- ✅ 实时保存到配置文件

#### 3.2 应用日志配置

**路径**: `/app-log-config`

配置每个交易应用的日志目录路径。

- ✅ 新增/编辑/删除应用配置
- ✅ 路径验证功能
- ✅ 实时检测路径状态
- ✅ 支持 34+ 个应用配置

#### 3.3 系统配置

**路径**: `/config`

系统级配置管理。

- ✅ 应用基础配置
- ✅ 日志级别设置
- ✅ 搜索参数配置
- ✅ 性能参数调整

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

### 部署

- **Web 服务器**: Nginx / Tengine
- **反向代理**: Nginx
- **应用服务**: Flask Development Server / Gunicorn

---

## 📁 项目结构

```
log-tracker/
├── backend/                 # Flask 后端项目
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
│   └── log_dirs.json        # 日志目录配置
├── nginx.conf               # Nginx 配置示例
├── README.md                # 项目说明
└── LICENSE                  # 许可证
```

---

## 🔌 API 接口

### 查询接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/search` | GET | 根据 REQ_SN 搜索日志 |
| `/api/search-by-trace` | GET | 根据 TraceID 搜索日志 |
| `/api/trace` | GET | 追踪完整交易链路 |
| `/api/trace-summary` | GET | 获取交易链路摘要 |
| `/api/log-query` | GET | 综合日志查询 |
| `/api/transaction-trace` | GET | 交易类型日志追踪 |

### 配置接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/services` | GET | 获取可用服务列表 |
| `/api/transaction-types` | GET | 获取交易类型配置 |
| `/api/config/transaction-types` | POST | 更新交易类型配置 |
| `/api/config/log-dirs` | GET/POST | 获取/更新日志目录配置 |
| `/api/config/validate-path` | POST | 验证路径是否存在 |

---

## 📝 配置说明

### 交易类型配置

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

### 日志目录配置

```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
  "sft-pay": "/root/sft/testlogs/sft-pay"
}
```

---

## 🎯 使用示例

### 查询 REQ_SN

```bash
curl "http://localhost:5000/api/search?req_sn=20260408090000019466514799&service=sft-aipg"
```

### 追踪交易链路

```bash
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=20260408090000019466514799&log_time=2026040809"
```

### 获取服务列表

```bash
curl "http://localhost:5000/api/services"
```

---

## 📊 性能特性

- **流式处理**: 使用生成器逐块读取，避免内存溢出
- **索引机制**: 为 TraceID 建立索引，加速搜索
- **时间定位**: 根据日志文件名快速定位，减少扫描范围
- **压缩支持**: 直接读取 .gz 文件，节省 8 倍时间
- **多编码检测**: GBK/GB18030/UTF-8 自动识别

---

## 🛠️ 开发指南

### 添加新的日志解析规则

编辑 `backend/models/log_parser.py`，修改 `parse_log_block()` 函数。

### 添加新的 API 接口

在 `backend/app_main.py` 中添加路由处理函数。

### 添加新的页面

1. 在 `frontend/src/views/` 创建新组件
2. 在 `frontend/src/router/index.js` 添加路由
3. 在 `frontend/src/App.vue` 添加导航菜单

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
- **GitHub**: https://github.com/xiegm900209/log-tracker
- **Issues**: https://github.com/xiegm900209/log-tracker/issues

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

<div align="center">

**Made with ❤️ by Log Tracker Team**

[⬆ 返回顶部](#交易日志链路追踪系统)

</div>
