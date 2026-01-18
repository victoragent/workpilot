#!/bin/bash
# WorkPilot Bot - 状态检查脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 PID 文件
if [ ! -f "workpilot.pid" ]; then
    echo "📊 WorkPilot Bot 状态: 未运行"
    exit 1
fi

# 读取 PID
PID=$(cat workpilot.pid)

# 检查进程是否存在
if ps -p $PID > /dev/null 2>&1; then
    echo "📊 WorkPilot Bot 状态: ✅ 运行中"
    echo "   PID: $PID"
    echo "   启动时间: $(ps -p $PID -o lstart=)"
    echo "   CPU 使用: $(ps -p $PID -o %cpu=)%"
    echo "   内存使用: $(ps -p $PID -o %mem=)%"
    echo ""

    # 显示最近的日志
    if [ -f "logs/workpilot.log" ]; then
        echo "📝 最近日志 (最后 10 行):"
        echo "----------------------------------------"
        tail -n 10 logs/workpilot.log
        echo "----------------------------------------"
        echo ""
        echo "查看完整日志: tail -f logs/workpilot.log"
    fi
else
    echo "📊 WorkPilot Bot 状态: ❌ 已停止 (PID 文件存在但进程不存在)"
    rm -f workpilot.pid
    exit 1
fi
