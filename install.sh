#!/bin/bash
# WorkPilot 安装脚本

set -e

echo "================================"
echo "WorkPilot 安装向导"
echo "================================"
echo ""

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.9 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ 检测到 Python $PYTHON_VERSION"

# 检查是否存在虚拟环境
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在"
    read -p "是否删除并重新创建? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧的虚拟环境..."
        rm -rf venv
    else
        echo "使用现有虚拟环境"
    fi
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip > /dev/null

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "================================"
    echo "配置 Bot Token"
    echo "================================"
    echo "请从 @BotFather 获取你的 Bot Token"
    echo "Token 格式类似: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    echo ""
    read -p "请输入你的 Bot Token: " BOT_TOKEN

    if [ -z "$BOT_TOKEN" ]; then
        echo "❌ Token 不能为空"
        echo "你可以稍后手动创建 .env 文件"
    else
        cp .env.example .env
        sed -i.bak "s/your_bot_token_here/$BOT_TOKEN/" .env
        rm .env.bak
        echo "✓ .env 文件已创建"
    fi
else
    echo "✓ .env 文件已存在"
fi

# 创建数据目录
mkdir -p data/reports

echo ""
echo "================================"
echo "安装完成!"
echo "================================"
echo ""
echo "使用方法:"
echo "  1. 激活虚拟环境: source venv/bin/activate"
echo "  2. 运行 Bot:       python main.py"
echo ""
echo "如果还未配置 Bot Token，请编辑 .env 文件"
echo ""
