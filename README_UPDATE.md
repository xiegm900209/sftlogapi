# 交易日志链路追踪系统 - 功能更新

## ✅ 已完成的功能

### 1. 日志追踪查询页面 (`/log-query`)

**功能**: 支持多条件组合查询日志
- ✅ REQ_SN 查询
- ✅ 商户号查询
- ✅ 交易时间范围查询
- ✅ 服务选择
- ✅ 结果导出 CSV

**访问**: http://172.16.2.164:8083/log-query

---

### 2. 交易类型管理页面 (`/transaction-types`)

**功能**: 可视化配置交易类型
- ✅ 新增交易类型
- ✅ 编辑交易类型
- ✅ 删除交易类型
- ✅ 关联应用多选
- ✅ 实时保存到配置文件

**访问**: http://172.16.2.164:8083/transaction-types

---

### 3. 应用日志目录配置页面 (`/app-log-config`)

**功能**: 配置每个应用的日志目录
- ✅ 新增应用配置
- ✅ 编辑应用配置
- ✅ 删除应用配置
- ✅ 路径验证功能
- ✅ 实时检测路径状态

**访问**: http://172.16.2.164:8083/app-log-config

---

## 📁 新增文件

### 前端
```
frontend/src/views/
├── LogQuery.vue              # 日志追踪查询页面
├── TransactionTypeManage.vue # 交易类型管理页面
└── AppLogConfig.vue          # 应用日志配置页面
```

### 后端
```
backend/app_main.py           # 已更新，新增 4 个 API 接口
```

### 文档
```
NEW_FEATURES.md               # 详细功能说明
README_UPDATE.md              # 本文档
```

---

## 🔌 新增 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/log-query` | GET | 综合日志查询 |
| `/api/config/transaction-types` | POST | 更新交易类型 |
| `/api/config/log-dirs` | GET/POST | 获取/更新日志目录 |
| `/api/config/validate-path` | POST | 验证路径 |

---

## 🎯 使用指南

### 查询日志
1. 访问 http://172.16.2.164:8083/log-query
2. 输入查询条件（至少一个）
3. 点击"查询"按钮
4. 查看结果，可导出 CSV

### 配置交易类型
1. 访问 http://172.16.2.164:8083/transaction-types
2. 点击"新增交易类型"
3. 填写交易代码、名称、关联应用
4. 保存配置

### 配置日志目录
1. 访问 http://172.16.2.164:8083/app-log-config
2. 点击"新增应用配置"
3. 选择应用，输入日志目录路径
4. 点击"测试路径"验证
5. 保存配置

---

## 📊 系统状态

| 组件 | 状态 | 端口 |
|------|------|------|
| Nginx | ✅ 运行中 | 8083 |
| Flask | ✅ 运行中 | 5000 |
| 前端 | ✅ 已部署 | - |
| 后端 API | ✅ 新增 4 个接口 | - |

---

## 🔧 维护命令

```bash
# 重新构建前端
cd /root/sft/log-tracker/frontend && npm run build && cp -r dist/* /var/www/log-tracker/

# 重启后端
pkill -f "python3 app_main.py"
cd /root/sft/log-tracker/backend && nohup python3 app_main.py > /tmp/log-tracker.log 2>&1 &

# 查看日志
tail -f /tmp/log-tracker.log
```

---

## 📝 配置文件

- **交易类型**: `/root/sft/log-tracker/config/transaction_types.json`
- **日志目录**: `/root/sft/log-tracker/config/log_dirs.json`

所有配置支持运行时更新，无需重启服务。
