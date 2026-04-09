# 新增功能说明

**版本**: v1.1.0  
**发布日期**: 2026-04-09

## 功能概述

本次更新新增三个主要功能模块，增强了日志追踪系统的配置管理和查询能力。

---

## 需求 1: 日志追踪查询页面

**访问路径**: `/log-query`  
**菜单**: 日志追踪查询

### 功能特性

- **多条件组合查询**
  - REQ_SN（交易序列号）
  - 商户号
  - 交易时间范围
  - 服务选择

- **结果展示**
  - 表格形式展示查询结果
  - 支持展开查看完整日志内容
  - 日志级别彩色标签（ERROR/WARN/INFO/DEBUG）
  - 分页显示（20/50/100/200 条/页）

- **导出功能**
  - 支持导出 CSV 格式
  - 包含 BOM 头，兼容 Excel 打开

### 使用示例

1. 输入 REQ_SN `20240409123456` 查询特定交易日志
2. 输入商户号 `MERCHANT123` 查询该商户所有交易
3. 选择时间范围 `2024-04-09 00:00:00` 至 `2024-04-09 23:59:59` 查询当天日志
4. 组合使用多个条件进行精确查询

---

## 需求 2: 交易类型管理页面

**访问路径**: `/transaction-types`  
**菜单**: 配置管理 > 交易类型管理

### 功能特性

- **交易类型列表**
  - 显示所有已配置的交易类型
  - 展示交易代码、名称、关联应用
  - 应用数量统计

- **新增交易类型**
  - 交易代码（保存后不可修改）
  - 交易名称
  - 关联应用（多选）

- **编辑交易类型**
  - 修改交易名称
  - 调整关联应用

- **删除交易类型**
  - 二次确认防止误删
  - 实时保存到配置文件

### 数据结构

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

### 配置文件

- **路径**: `/root/sft/log-tracker/config/transaction_types.json`
- **格式**: JSON
- **权限**: 需要写权限

---

## 需求 3: 应用日志目录配置页面

**访问路径**: `/app-log-config`  
**菜单**: 配置管理 > 应用日志配置

### 功能特性

- **配置列表**
  - 显示所有应用的日志目录配置
  - 实时检测路径是否存在
  - 状态标签（存在/不存在）

- **新增应用配置**
  - 选择应用名称（下拉选择，已配置的自动禁用）
  - 输入日志目录路径
  - 路径测试功能

- **编辑应用配置**
  - 修改日志目录路径
  - 实时验证路径有效性

- **删除应用配置**
  - 二次确认
  - 自动保存

### 路径验证

- 检查路径是否存在
- 检查是否为目录
- 检查是否可读
- 显示目录文件数量

### 配置文件

- **路径**: `/root/sft/log-tracker/config/log_dirs.json`
- **格式**: JSON
- **示例**:
  ```json
  {
    "sft-aipg": "/root/sft/testlogs/sft-aipg",
    "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
    "sft-pay": "/root/sft/testlogs/sft-pay"
  }
  ```

---

## API 接口

### 新增接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/log-query` | GET | 综合日志查询 |
| `/api/config/transaction-types` | POST | 更新交易类型配置 |
| `/api/config/log-dirs` | GET/POST | 获取/更新日志目录配置 |
| `/api/config/validate-path` | POST | 验证路径是否存在 |

### 请求示例

#### 日志查询
```bash
curl "http://172.16.2.164:8083/api/log-query?req_sn=12345&merchant_no=M001&start_time=2024-04-09%2000:00:00&end_time=2024-04-09%2023:59:59"
```

#### 更新交易类型
```bash
curl -X POST http://172.16.2.164:8083/api/config/transaction-types \
  -H "Content-Type: application/json" \
  -d '{"310011":{"name":"协议支付","apps":["sft-aipg","sft-trxqry"]}}'
```

#### 更新日志目录
```bash
curl -X POST http://172.16.2.164:8083/api/config/log-dirs \
  -H "Content-Type: application/json" \
  -d '{"sft-aipg":"/root/sft/testlogs/sft-aipg"}'
```

#### 验证路径
```bash
curl -X POST http://172.16.2.164:8083/api/config/validate-path \
  -H "Content-Type: application/json" \
  -d '{"path":"/root/sft/testlogs/sft-aipg"}'
```

---

## 技术实现

### 前端

- **框架**: Vue 3 + Vite
- **UI 库**: Element Plus
- **新增组件**:
  - `LogQuery.vue` - 日志追踪查询
  - `TransactionTypeManage.vue` - 交易类型管理
  - `AppLogConfig.vue` - 应用日志配置
- **路由**: 新增 3 个路由
- **导航**: 更新主导航菜单

### 后端

- **框架**: Flask
- **新增路由**: 4 个 API 接口
- **配置文件**: 支持运行时更新 JSON 配置
- **路径验证**: 使用 `os.path` 和 `os.access`

---

## 注意事项

1. **权限要求**
   - nginx worker 用户需要对日志目录有读取权限
   - 配置文件需要写权限

2. **路径配置**
   - 建议使用绝对路径
   - 避免使用 `~` 或环境变量

3. **配置保存**
   - 所有配置实时保存到文件
   - 修改后立即生效，无需重启服务

4. **性能考虑**
   - 日志查询建议添加时间范围限制
   - 大文件搜索可能需要较长时间

---

## 后续优化

- [ ] 支持更多查询条件（TraceID、日志级别等）
- [ ] 批量导入/导出配置
- [ ] 配置变更历史记录
- [ ] 日志目录自动发现
- [ ] 查询结果缓存机制
