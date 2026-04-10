# sftlogapi 部署说明

## 📦 部署信息

| 项目 | 值 |
|------|-----|
| 项目名称 | sftlogapi |
| 部署方式 | 本地部署（非容器化） |
| 项目路径 | /root/sft/sftlogapi/ |
| Flask 端口 | 5001 |
| Tengine 端口 | 8090 |

## 🌐 访问地址

- **首页**: `http://172.16.2.164:8090/sftlogapi/`
- **日志查询**: `http://172.16.2.164:8090/sftlogapi/log-query`
- **交易追踪**: `http://172.16.2.164:8090/sftlogapi/transaction-trace`
- **配置管理**: `http://172.16.2.164:8090/sftlogapi/config`
- **API 接口**: `http://172.16.2.164:8090/sftlogapi/api/services`

## 🔧 启动/停止命令

### 一键启动
```bash
cd /root/sft/sftlogapi
./start.sh
```

### 手动启动
```bash
# 1. 复制前端静态文件
mkdir -p /var/www/sftlogapi
cp -r /root/sft/sftlogapi/frontend/dist/* /var/www/sftlogapi/

# 2. 启动 Flask 后端
cd /root/sft/sftlogapi/backend
nohup python3 app_main.py > /var/log/sftlogapi.log 2>&1 &

# 3. 重启 Tengine（如修改了配置）
/usr/local/tengine/sbin/nginx -s reload
```

### 停止服务
```bash
# 查找进程
ps aux | grep "[p]ython3 app_main.py" | grep sftlogapi

# 停止进程
kill <PID>
```

### 查看日志
```bash
tail -f /var/log/sftlogapi.log
```

## 📁 配置文件

- **Flask 后端**: `/root/sft/sftlogapi/backend/app_main.py`
- **前端静态文件**: `/var/www/sftlogapi/`
- **Tengine 配置**: `/usr/local/tengine/conf/conf.d/sftlogapi.conf`
- **日志目录配置**: `/root/sft/sftlogapi/config/log_dirs.json`
- **交易类型配置**: `/root/sft/sftlogapi/config/transaction_types.json`

## 🏗️ 架构说明

```
用户请求
    ↓
Tengine (8090 端口)
    ↓
┌─────────────────────────────────────┐
│ /sftlogapi/      → 静态文件          │
│ /sftlogapi/api/  → Flask (5001)     │
│ /sftlogapi/search/ → Flask (5001)   │
│ /sftlogapi/config/ → Flask (5001)   │
└─────────────────────────────────────┘
    ↓
Flask 后端 (5001 端口)
    ↓
日志文件 (/root/sft/testlogs/)
```

## ✅ 验证步骤

1. 检查 Flask 进程：
   ```bash
   ps aux | grep "[p]ython3 app_main.py" | grep sftlogapi
   ```

2. 检查端口监听：
   ```bash
   netstat -tlnp | grep 5001
   netstat -tlnp | grep 8090
   ```

3. 测试 API：
   ```bash
   curl http://172.16.2.164:8090/sftlogapi/api/services
   ```

4. 访问前端：
   ```
   http://172.16.2.164:8090/sftlogapi/
   ```

## 📝 与 log-tracker 的区别

| 项目 | log-tracker | sftlogapi |
|------|-------------|-----------|
| 部署方式 | Docker 容器 | 本地部署 |
| Tengine 端口 | 8083 | 8090 |
| Flask 端口 | 5000 | 5001 |
| 子路径 | /log-tracker/ | /sftlogapi/ |
| 项目路径 | /root/sft/log-tracker/ | /root/sft/sftlogapi/ |
| 前端文件 | /var/www/log-tracker/ | /var/www/sftlogapi/ |

## ⚠️ 注意事项

1. **端口占用**: 确保 5001 和 8090 端口未被其他服务占用
2. **日志目录**: 确保 `/root/sft/testlogs/` 目录存在且有读取权限
3. **配置文件**: 修改配置后无需重启，Flask 会实时读取
4. **前端更新**: 修改前端代码后需要重新构建并复制静态文件
