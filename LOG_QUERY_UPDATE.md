# 日志追踪查询功能更新

**版本**: v1.2.0  
**更新日期**: 2026-04-09

---

## 📋 更新内容

### 日志时间格式变更

**旧格式**: 日期时间选择器 (YYYY-MM-DD HH:mm:ss)  
**新格式**: 文本输入 (YYYYMMDDHH - 10 位数字)

**示例**: `2026040809` 表示 2026 年 4 月 8 日 9 时的日志文件

---

## 🎯 核心功能

### 查询逻辑

```
1. 用户输入 REQ_SN + 日志时间 (如：2026040809)
       ↓
2. 系统根据时间定位日志文件
   (sft-aipg-sft-aipg-59c947b9c9-cj6fm_zb_2026040809.log)
       ↓
3. 在文件中查找包含 REQ_SN 的行
       ↓
4. 提取该行的 TraceID (第 3 个参数)
   日志格式：[时间][线程][TraceID][级别][环境][公司][服务][]-[内容]
       ↓
5. 使用 TraceID 查询所有包含该 TraceID 的日志行
       ↓
6. 在页面上显示所有相关日志
```

### 日志格式解析

```
[2026-04-08 09:00:00.245][http-apr-8195-exec-2287][TCiDl7n3][INFO][C02][sft][sft-aipg][]-[日志内容]
 │                            │                      │       │   │   │        │
 └─ 时间戳                     └─ 线程                 └─ TraceID └─ 级别 └─ 环境 └─ 公司 └─ 服务
```

**第 3 个参数 `TCiDl7n3` 就是 TraceID**

---

## 🖥️ 页面功能

### 查询条件

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| REQ_SN | 文本 | ✅ | 交易序列号 |
| 商户号 | 文本 | ❌ | 用于过滤结果 |
| 日志时间 | 文本 | ❌ | 格式：YYYYMMDDHH (10 位数字) |
| 服务 | 下拉 | ❌ | 选择要查询的服务 |

### 结果展示

- ✅ 表格显示所有包含 TraceID 的日志
- ✅ 高亮显示包含 REQ_SN 的原始行 (浅蓝色背景)
- ✅ 显示 TraceID 标签
- ✅ 支持展开查看完整日志内容
- ✅ 日志级别彩色标签
- ✅ 支持导出 CSV

---

## 📝 使用示例

### 示例 1: 精确查询

```
REQ_SN: 20260408090000019466514799
日志时间：2026040809
服务：sft-aipg
```

**结果**: 找到 TraceID `TCiDl7n3` 的所有 9 条日志记录

### 示例 2: 模糊查询 (不指定时间)

```
REQ_SN: 20260408090000019466514799
日志时间：(留空)
服务：sft-aipg
```

**结果**: 在所有时间的日志文件中查找

### 示例 3: 带商户号过滤

```
REQ_SN: 20260408090000019466514799
商户号：200000000007133
日志时间：2026040809
服务：sft-aipg
```

**结果**: 找到 TraceID 相关日志，并过滤包含该商户号的记录

---

## 🔌 API 接口

### 请求参数

```
GET /api/log-query?req_sn=xxx&log_time=2026040809&service=sft-aipg&merchant_no=xxx
```

| 参数 | 类型 | 说明 |
|------|------|------|
| req_sn | string | 交易序列号 |
| log_time | string | 日志时间 (10 位数字) |
| service | string | 服务名称 |
| merchant_no | string | 商户号 |

### 响应格式

```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2026-04-08 09:00:00.245",
      "service": "sft-aipg",
      "level": "INFO",
      "traceId": "TCiDl7n3",
      "thread": "http-apr-8195-exec-2287",
      "content": "日志内容...",
      "fullContent": "完整日志内容...",
      "isReqSnMatch": true
    }
  ],
  "trace_id": "TCiDl7n3",
  "total": 9
}
```

---

## 🛠️ 技术实现

### 新增函数

```python
# 根据时间查找日志文件
find_log_files_by_time(service_name, log_time, log_dir)

# 在文件中查找 REQ_SN 并提取 TraceID
find_req_sn_and_trace_id(log_file, req_sn)

# 在所有文件中查找 REQ_SN
find_req_sn_in_all_files(service_name, req_sn, log_dir)

# 根据 TraceID 和时间查询日志
find_logs_by_trace_id_with_time(service_name, trace_id, log_dir, log_time)
```

### 日志文件名格式

```
sft-aipg-sft-aipg-59c947b9c9-cj6fm_zb_2026040809.log
                                              │
                                              └─ 10 位时间戳 (YYYYMMDDHH)
```

### 时间扩展查询

如果指定了 `log_time=2026040809`，系统会查询：
- 主文件：`2026040809`
- 前一小时：`2026040808`
- 后一小时：`2026040810`

---

## 📊 测试结果

**测试用例**: REQ_SN=`20260408090000019466514799`

| 指标 | 值 |
|------|-----|
| TraceID | TCiDl7n3 |
| 日志条数 | 9 条 |
| 查询时间 | < 1 秒 |
| 服务 | sft-aipg |
| 时间范围 | 2026-04-08 09:00:00 |

---

## ⚠️ 注意事项

1. **时间格式**: 必须是 10 位数字，如 `2026040809`
2. **权限**: 确保 nginx 用户对日志目录有读取权限
3. **性能**: 不指定时间会扫描所有文件，建议指定时间范围
4. **编码**: 日志文件可能包含特殊字符 (GBK 编码)

---

## 🔄 相关文件

- 前端：`frontend/src/views/LogQuery.vue`
- 后端：`backend/app_main.py`
- 解析器：`backend/models/log_parser.py`

---

## 📖 访问地址

**http://172.16.2.164:8083/log-query**
