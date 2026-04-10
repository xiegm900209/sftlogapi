# 镜像更新说明 - v2.3.10

## 🐛 修复问题

**问题**: v2.3.9 镜像中配置文件的路径仍然是 `/root/sft/testlogs/`，导致在目标机器上无法正确加载配置。

**修复**: v2.3.10 已修复配置文件路径，全部改为容器内路径 `/app/logs/`。

---

## 📦 新镜像信息

| 项目 | 详情 |
|------|------|
| **镜像文件** | `log-tracker-v2.3.10.tar` |
| **文件大小** | 53MB |
| **镜像版本** | v2.3.10 |
| **创建时间** | 2026-04-10 14:13 |
| **配置路径** | ✅ 已修复为 `/app/logs/` |

---

## 🚀 迁移到目标机器

### 步骤 1：传输镜像

```bash
scp /root/sft/log-tracker/log-tracker-v2.3.10.tar sftuser@target-host:/tmp/
```

### 步骤 2：导入并启动

在目标机器执行：

```bash
# 停止旧容器
docker rm -f log-tracker

# 导入新镜像
docker load -i /tmp/log-tracker-v2.3.10.tar

# 启动容器
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.10
```

### 步骤 3：验证配置

```bash
# 等待启动
sleep 6

# 验证容器内配置
docker exec log-tracker cat /app/config/log_dirs.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'配置应用数：{len(d)}')"
# 应输出：配置应用数：34

# 测试 API
curl http://localhost:8089/api/config/log-dirs | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'API 返回：{len(d.get(\"log_dirs\", {}))} 个应用')"
# 应输出：API 返回：34 个应用

# 访问页面验证
echo "访问：http://localhost:8089/app-log-config"
```

---

## ✅ 验证清单

| 检查项 | 预期结果 |
|--------|----------|
| 容器状态 | Up (healthy) |
| 容器内配置路径 | `/app/logs/xxx` |
| 配置应用数 | 34 个 |
| 交易类型数 | 12 个 |
| API 服务列表 | 34 个应用 |
| 页面显示 | 34 个应用 |

---

## 📋 配置对比

### v2.3.9（旧版本 - 有问题）

```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry"
}
```

❌ 路径是宿主机路径，无法在容器内使用

### v2.3.10（新版本 - 已修复）

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry"
}
```

✅ 路径是容器内路径，正确挂载后可以使用

---

## ⚠️ 重要提示

1. **必须使用 v2.3.10 或更高版本**
2. **挂载日志目录**: `-v /app/sharenfs/sft-logs:/app/logs:ro`
3. **不要挂载 config**: 配置已打包在镜像中

---

**最后更新**: 2026-04-10 14:13  
**版本**: v2.3.10  
**状态**: ✅ 已修复配置路径
