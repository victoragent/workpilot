"""Bot service - Main business logic"""

import logging
from typing import Dict

from src.models.config import Config
from src.models.report import WeeklyReport
from src.utils.logger import setup_logger
from src.utils.time_utils import get_current_week


logger = setup_logger(__name__)


class BotService:
    """Bot 核心服务类，整合配置和周报管理"""

    def __init__(self, config: Config = None, report_manager: WeeklyReport = None):
        """初始化 Bot 服务

        Args:
            config: 配置管理实例
            report_manager: 周报管理实例
        """
        self.config = config or Config()
        self.report_manager = report_manager or WeeklyReport()

    def register_group(self, group_id: int, group_name: str) -> bool:
        """注册群组

        Args:
            group_id: 群组ID
            group_name: 群组名称

        Returns:
            是否注册成功
        """
        self.config.register_group(group_id, group_name)
        logger.info(f"注册新群组: {group_name} ({group_id})")
        return True

    def add_member(self, group_id: int, user_id: int, username: str):
        """添加成员

        Args:
            group_id: 群组ID
            user_id: 用户ID
            username: 用户名
        """
        self.config.add_member(group_id, user_id, username)
        logger.info(f"添加成员 {username} ({user_id}) 到群 {group_id}")

    def remove_member(self, group_id: int, user_id: int):
        """移除成员

        Args:
            group_id: 群组ID
            user_id: 用户ID
        """
        self.config.remove_member(group_id, user_id)
        logger.info(f"移除成员 {user_id} 从群 {group_id}")

    def add_report(self, group_id: int, user_id: int,
                   username: str, content: str) -> bool:
        """添加周报

        Args:
            group_id: 群组ID
            user_id: 用户ID
            username: 用户名
            content: 周报内容

        Returns:
            是否添加成功
        """
        success = self.report_manager.add_report(
            group_id, user_id, username, content
        )
        if success:
            logger.info(f"用户 {username} ({user_id}) 在群 {group_id} 提交了周报")
        return success

    def get_pending_members(self, group_id: int) -> list:
        """获取未提交成员

        Args:
            group_id: 群组ID

        Returns:
            未提交成员列表
        """
        group_config = self.config.get_group(group_id) or {}
        members = group_config.get("members", {})
        return self.report_manager.get_pending_members(group_id, members)

    def get_group_members(self, group_id: int) -> Dict[str, str]:
        """获取群组成员

        Args:
            group_id: 群组ID

        Returns:
            成员字典 {user_id: username}
        """
        group_config = self.config.get_group(group_id) or {}
        return group_config.get("members", {})

    def generate_summary(self, group_id: int, week: str = None) -> str:
        """生成周报汇总

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            汇总文本
        """
        group_config = self.config.get_group(group_id) or {}
        group_name = group_config.get("name", "未知群组")
        pending_members = self.get_pending_members(group_id)

        return self.report_manager.generate_summary(
            group_id, group_name, week, pending_members
        )

    def get_report_stats(self, group_id: int, week: str = None) -> dict:
        """获取周报统计信息

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            统计信息字典
        """
        data = self.report_manager.load_reports(group_id, week)
        members = self.get_group_members(group_id)

        return {
            "week": week or get_current_week(),
            "submitted": len(data["reports"]),
            "total": len(members),
            "reports": data["reports"]
        }

    def export_report(self, group_id: int, week: str = None):
        """导出周报

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            导出文件路径
        """
        group_config = self.config.get_group(group_id) or {}
        group_name = group_config.get("name", "未知群组")

        return self.report_manager.export_to_markdown(
            group_id, group_name, week
        )

    def get_report_keywords(self) -> list:
        """获取周报关键词

        Returns:
            关键词列表
        """
        return self.config.get_report_keywords()

    def get_all_groups(self) -> Dict:
        """获取所有群组配置

        Returns:
            所有群组配置
        """
        return self.config.get_groups()
