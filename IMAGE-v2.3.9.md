# 镜像迁移说明 - v2.3.9

## 📦 镜像信息

| 项目 | 详情 |
|------|------|
| **镜像文件** | `log-tracker-v2.3.9.tar` |
| **文件大小** | 53MB |
| **镜像版本** | v2.3.9 |
| **创建时间** | 2026-04-10 13:46 |
| **配置状态** | ✅ 已包含最新配置 |

---

## ✅ 已打包的最新配置

### 1. 日志目录配置 (34 个应用)

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry",
  "sft-pay": "/app/logs/sft-pay",
  "sft-batchpay": "/app/logs/sft-batchpay",
  ... (共 34 个应用)
}
```

### 2. 交易类型配置 (12 个交易类型)

```json
{
  "100001": {"name": "代收", "apps": [...]},
  "100002": {"name": "代付", "apps": [...]},
  "100007": {"name": "实时转账", "apps": [...]},
  ... (共 12 个交易类型)
}
```

---

## 🚀 迁移步骤

### 步骤 1：传输镜像文件

```bash
# 方式一：scp 传输
scp /root/sft/log-tracker/log-tracker-v2.3.9.tar user@target-server:/tmp/

# 方式二：U 盘拷贝
cp /root/sft/log-tracker/log-tracker-v2.3.9.tar /mnt/usb/
```

### 步骤 2：导入镜像

在目标机器执行：

```bash
docker load -i /tmp/log-tracker-v2.3.9.tar
```

验证导入：

```bash
docker images log-tracker
# 应显示：log-tracker v2.3.9 218MB
```

### 步骤 3：启动容器

```bash
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /你的/日志/路径:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.9
```

**重要参数说明**：
- `-v /你的/日志/路径:/app/logs:ro` - **必须修改**为实际日志路径
- `-p 8089:80` - 可根据需要修改端口

### 步骤 4：验证运行

```bash
# 查看状态
docker ps | grep log-tracker

# 测试 API
curl http://localhost:8089/api/services

# 测试日志查询
curl "http://localhost:8089/api/log-query?req_sn=xxx&service=sft-aipg&log_time=2026040809"
```

---

## ⚠️ 重要说明

### 1. 日志目录挂载

**必须挂载日志目录**，否则无法查询日志：

```bash
# 正确示例
-v /root/sft/testlogs:/app/logs:ro

# 或目标环境的实际路径
-v /data/logs:/app/logs:ro
```

### 2. 配置文件

配置已打包在镜像中，**无需额外挂载配置文件**。

如需自定义配置，可挂载：

```bash
-v ./config:/app/config
```

### 3. 端口映射

如果 8089 端口被占用，可改用其他端口：

```bash
# 使用 80 端口
-p 80:80

# 或使用 8088 端口
-p 8088:80
```

---

## 📋 配置清单

| 配置项 | 数量 | 状态 |
|--------|------|------|
| 应用日志目录 | 34 个 | ✅ 已打包 |
| 交易类型 | 12 个 | ✅ 已打包 |
| 应用配置 | 完整 | ✅ 已打包 |

---

## 🔧 快速启动脚本

在目标机器创建脚本：

```bash
#!/bin/bash
# start-log-tracker.sh

set -e

# 导入镜像
docker load -i log-tracker-v2.3.9.tar

# 启动容器
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.9

echo "✅ 启动成功！"
echo "🌐 访问地址：http://localhost:8089"
```

使用：

```bash
chmod +x start-log-tracker.sh
./start-log-tracker.sh
```

---

## 📊 验证检查清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| 镜像导入 | `docker images log-tracker` | v2.3.9 |
| 容器运行 | `docker ps \| grep log-tracker` | Up (healthy) |
| 服务列表 | `curl localhost:8089/api/services` | 34 个应用 |
| 交易类型 | `curl localhost:8089/api/transaction-types` | 12 个类型 |
| 日志查询 | `curl localhost:8089/api/log-query?...` | 正常返回 |

---

## 📞 故障排查

### 容器无法启动

```bash
# 查看日志
docker logs log-tracker

# 检查端口占用
netstat -tlnp | grep 8089
```

### 查询不到日志

1. 检查日志目录挂载是否正确
2. 确认日志目录有读权限
3. 验证日志时间格式 (YYYYMMDDHH)

### 配置未生效

配置已打包在镜像中，如需修改：

```bash
# 挂载自定义配置
docker run -d \
  --name log-tracker \
  -v ./config:/app/config \
  ...
```

---

## 📁 文件位置

| 文件 | 路径 |
|------|------|
| 镜像文件 | `/root/sft/log-tracker/log-tracker-v2.3.9.tar` |
| 配置文件 | `/root/sft/log-tracker/config/` |
| 迁移文档 | `/root/sft/log-tracker/MIGRATION.md` |

---

**最后更新**: 2026-04-10 13:46  
**版本**: v2.3.9  
**状态**: ✅ 已验证，可迁移
