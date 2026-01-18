#!/bin/bash
# WorkPilot Bot - 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 PID 文件
if [ ! -f "workpilot.pid" ]; then
    echo "❌ Bot 未在运行"
    exit 1
fi

# 读取 PID
PID=$(cat workpilot.pid)

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Bot 进程不存在 (PID: $PID)"
    rm -f workpilot.pid
    exit 1
fi

# 停止进程
echo "🛑 停止 WorkPilot Bot (PID: $PID)..."
kill $PID

# 等待进程结束
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ Bot 已停止"
        rm -f workpilot.pid
        exit 0
    fi
    sleep 1
done

# 如果还没停止，强制终止
echo "⚠️  强制终止 Bot..."
kill -9 $PID
rm -f workpilot.pid
echo "✅ Bot 已强制停止"
