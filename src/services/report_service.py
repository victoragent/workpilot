"""Report service - Report related operations"""

import logging
from pathlib import Path

from telegram.constants import ParseMode

from src.services.bot_service import BotService
from src.utils.logger import setup_logger
from src.utils.time_utils import get_current_week


logger = setup_logger(__name__)


class ReportService:
    """周报服务类"""

    def __init__(self, bot_service: BotService):
        """初始化周报服务

        Args:
            bot_service: Bot 服务实例
        """
        self.bot_service = bot_service

    def get_status_text(self, group_id: int, week: str = None) -> str:
        """获取状态文本

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            状态文本
        """
        if week is None:
            week = get_current_week()

        stats = self.bot_service.get_report_stats(group_id, week)
        pending_members = self.bot_service.get_pending_members(group_id)

        status_text = f"📊 **{week} 周报状态**\n\n"
        status_text += f"已提交: {stats['submitted']}/{stats['total']}\n\n"

        if stats['reports']:
            status_text += "✅ **已提交:**\n"
            for user_id, report in stats['reports'].items():
                status_text += f"  • {report['username']}\n"

        if pending_members:
            status_text += f"\n⏳ **未提交 ({len(pending_members)}人):**\n"
            for member in pending_members:
                status_text += f"  • {member['username']}\n"

        return status_text

    def get_summary_text(self, group_id: int, week: str = None) -> str:
        """获取汇总文本

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            汇总文本
        """
        return self.bot_service.generate_summary(group_id, week)

    def get_members_text(self, group_id: int) -> str:
        """获取成员列表文本

        Args:
            group_id: 群组ID

        Returns:
            成员列表文本
        """
        members = self.bot_service.get_group_members(group_id)

        if not members:
            return "暂无注册成员，请使用 /register 注册"

        text = f"👥 **已注册成员 ({len(members)}人)**\n\n"
        for user_id, username in members.items():
            text += f"• {username}\n"

        return text

    def get_export_file(self, group_id: int, week: str = None) -> Path:
        """获取导出文件路径

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            导出文件路径
        """
        return self.bot_service.export_report(group_id, week)

    def check_if_report_message(self, text: str) -> bool:
        """检查消息是否包含周报关键词

        Args:
            text: 消息文本

        Returns:
            是否是周报消息
        """
        keywords = self.bot_service.get_report_keywords()
        return any(keyword in text for keyword in keywords)
