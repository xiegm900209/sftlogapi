# 配置问题修复指南

## ⚠️ 问题现象

在目标机器启动容器后，应用日志配置页面只显示 5 个应用，而不是 34 个。

**原因**: 配置文件虽然打包在镜像中，但可能由于以下原因未正确加载：
1. 容器启动时挂载了外部配置文件覆盖了镜像内置配置
2. Flask 后端启动时读取了错误的配置路径
3. 配置文件权限问题

---

## ✅ 解决方案

### 方案一：使用镜像内置配置（推荐）

**不要挂载 config 目录**，直接使用镜像内置的配置：

```bash
# 停止旧容器
docker rm -f log-tracker

# 启动容器（不挂载 config）
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.9
```

**验证配置**:
```bash
# 检查容器内配置
docker exec log-tracker cat /app/config/log_dirs.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'配置应用数：{len(d)}')"
# 应输出：配置应用数：34

# 测试 API
curl http://localhost:8089/api/config/log-dirs | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'API 返回：{len(d.get(\"log_dirs\", {}))} 个应用')"
# 应输出：API 返回：34 个应用
```

---

### 方案二：挂载外部配置文件

如果需要自定义配置，可以挂载外部配置文件：

```bash
# 准备配置文件
mkdir -p /app/sharenfs/log-tracker/config

# 下载最新配置
curl http://172.16.2.164:8089/api/config/log-dirs | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('log_dirs', d), indent=2, ensure_ascii=False))" \
  > /app/sharenfs/log-tracker/config/log_dirs.json

curl http://172.16.2.164:8089/api/transaction-types | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('transaction_types', {}), indent=2, ensure_ascii=False))" \
  > /app/sharenfs/log-tracker/config/transaction_types.json

# 启动容器（挂载 config）
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  -v /app/sharenfs/log-tracker/config:/app/config \
  --restart unless-stopped \
  log-tracker:v2.3.9
```

---

## 🔧 快速部署脚本

使用提供的部署脚本：

```bash
# 复制脚本到目标机器
scp deploy.sh sftuser@target-host:/tmp/

# 在目标机器执行
ssh sftuser@target-host
chmod +x /tmp/deploy.sh
/tmp/deploy.sh
```

---

## 📋 验证检查清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| 容器状态 | `docker ps \| grep log-tracker` | Up (healthy) |
| 容器内配置 | `docker exec log-tracker cat /app/config/log_dirs.json \| python3 -c "..."` | 34 个应用 |
| API 服务列表 | `curl localhost:8089/api/services` | 34 个应用 |
| API 日志目录 | `curl localhost:8089/api/config/log-dirs` | 34 个应用 |
| API 交易类型 | `curl localhost:8089/api/transaction-types` | 12 个类型 |
| 页面显示 | 访问 http://localhost:8089/app-log-config | 34 个应用 |

---

## ⚠️ 常见错误

### 错误 1：只显示 5 个应用

**原因**: 配置文件未正确加载

**解决**:
```bash
# 检查容器内配置文件
docker exec log-tracker cat /app/config/log_dirs.json

# 如果文件不存在或内容不对，重启容器
docker rm -f log-tracker
docker run -d --name log-tracker -p 8089:80 -v /app/sharenfs/sft-logs:/app/logs:ro log-tracker:v2.3.9
```

### 错误 2：配置被外部挂载覆盖

**原因**: 挂载了外部 config 目录

**解决**: 移除 config 挂载，使用镜像内置配置

```bash
# 错误的方式（会覆盖镜像配置）
-v ./config:/app/config  # ❌

# 正确的方式（使用镜像内置配置）
# 不挂载 config 目录  # ✅
```

---

## 📊 配置说明

### 镜像内置配置 (v2.3.9)

| 配置项 | 数量 | 路径 |
|--------|------|------|
| 应用日志目录 | 34 个 | `/app/config/log_dirs.json` |
| 交易类型 | 12 个 | `/app/config/transaction_types.json` |

### 配置路径

| 文件 | 容器内路径 |
|------|-----------|
| 日志目录 | `/app/config/log_dirs.json` |
| 交易类型 | `/app/config/transaction_types.json` |
| 应用配置 | `/app/config/app_config.json` |

---

## 🚀 完整部署命令

```bash
# 1. 导入镜像
docker load -i log-tracker-v2.3.9.tar

# 2. 停止旧容器
docker rm -f log-tracker 2>/dev/null || true

# 3. 启动容器（使用镜像内置配置）
docker run -d \
  --name log-tracker \
  -p 8089:80 \
  -v /app/sharenfs/sft-logs:/app/logs:ro \
  --restart unless-stopped \
  log-tracker:v2.3.9

# 4. 验证
sleep 6
docker exec log-tracker cat /app/config/log_dirs.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ 配置：{len(d)} 个应用')"
curl http://localhost:8089/api/services | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ 服务：{len(d.get(\"services\", []))} 个应用')"

echo "✅ 部署完成！访问：http://localhost:8089"
```

---

**最后更新**: 2026-04-10 14:06  
**版本**: v2.3.9
