# 配置迁移说明

## 📋 配置文件位置

- **当前配置**: `/root/sft/sftlogapi/config/log_dirs.json`
- **Docker 备份**: `/root/sft/sftlogapi/config/log_dirs.json.docker-backup`
- **配置模板**: `/root/sft/sftlogapi/config/log_dirs.json.sample`

---

## 🔄 本地部署 vs 容器化部署

### 本地部署（当前）

**日志目录**: `/root/sft/testlogs/{service}`

```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry"
}
```

**适用场景**:
- 本地开发测试
- 虚拟机直接部署
- 使用本地 Tengine 转发

---

### 容器化部署（未来）

**日志目录**: `/app/logs/{service}`

```json
{
  "sft-aipg": "/app/logs/sft-aipg",
  "sft-trxqry": "/app/logs/sft-trxqry"
}
```

**Docker 挂载**:
```bash
docker run -d \
  --name sftlogapi \
  -p 8090:80 \
  -v /root/sft/testlogs:/app/logs:ro \
  -v /root/sft/sftlogapi/config:/app/config \
  sftlogapi:v1.0.0
```

**适用场景**:
- Docker 容器化部署
- Kubernetes 集群
- 需要隔离环境

---

## 🔧 配置切换方法

### 本地部署 → 容器化

```bash
# 1. 备份当前配置
cp /root/sft/sftlogapi/config/log_dirs.json /tmp/log_dirs_local.json

# 2. 恢复 Docker 配置
cp /root/sft/sftlogapi/config/log_dirs.json.docker-backup \
   /root/sft/sftlogapi/config/log_dirs.json

# 3. 重启服务
# Docker 容器启动时会自动使用 /app/logs 路径
```

### 容器化 → 本地部署

```bash
# 1. 备份 Docker 配置
cp /root/sft/sftlogapi/config/log_dirs.json /tmp/log_dirs_docker.json

# 2. 恢复本地配置（已自动完成）
# 当前 log_dirs.json 已修改为 /root/sft/testlogs

# 3. 重启 Flask 服务
ps aux | grep "[p]ython3 app_main.py" | grep sftlogapi | awk '{print $2}' | xargs kill
cd /root/sft/sftlogapi/backend && nohup python3 app_main.py > /var/log/sftlogapi_ai.log 2>&1 &
```

---

## 📁 配置文件说明

| 文件 | 用途 | 路径格式 |
|------|------|---------|
| `log_dirs.json` | 当前生效配置 | 本地：`/root/sft/testlogs/` |
| `log_dirs.json.docker-backup` | Docker 配置备份 | 容器：`/app/logs/` |
| `log_dirs.json.sample` | 配置模板（本地） | 本地：`/root/sft/testlogs/` |

---

## ✅ 验证配置

### 1. 检查配置文件

```bash
cat /root/sft/sftlogapi/config/log_dirs.json | head -5
```

期望输出（本地部署）:
```json
{
  "sft-acctasync": "/root/sft/testlogs/sft-acctasync",
  "sft-acctrpc": "/root/sft/testlogs/sft-acctrpc",
  ...
}
```

### 2. 测试 API 查询

```bash
curl -X POST "http://172.16.2.164:8090/sftlogapi/api/ai/query" \
  -H "Authorization: Bearer zhiduoxing-prod" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "trace_id_search",
    "params": {
      "trace_id": "LX260408090024C80C82F3",
      "log_time": "2026040809"
    }
  }'
```

### 3. 检查日志目录

```bash
ls -la /root/sft/testlogs/ | head -10
```

---

## 🚨 注意事项

1. **路径权限**: 确保 Flask 进程有读取日志目录的权限
2. **路径一致性**: 配置路径必须与实际日志目录一致
3. **Docker 挂载**: 容器化时必须挂载日志目录到 `/app/logs`
4. **配置热更新**: 修改配置后需要重启服务才能生效

---

## 📝 修改历史

| 日期 | 操作 | 说明 |
|------|------|------|
| 2026-04-10 17:51 | 修改为本地路径 | 从 `/app/logs/` 改为 `/root/sft/testlogs/` |
| 2026-04-10 17:51 | 备份 Docker 配置 | 保存容器化配置到 `log_dirs.json.docker-backup` |

---

**文档版本**: v1.0  
**更新时间**: 2026-04-10
