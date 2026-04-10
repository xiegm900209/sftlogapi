#!/bin/bash
# 配置同步脚本 - 从运行中的实例同步配置到 Docker 容器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 同步配置文件..."
echo "=================="

# 源地址（运行中的实例）
SOURCE_URL="${SOURCE_URL:-http://172.16.2.164:8083}"

# 同步交易类型配置
echo "📋 同步交易类型配置..."
curl -s "$SOURCE_URL/api/transaction-types" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" \
  > config/transaction_types.json
echo "✅ 交易类型配置已更新"

# 同步日志目录配置
echo "📁 同步日志目录配置..."
curl -s "$SOURCE_URL/api/config/log-dirs" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" \
  > config/log_dirs.json
echo "✅ 日志目录配置已更新"

# 同步应用配置
echo "⚙️ 同步应用配置..."
curl -s "$SOURCE_URL/api/config/app" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" \
  > config/app_config.json
echo "✅ 应用配置已更新"

# 更新 sample 文件
echo "📝 更新 Sample 文件..."
cp config/transaction_types.json config/transaction_types.json.sample
cp config/log_dirs.json config/log_dirs.json.sample
cp config/app_config.json config/app_config.json.sample

echo ""
echo "✅ 配置同步完成！"
echo ""
echo "容器会自动加载新配置（无需重启）"
echo "如需手动验证，可运行:"
echo "  docker exec log-tracker cat /app/config/transaction_types.json | head -20"
