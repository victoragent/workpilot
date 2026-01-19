"""Bot menu button setup"""

import logging
from telegram import BotCommand
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def setup_menu_commands(application):
    """设置 Bot 菜单按钮和命令列表

    Args:
        application: Telegram Application 实例
    """
    try:
        # 定义命令列表
        commands = [
            BotCommand("start", "🚀 开始使用"),
            BotCommand("help", "📖 查看帮助"),
            BotCommand("sync", "🔄 同步群组成员"),
            BotCommand("submit", "✍️ 提交周报"),
            BotCommand("status", "📊 查看提交状态"),
            BotCommand("summary", "📑 查看周报汇总"),
            BotCommand("remind", "⏰ 发送提醒"),
            BotCommand("export", "📤 导出周报"),
            BotCommand("members", "👥 查看成员列表"),
        ]

        # 设置命令列表（所有聊天）
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot 命令列表已设置")

    except Exception as e:
        logger.error(f"❌ 设置命令列表失败: {e}")


def get_menu_commands_description():
    """获取命令列表描述（用于文档）

    Returns:
        命令描述字典
    """
    return {
        "start": "开始使用 Bot，初始化群组",
        "help": "查看使用帮助和命令列表",
        "sync": "同步群组成员列表（需要 Bot 是管理员）",
        "submit": "提交本周周报",
        "status": "查看本周周报提交状态",
        "summary": "查看本周所有周报汇总",
        "remind": "手动提醒未提交成员",
        "export": "导出周报为 Markdown 文件",
        "members": "查看已注册成员列表",
    }
