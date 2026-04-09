# 全部应用日志目录配置

**配置日期**: 2026-04-09  
**版本**: v2.0.2

---

## ✅ 配置完成

已配置 **34 个应用** 的日志目录，所有应用日志路径均指向 `/root/sft/testlogs/{service_name}`。

---

## 📋 配置列表

| 序号 | 应用名称 | 日志目录 |
|------|---------|---------|
| 1 | sft-acctasync | /root/sft/testlogs/sft-acctasync |
| 2 | sft-acctrpc | /root/sft/testlogs/sft-acctrpc |
| 3 | sft-admin | /root/sft/testlogs/sft-admin |
| 4 | sft-agrsign | /root/sft/testlogs/sft-agrsign |
| 5 | sft-aigw | /root/sft/testlogs/sft-aigw |
| 6 | sft-aipg | /root/sft/testlogs/sft-aipg |
| 7 | sft-batchapi | /root/sft/testlogs/sft-batchapi |
| 8 | sft-biztask | /root/sft/testlogs/sft-biztask |
| 9 | sft-btresult-http | /root/sft/testlogs/sft-btresult-http |
| 10 | sft-bttrx-listener | /root/sft/testlogs/sft-bttrx-listener |
| 11 | sft-chnlagent | /root/sft/testlogs/sft-chnlagent |
| 12 | sft-chnlbatch | /root/sft/testlogs/sft-chnlbatch |
| 13 | sft-contractsvc | /root/sft/testlogs/sft-contractsvc |
| 14 | sft-gwsign | /root/sft/testlogs/sft-gwsign |
| 15 | sft-merapi | /root/sft/testlogs/sft-merapi |
| 16 | sft-mergetask | /root/sft/testlogs/sft-mergetask |
| 17 | sft-mergetask1 | /root/sft/testlogs/sft-mergetask1 |
| 18 | sft-mergetask2 | /root/sft/testlogs/sft-mergetask2 |
| 19 | sft-mergetask3 | /root/sft/testlogs/sft-mergetask3 |
| 20 | sft-monitor | /root/sft/testlogs/sft-monitor |
| 21 | sft-product | /root/sft/testlogs/sft-product |
| 22 | sft-riskctrl | /root/sft/testlogs/sft-riskctrl |
| 23 | sft-rtresult-http | /root/sft/testlogs/sft-rtresult-http |
| 24 | sft-rtresult-listener | /root/sft/testlogs/sft-rtresult-listener |
| 25 | sft-rttrx-callback | /root/sft/testlogs/sft-rttrx-callback |
| 26 | sft-trxbatch | /root/sft/testlogs/sft-trxbatch |
| 27 | sft-trxcharge | /root/sft/testlogs/sft-trxcharge |
| 28 | sft-trxnotify | /root/sft/testlogs/sft-trxnotify |
| 29 | sft-trxpay | /root/sft/testlogs/sft-trxpay |
| 30 | sft-trxqry | /root/sft/testlogs/sft-trxqry |
| 31 | sft-trxrefund | /root/sft/testlogs/sft-trxrefund |
| 32 | sft-trxtask | /root/sft/testlogs/sft-trxtask |
| 33 | sft-ucpagent | /root/sft/testlogs/sft-ucpagent |
| 34 | sft-web | /root/sft/testlogs/sft-web |

---

## 📁 配置文件

**文件路径**: `/root/sft/log-tracker/config/log_dirs.json`

**文件格式**: JSON

**示例**:
```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
  "sft-product": "/root/sft/testlogs/sft-product",
  ...
}
```

---

## 🔌 API 验证

### 获取服务列表

```bash
curl http://127.0.0.1:5000/api/services
```

**响应**:
```json
{
  "success": true,
  "services": [
    "sft-aipg",
    "sft-trxqry",
    "sft-product",
    ...
  ]
}
```

### 获取日志目录配置

```bash
curl http://127.0.0.1:5000/api/config/log-dirs
```

**响应**:
```json
{
  "success": true,
  "log_dirs": {
    "sft-aipg": "/root/sft/testlogs/sft-aipg",
    "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
    ...
  }
}
```

---

## 🎯 使用说明

### 日志追踪查询

现在可以在 **日志追踪查询** 页面选择任意一个已配置的服务进行查询：

1. 访问 http://172.16.2.164:8083/log-query
2. 输入 REQ_SN 或商户号
3. 选择服务（34 个可选）
4. 输入日志时间（可选）
5. 点击查询

### 配置管理

如需修改某个应用的日志目录：

1. 访问 http://172.16.2.164:8083/app-log-config
2. 找到对应的应用
3. 点击"编辑"
4. 修改日志目录路径
5. 点击"测试路径"验证
6. 保存配置

---

## ⚠️ 注意事项

1. **路径权限**: 确保 nginx worker 用户对日志目录有读取权限
2. **日志格式**: 所有日志文件应遵循统一的格式规范
3. **编码格式**: 支持 GBK、UTF-8 等多种编码自动检测
4. **文件命名**: 日志文件名应包含时间戳（如：`xxx_2026040809.log`）

---

## 🌐 访问地址

- **首页**: http://172.16.2.164:8083
- **日志追踪查询**: http://172.16.2.164:8083/log-query
- **应用日志配置**: http://172.16.2.164:8083/app-log-config

---

## 📊 统计信息

- **总应用数**: 34 个
- **配置文件**: `/root/sft/log-tracker/config/log_dirs.json`
- **配置时间**: 2026-04-09 16:28
- **配置方式**: 批量自动配置
