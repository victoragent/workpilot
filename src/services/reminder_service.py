"""Reminder service - Handle scheduled reminders"""

import logging
from typing import List

from telegram import Bot
from telegram.constants import ParseMode

from src.services.bot_service import BotService
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class ReminderService:
    """提醒服务类"""

    def __init__(self, bot_service: BotService):
        """初始化提醒服务

        Args:
            bot_service: Bot 服务实例
        """
        self.bot_service = bot_service

    async def send_reminder_to_group(self, bot: Bot, group_id: int):
        """向指定群组发送提醒

        Args:
            bot: Telegram Bot 实例
            group_id: 群组ID
        """
        pending = self.bot_service.get_pending_members(group_id)

        if not pending:
            logger.info(f"群 {group_id} 所有人都已提交周报")
            return

        reminder_text = self._build_reminder_text(pending)

        try:
            await bot.send_message(
                chat_id=group_id,
                text=reminder_text,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"已向群 {group_id} 发送提醒")
        except Exception as e:
            logger.error(f"发送提醒失败 (群 {group_id}): {e}")

    async def send_reminder_to_all_groups(self, bot: Bot):
        """向所有群组发送提醒

        Args:
            bot: Telegram Bot 实例
        """
        groups = self.bot_service.get_all_groups()

        for group_id in groups.keys():
            await self.send_reminder_to_group(bot, int(group_id))

    def _build_reminder_text(self, pending_members: List[dict]) -> str:
        """构建提醒消息文本

        Args:
            pending_members: 未提交成员列表

        Returns:
            提醒消息文本
        """
        reminder_text = "⏰ **周报提醒**\n\n以下同学还未提交本周周报，请尽快提交：\n\n"

        mentions = []
        for member in pending_members:
            # 使用 Markdown 格式的 mention
            mentions.append(
                f"[{member['username']}](tg://user?id={member['user_id']})"
            )

        reminder_text += " ".join(mentions)
        reminder_text += "\n\n请使用 /submit 命令提交周报，或发送包含「周报」的消息。"

        return reminder_text

    def build_auto_reminder_text(self, pending_members: List[dict]) -> str:
        """构建自动提醒消息文本

        Args:
            pending_members: 未提交成员列表

        Returns:
            自动提醒消息文本
        """
        reminder_text = "⏰ **自动提醒**\n\n以下同学还未提交本周周报：\n\n"

        mentions = []
        for member in pending_members:
            mentions.append(
                f"[{member['username']}](tg://user?id={member['user_id']})"
            )

        reminder_text += " ".join(mentions)
        reminder_text += "\n\n请尽快提交周报！"

        return reminder_text
