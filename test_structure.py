#!/usr/bin/env python3
"""
代码结构验证脚本
用于检查重构后的代码文件是否完整
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (缺失)")
        return False


def main():
    print("=" * 60)
    print("WorkPilot 代码结构验证")
    print("=" * 60)
    print()

    all_ok = True

    # 检查主入口
    print("1. 主入口文件:")
    all_ok &= check_file_exists("main.py", "主入口文件")
    all_ok &= check_file_exists(".env.example", "环境变量示例")
    print()

    # 检查配置文件
    print("2. 配置文件:")
    all_ok &= check_file_exists("requirements.txt", "依赖列表")
    all_ok &= check_file_exists("README.md", "项目说明")
    all_ok &= check_file_exists("docs/INSTALL.md", "安装指南")
    print()

    # 检查源代码结构
    print("3. 源代码结构 (src/):")
    all_ok &= check_file_exists("src/__init__.py", "src 包初始化")
    print()

    # 检查模型层
    print("4. 数据模型 (src/models/):")
    all_ok &= check_file_exists("src/models/__init__.py", "models 包初始化")
    all_ok &= check_file_exists("src/models/config.py", "配置模型")
    all_ok &= check_file_exists("src/models/report.py", "周报模型")
    print()

    # 检查服务层
    print("5. 业务逻辑 (src/services/):")
    all_ok &= check_file_exists("src/services/__init__.py", "services 包初始化")
    all_ok &= check_file_exists("src/services/bot_service.py", "Bot 核心服务")
    all_ok &= check_file_exists("src/services/report_service.py", "周报服务")
    all_ok &= check_file_exists("src/services/reminder_service.py", "提醒服务")
    print()

    # 检查处理器层
    print("6. 消息处理器 (src/handlers/):")
    all_ok &= check_file_exists("src/handlers/__init__.py", "handlers 包初始化")
    all_ok &= check_file_exists("src/handlers/commands.py", "命令处理器")
    all_ok &= check_file_exists("src/handlers/messages.py", "消息处理器")
    print()

    # 检查工具层
    print("7. 工具函数 (src/utils/):")
    all_ok &= check_file_exists("src/utils/__init__.py", "utils 包初始化")
    all_ok &= check_file_exists("src/utils/logger.py", "日志工具")
    all_ok &= check_file_exists("src/utils/time_utils.py", "时间工具")
    print()

    # 检查其他
    print("8. 其他组件:")
    all_ok &= check_file_exists("src/scheduler.py", "定时任务配置")
    all_ok &= check_file_exists("install.sh", "Linux/macOS 安装脚本")
    all_ok &= check_file_exists("install.ps1", "Windows 安装脚本")
    print()

    # 统计
    print("=" * 60)
    if all_ok:
        print("✓ 所有文件检查通过！代码结构完整。")
        print()
        print("下一步:")
        print("  1. 运行安装脚本: bash install.sh (Linux/macOS)")
        print("  2. 或运行: .\\install.ps1 (Windows)")
        print("  3. 或查看 docs/INSTALL.md 手动安装")
    else:
        print("✗ 部分文件缺失，请检查项目结构。")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
