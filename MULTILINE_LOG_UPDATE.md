# 多行日志解析更新

**版本**: v1.3.0  
**更新日期**: 2026-04-09

---

## 📋 更新内容

### 日志解析规则

**规则**: 以时间戳开头作为新日志的开始，到下一个时间戳开头之间的所有内容都属于同一行日志。

```
[2026-04-08 09:00:00.335][http-apr-8195-exec-2284][TC5PCfGK][DEBUG][C02][sft][sft-aipg][]-[<?xml version="1.0" encoding="GBK"?><AIPG>
 <INFO>
 <TRX_CODE>200004</TRX_CODE>
 <VERSION>06</VERSION>
 <DATA_TYPE>2</DATA_TYPE>
 <REQ_SN>202604080800000001</REQ_SN>
 ...
</AIPG> ?:?]          ← 这一整块（多行）算作一条日志
[2026-04-08 09:00:00.335][http-apr-8195-exec-2284][TC5PCfGK][INFO][...]  ← 新的日志开始
```

---

## 🔧 技术实现

### 解析逻辑

```python
def read_log_blocks(file_path: str):
    """
    使用生成器逐块读取日志文件
    每条完整的日志记录以时间戳 [YYYY-MM-DD HH:mm:ss.SSS] 开头
    如果一行不以时间戳开头，它属于上一条日志的延续（多行日志）
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_block_lines = []

        for line in f:
            # 检查是否为新的日志块开头（以时间戳开始）
            if re.match(r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\]', line):
                if current_block_lines:
                    # 解析上一个日志块
                    yield parse_log_block(''.join(current_block_lines))

                current_block_lines = [line]
            else:
                # 续行内容，添加到当前块
                current_block_lines.append(line)

        # 处理最后一个块
        if current_block_lines:
            yield parse_log_block(''.join(current_block_lines))
```

### 关键正则

```python
# 检测时间戳开头
r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\]'

# 匹配日志头部
r'^\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[\]-\[(.*)$'
```

---

## 📊 测试结果

### 测试 1: 多行 XML 日志

**REQ_SN**: `202604080800000001`  
**日志时间**: `2026040809`  
**服务**: `sft-aipg`

**结果**:
- ✅ TraceID: `TC5PCfGK`
- ✅ 找到 17 条相关日志
- ✅ 多行 XML 内容完整解析
- ✅ 内容包含完整 XML 结构

### 测试 2: 单行日志

```
[2026-04-08 09:00:00.305][http-apr-8195-exec-2284][TC5PCfGK][DEBUG][C02][sft][sft-aipg][]-[cache-get-null UnifyAuthConfig 200604000002340_200004 ?:?]
```

**结果**: ✅ 正常解析

---

## 📝 日志格式

### 标准格式

```
[时间戳][线程][TraceID][级别][环境][公司][服务][]-[日志内容 ?:?]
```

### 字段说明

| 位置 | 字段 | 示例 |
|------|------|------|
| 1 | 时间戳 | `2026-04-08 09:00:00.335` |
| 2 | 线程 | `http-apr-8195-exec-2284` |
| 3 | TraceID | `TC5PCfGK` |
| 4 | 级别 | `INFO` / `DEBUG` / `ERROR` |
| 5 | 环境 | `C02` |
| 6 | 公司 | `sft` |
| 7 | 服务 | `sft-aipg` |
| 8 | 内容 | `日志信息 ?:?]` |

---

## 🔄 更新文件

| 文件 | 变更内容 |
|------|---------|
| `backend/models/log_parser.py` | 重写解析逻辑，支持多行日志 |
| `backend/app_main.py` | 无变更 |
| `frontend/src/views/LogQuery.vue` | 无变更 |

---

## ✅ 验证通过

- [x] 单行日志正常解析
- [x] 多行 XML 日志完整解析
- [x] TraceID 正确提取（第 3 个参数）
- [x] 查询结果包含所有相关日志
- [x] 前端页面正常显示

---

## 🌐 访问地址

**http://172.16.2.164:8083/log-query**
