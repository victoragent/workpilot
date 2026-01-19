"""
WorkPilot - Telegram 周报收集 Bot
主入口文件
"""

import os
import sys
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    # 尝试加载 .env 文件
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 已加载环境变量文件: {env_file}")
    else:
        print("⚠️  .env 文件不存在，将使用系统环境变量")
except ImportError:
    print("⚠️  python-dotenv 未安装，将使用系统环境变量")

from src.handlers.commands import (
    start,
    help_command,
    sync_members,
    register_member,
    unregister_member,
    submit_report,
    check_status,
    show_summary,
    send_reminder,
    export_report,
    list_members,
    exclude_user,
    include_user,
    list_excluded,
)
from src.handlers.messages import handle_message
from src.handlers.menu_setup import setup_menu_commands
from src.scheduler import setup_scheduled_jobs
from src.utils.logger import setup_logger


# 配置日志
logger = setup_logger(__name__)


def main():
    """主函数"""
    # 从环境变量获取 Bot Token
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        logger.error("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        print("错误: 请设置 TELEGRAM_BOT_TOKEN 环境变量")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        sys.exit(1)

    # 创建应用
    application = Application.builder().token(token).build()

    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sync", sync_members))
    application.add_handler(CommandHandler("register", register_member))
    application.add_handler(CommandHandler("unregister", unregister_member))
    application.add_handler(CommandHandler("submit", submit_report))
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("summary", show_summary))
    application.add_handler(CommandHandler("remind", send_reminder))
    application.add_handler(CommandHandler("export", export_report))
    application.add_handler(CommandHandler("members", list_members))
    application.add_handler(CommandHandler("exclude", exclude_user))
    application.add_handler(CommandHandler("include", include_user))
    application.add_handler(CommandHandler("excluded", list_excluded))

    # 添加消息处理器（检测周报关键词）
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    # 设置定时任务
    setup_scheduled_jobs(application)

    # 设置菜单命令
    async def post_init(application) -> None:
        """应用初始化后的回调"""
        await setup_menu_commands(application)

    application.post_init = post_init

    # 启动 Bot
    logger.info("Bot 启动中...")
    print("Bot 启动成功！按 Ctrl+C 停止")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
