"""Message handlers for Telegram bot"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.services.bot_service import BotService
from src.services.report_service import ReportService
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


# 创建服务实例
bot_service = BotService()
report_service = ReportService(bot_service)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息，检测是否包含周报关键词

    Args:
        update: Telegram 更新对象
        context: 上下文对象
    """
    chat = update.effective_chat
    user = update.effective_user
    message = update.message

    if not message or not message.text:
        return

    if chat.type not in ['group', 'supergroup']:
        return

    text = message.text

    # 检查是否包含周报关键词
    is_report = report_service.check_if_report_message(text)

    if is_report and len(text) > 10:  # 确保有足够的内容
        # 自动注册成员
        bot_service.add_member(chat.id, user.id, user.full_name or user.username)

        # 保存周报
        bot_service.add_report(
            chat.id, user.id, user.full_name or user.username, text
        )

        await message.reply_text(
            f"✅ 检测到周报内容，已自动收录！\n"
            f"提交者: {user.full_name}"
        )
        logger.info(f"自动收录周报: {user.full_name} 在群 {chat.id}")


async def scheduled_reminder(context: ContextTypes.DEFAULT_TYPE):
    """定时提醒任务

    Args:
        context: 上下文对象
    """
    from ..services.reminder_service import ReminderService
    from ..services.bot_service import BotService

    bot = context.bot
    bot_service = BotService()
    reminder_service = ReminderService(bot_service)

    await reminder_service.send_reminder_to_all_groups(bot)
