# 中文乱码修复

**版本**: v1.5.0  
**修复日期**: 2026-04-09

---

## 🐛 问题描述

### 现象

日志中的中文在页面显示为乱码：

**原始日志**:
```
[2026-04-08 09:00:00.628][...][INFO]...-[请求处理完成：270 - 1002 3476885078078918656 310011 2006040000013768 20260408090000358 159.75.245.95 3043 协议号未找到或失效 - GBK ?:?]
```

**页面显示**:
```
[2026-04-08 09:00:00.628][...][INFO]...-[: 270 - 1002 3476885078078918656 310011 2006040000013768 20260408090000358 159.75.245.95 3043 ЭδҵʧЧ - GBK]
```

### 原因

日志文件使用 **GBK 编码**，但系统默认按 UTF-8 读取，导致中文字符解码错误。

---

## ✅ 解决方案

### 编码检测逻辑

```python
def read_log_blocks(file_path: str):
    # 尝试不同编码读取文件 - GBK 在前因为中文日志通常是 GBK
    encodings = ['gbk', 'gb18030', 'utf-8']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    
    if content is None:
        # 如果所有编码都失败，使用 latin-1 读取所有字节
        # 然后尝试按 GBK 解码中文部分
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
        try:
            content = raw_bytes.decode('gbk', errors='replace')
        except:
            content = raw_bytes.decode('latin-1')
    
    # 按行处理...
```

### 优先级

1. **GBK** - 中文日志系统最常用
2. **GB18030** - GBK 的超集
3. **UTF-8** - 国际通用
4. **Latin-1 + GBK 重试** - 处理 ISO-8859 文件

---

## 📊 测试结果

### 测试 1: 中文日志读取

**文件**: `sft-aipg-sft-aipg-59c947b9c9-cj6fm_zb_2026040809.log`

```python
✓ 找到中文日志 #1
  内容：过滤耗时:0
```

### 测试 2: 包含"协议"的日志

**文件**: 同上

```python
Log 246: <?xml version="1.0" encoding="GBK"?><AIPG>
  <INFO>
    <TRX_CODE>310011</TRX_CODE>
    ...
    <ERR_MSG>协议号未找到或失效</ERR_MSG>
  </INFO>
</AIPG>
```

### 测试 3: 文件编码检测

```bash
file sft-aipg*.log
# 输出：ISO-8859 text, with very long lines
```

虽然 `file` 命令检测为 ISO-8859，但实际包含 GBK 中文字符。

---

## 📁 更新文件

| 文件 | 变更内容 |
|------|---------|
| `backend/models/log_parser.py` | 支持多编码检测，优先 GBK |

---

## 🌐 访问地址

**http://172.16.2.164:8083/log-query**

---

## ⚠️ 注意事项

1. **编码优先级**: GBK > GB18030 > UTF-8 > Latin-1
2. **性能影响**: 多编码检测会增加少量开销
3. **兼容性**: 支持 UTF-8、GBK、GB18030、ISO-8859-1 编码的日志文件
4. **错误处理**: 使用 `errors='replace'` 替换无法识别的字符

---

## 🔍 常见问题

### Q: 为什么不直接用 UTF-8？

A: 中国金融系统很多日志文件使用 GBK 编码，直接指定 UTF-8 会导致中文乱码。

### Q: 如何确认日志文件编码？

A: 使用 `file` 命令或文本编辑器查看，但最可靠的方法是尝试多种编码。

### Q: 会影响性能吗？

A: 影响很小。通常第一次尝试 GBK 就能成功，不会遍历所有编码。
