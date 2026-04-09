# 日志时间必填更新

**版本**: v2.3.1  
**更新日期**: 2026-04-09

---

## 📋 更新说明

### 问题背景

之前的查询接口中，日志时间参数 (`log_time`) 是可选的。这导致以下问题：

1. **性能风险**: 用户可能不输入时间，系统需要扫描所有日志文件
2. **系统崩溃**: 当日志文件数量巨大时，全量扫描会导致内存溢出
3. **查询缓慢**: 全量扫描耗时过长，用户体验差

### 解决方案

**强制要求输入日志时间**，所有查询接口必须提供 `log_time` 参数。

---

## ✅ 变更内容

### 1. 前端验证

#### 日志追踪查询 (`/log-query`)

**变更**:
- ✅ 日志时间字段标记为必填 (`required`)
- ✅ 占位符提示"*必填"
- ✅ 提交前验证：未输入时间则拦截
- ✅ 格式验证：必须是 10 位数字

**代码**:
```javascript
// 强制要求输入日志时间
if (!this.queryForm.logTime) {
  this.$message.error('请输入日志时间（必填），格式：2026040809')
  return
}

// 验证时间格式
const timePattern = /^\d{10}$/
if (!timePattern.test(this.queryForm.logTime)) {
  this.$message.error('日志时间格式不正确，应为 10 位数字（如：2026040809）')
  return
}
```

#### 交易类型追踪 (`/transaction-trace`)

**变更**: 同上

---

### 2. 后端验证

#### API: `/api/transaction-trace`

**变更**:
```python
# 强制要求输入日志时间，防止查询全量日志
if not log_time:
    return jsonify({
        'success': False,
        'message': '请输入日志时间（必填），格式：YYYYMMDDHH（如：2026040809）'
    }), 400

# 验证时间格式
import re
if not re.match(r'^\d{10}$', log_time):
    return jsonify({
        'success': False,
        'message': '日志时间格式不正确，应为 10 位数字（如：2026040809）'
    }), 400
```

#### API: `/api/log-query`

**变更**: 同上

---

### 3. 用户界面

#### 首页说明更新

**变更前**:
```
📝 日志时间格式：输入 10 位数字，格式为 YYYYMMDDHH（如：2026040809）
```

**变更后**:
```
📝 日志时间格式：输入 10 位数字，格式为 YYYYMMDDHH（如：2026040809）（必填，防止系统过载）
```

---

## 📊 测试验证

### 测试 1: 不输入时间

**请求**:
```bash
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=xxx"
```

**响应**:
```json
{
  "success": false,
  "message": "请输入日志时间（必填），格式：YYYYMMDDHH（如：2026040809）"
}
```

✅ **通过**

### 测试 2: 时间格式错误

**请求**:
```bash
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=xxx&log_time=20260408"
```

**响应**:
```json
{
  "success": false,
  "message": "日志时间格式不正确，应为 10 位数字（如：2026040809）"
}
```

✅ **通过**

### 测试 3: 正常查询

**请求**:
```bash
curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=xxx&log_time=2026040809"
```

**响应**: HTTP 200 (正常处理)

✅ **通过**

---

## 🎯 影响范围

### 受影响的接口

| 接口 | 变更 | 影响 |
|------|------|------|
| `/api/transaction-trace` | `log_time` 必填 | 高 |
| `/api/log-query` | `log_time` 必填 | 高 |
| `/api/search` | 无变更 | 无 |
| `/api/search-by-trace` | 无变更 | 无 |

### 受影响的前端页面

| 页面 | 变更 |
|------|------|
| `/log-query` | 日志时间必填验证 |
| `/transaction-trace` | 日志时间必填验证 |

---

## 📝 用户指南

### 正确的输入方式

✅ **正确**:
- `2026040809` (2026 年 4 月 8 日 9 时)
- `2026040915` (2026 年 4 月 9 日 15 时)

❌ **错误**:
- `20260408` (只有 8 位)
- `2026-04-08` (包含横杠)
- `202604080900` (12 位)
- 空值

### 如何确定日志时间

1. **查看日志文件名**: `sft-aipg-xxx_2026040809.log`
   - 时间部分：`2026040809`

2. **不确定具体时间**:
   - 先查询前后 3 个小时
   - 例如：`2026040808`, `2026040809`, `2026040810`

3. **跨天查询**:
   - 需要分别查询不同日期的时间段
   - 例如：`2026040823` 和 `2026040900`

---

## ⚠️ 注意事项

### 对现有用户的影响

- **已有查询**: 需要添加时间参数
- **API 调用**: 必须传入 `log_time` 参数
- **AI 集成**: Function Calling 中 `log_time` 改为必填

### 性能提升

| 场景 | 变更前 | 变更后 | 提升 |
|------|--------|--------|------|
| 查询单个文件 | 100ms | 100ms | - |
| 查询 10 个文件 | 1s | 1s | - |
| 查询全部文件 | 100s+ | ❌ 禁止 | ∞ |

**结论**: 强制时间输入避免了全量扫描，防止系统崩溃。

---

## 🔄 回滚方案

如需回滚（不推荐）：

1. **前端**: 移除必填验证
2. **后端**: 移除时间参数检查
3. **文档**: 更新说明

**命令**:
```bash
git revert <commit-hash>
```

---

## 📁 变更文件

| 文件 | 变更内容 |
|------|---------|
| `frontend/src/views/LogQuery.vue` | 添加必填验证 |
| `frontend/src/views/TransactionTrace.vue` | 添加必填验证 |
| `frontend/src/views/Home.vue` | 更新使用说明 |
| `backend/app_main.py` | 添加后端验证逻辑 |
| `REQUIRED_TIME_PARAM_UPDATE.md` | 本文档 |

---

## 🚀 部署步骤

1. **构建前端**:
   ```bash
   cd frontend
   npm run build
   ```

2. **部署前端**:
   ```bash
   rm -rf /var/www/log-tracker/*
   cp -r dist/* /var/www/log-tracker/
   ```

3. **重启后端**:
   ```bash
   pkill -f "python3 app_main.py"
   cd backend && nohup python3 app_main.py > /tmp/log-tracker.log 2>&1 &
   ```

4. **验证**:
   ```bash
   curl "http://localhost:5000/api/transaction-trace?transaction_type=310011&req_sn=xxx"
   # 应返回：请输入日志时间（必填）
   ```

---

## 📊 版本信息

- **当前版本**: v2.3.1
- **上一版本**: v2.3.0
- **变更类型**: 功能增强 + Bug 修复
- **向后兼容**: ❌ 不兼容（API 变更）

---

## 🎯 后续优化

- [ ] 添加时间范围查询（开始时间 - 结束时间）
- [ ] 支持模糊时间匹配（如：20260408* 查询整天）
- [ ] 添加查询超时限制
- [ ] 实现查询结果缓存
- [ ] 添加查询频率限制

---

<div align="center">

**强制时间输入，保护系统稳定！** 🛡️

[查看 API 文档](/api/docs) | [用户指南](#用户指南)

</div>
