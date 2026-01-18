#!/bin/bash
# WorkPilot Bot - 重启脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 重启 WorkPilot Bot..."
echo ""

# 先停止
./stop.sh

# 等待停止完成
sleep 2

# 再启动
./start.sh
