#!/bin/bash
# WorkPilot Bot - 后台启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，请先配置环境变量"
    exit 1
fi

# 检查是否已经在运行
if [ -f "workpilot.pid" ]; then
    PID=$(cat workpilot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Bot 已经在运行中 (PID: $PID)"
        echo "如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo "清理旧的 PID 文件..."
        rm -f workpilot.pid
    fi
fi

# 创建日志目录
mkdir -p logs

# 后台启动 Bot
echo "🚀 启动 WorkPilot Bot..."
nohup python main.py > logs/workpilot.log 2>&1 &
PID=$!

# 保存 PID
echo $PID > workpilot.pid

# 等待启动
sleep 2

# 检查是否启动成功
if ps -p $PID > /dev/null; then
    echo "✅ Bot 启动成功！"
    echo "   PID: $PID"
    echo "   日志: logs/workpilot.log"
    echo ""
    echo "查看日志: tail -f logs/workpilot.log"
    echo "停止 Bot: ./stop.sh"
    echo "查看状态: ./status.sh"
else
    echo "❌ Bot 启动失败，请查看日志: logs/workpilot.log"
    rm -f workpilot.pid
    exit 1
fi
