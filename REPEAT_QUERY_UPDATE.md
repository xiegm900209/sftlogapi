# 重复查询支持 - 多 TraceID 分组

**版本**: v1.4.0  
**更新日期**: 2026-04-09

---

## 📋 更新内容

### 问题场景

商户可能发起重复查询，同一个 REQ_SN 对应多个不同的 TraceID：

```bash
# Linux grep 结果示例
grep 202604080800000001 sft-aipg*.log

[2026-04-08 09:00:00.304][...][TC5PCfGK][INFO]...[REQ_SN>202604080800000001</REQ_SN>
[2026-04-08 09:00:03.547][...][TC07bG2Y][INFO]...[REQ_SN>202604080800000001</REQ_SN>
```

**问题**: 同一个 REQ_SN `202604080800000001` 对应两个不同的 TraceID:
- `TC5PCfGK` (第一次查询)
- `TC07bG2Y` (重复查询)

---

## ✅ 解决方案

### 查询逻辑

```
1. 输入 REQ_SN
   ↓
2. 查找所有包含该 REQ_SN 的日志行
   ↓
3. 提取所有不同的 TraceID
   ↓
4. 对每个 TraceID 查询完整链路
   ↓
5. 分组展示
```

### 响应格式

```json
{
  "success": true,
  "trace_count": 2,
  "trace_groups": [
    {
      "trace_id": "TC5PCfGK",
      "log_count": 17,
      "req_sn_count": 1,
      "first_timestamp": "2026-04-08 09:00:00.304",
      "logs": [...]
    },
    {
      "trace_id": "TC07bG2Y",
      "log_count": 15,
      "req_sn_count": 1,
      "first_timestamp": "2026-04-08 09:00:03.547",
      "logs": [...]
    }
  ]
}
```

---

## 🖥️ 前端展示

### 多分组模式 (>1 个 TraceID)

```
┌─────────────────────────────────────────────────┐
│ 查询结果 (32 条)  2 个 TraceID 分组              │
├─────────────────────────────────────────────────┤
│ ▼ TraceID: TC5PCfGK  17 条日志 | 1 次匹配       │
│   2026-04-08 09:00:00.304                       │
│   [表格显示 17 条日志]                            │
├─────────────────────────────────────────────────┤
│ ▶ TraceID: TC07bG2Y  15 条日志 | 1 次匹配       │
│   2026-04-08 09:00:03.547                       │
└─────────────────────────────────────────────────┘
```

### 单分组模式 (1 个 TraceID)

```
┌─────────────────────────────────────────────────┐
│ 查询结果 (17 条)                                 │
├─────────────────────────────────────────────────┤
│ [表格直接显示所有日志]                           │
└─────────────────────────────────────────────────┘
```

---

## 🔌 API 接口

### 请求

```
GET /api/log-query?req_sn=202604080800000001&service=sft-aipg&log_time=2026040809
```

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `trace_count` | number | TraceID 分组数量 |
| `trace_groups` | array | TraceID 分组列表 |
| `trace_groups[].trace_id` | string | TraceID |
| `trace_groups[].log_count` | number | 该 TraceID 的日志条数 |
| `trace_groups[].req_sn_count` | number | 匹配到 REQ_SN 的次数 |
| `trace_groups[].first_timestamp` | string | 第一次出现时间 |
| `trace_groups[].logs` | array | 日志列表 |

---

## 📊 测试结果

### 测试 1: 重复查询场景

**REQ_SN**: `202604080800000001`  
**服务**: `sft-aipg`  
**时间**: `2026040809`

**预期结果**:
- ✅ 找到 2 个 TraceID 分组
- ✅ 第一个 TraceID: `TC5PCfGK` (17 条日志)
- ✅ 第二个 TraceID: `TC07bG2Y` (15 条日志)
- ✅ 分组按时间排序

### 测试 2: 单次查询场景

**REQ_SN**: `20260408090000019466514799`  
**服务**: `sft-aipg`  
**时间**: `2026040809`

**预期结果**:
- ✅ 找到 1 个 TraceID 分组
- ✅ TraceID: `TCiDl7n3` (9 条日志)
- ✅ 直接显示表格

---

## 🛠️ 技术实现

### 后端变更

**文件**: `backend/app_main.py`

```python
# 查找所有包含 REQ_SN 的行
trace_id_map = {}
for log_block in read_log_blocks(log_file):
    if req_sn in log_block.content:
        trace_id = log_block.trace_id
        if trace_id not in trace_id_map:
            trace_id_map[trace_id] = []
        trace_id_map[trace_id].append(log_block)

# 对每个 TraceID 查询完整链路
for trace_id, logs in trace_id_map.items():
    trace_logs = find_logs_by_trace_id_with_time(...)
    # 构建分组信息
```

### 前端变更

**文件**: `frontend/src/views/LogQuery.vue`

- 新增 `traceGroups` 数据字段
- 新增 `activeGroups` 控制折叠面板
- 新增多分组展示 UI (el-collapse)
- 保留单分组展示 UI (el-table)

---

## 📁 更新文件

| 文件 | 变更内容 |
|------|---------|
| `backend/app_main.py` | 支持多 TraceID 查询和分组 |
| `frontend/src/views/LogQuery.vue` | 支持分组折叠展示 |

---

## 🌐 访问地址

**http://172.16.2.164:8083/log-query**

---

## ⚠️ 注意事项

1. **重复查询识别**: 系统会自动检测同一个 REQ_SN 是否对应多个 TraceID
2. **分组排序**: 按 TraceID 第一次出现的时间排序
3. **性能优化**: 指定日志时间可以加快查询速度
4. **商户号过滤**: 如果有商户号过滤条件，会应用到所有分组
