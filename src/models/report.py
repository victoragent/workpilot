"""Weekly report model"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.time_utils import get_current_week


class WeeklyReport:
    """周报数据管理类"""

    def __init__(self, reports_dir: Path = None):
        """初始化周报管理

        Args:
            reports_dir: 周报存储目录
        """
        self.reports_dir = reports_dir or Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _get_group_dir(self, group_id: int) -> Path:
        """获取群组周报目录

        Args:
            group_id: 群组ID

        Returns:
            群组目录路径
        """
        group_dir = self.reports_dir / str(group_id)
        group_dir.mkdir(exist_ok=True)
        return group_dir

    def _get_report_file(self, group_id: int, week: str = None) -> Path:
        """获取周报文件路径

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            周报文件路径
        """
        if week is None:
            week = get_current_week()
        return self._get_group_dir(group_id) / f"{week}.json"

    def load_reports(self, group_id: int, week: str = None) -> dict:
        """加载某群的周报数据

        Args:
            group_id: 群组ID
            week: 周标识，默认为当前周

        Returns:
            周报数据字典
        """
        file_path = self._get_report_file(group_id, week)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"week": week or get_current_week(), "reports": {}}

    def save_reports(self, group_id: int, data: dict, week: str = None):
        """保存周报数据

        Args:
            group_id: 群组ID
            data: 周报数据
            week: 周标识，默认为当前周
        """
        file_path = self._get_report_file(group_id, week)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_report(self, group_id: int, user_id: int, username: str,
                   content: str, week: str = None) -> bool:
        """添加周报

        Args:
            group_id: 群组ID
            user_id: 用户ID
            username: 用户名
            content: 周报内容
            week: 周标识，默认为当前周

        Returns:
            是否添加成功
        """
        if week is None:
            week = get_current_week()
        data = self.load_reports(group_id, week)

        data["reports"][str(user_id)] = {
            "username": username,
            "content": content,
            "submitted_at": datetime.now().isoformat()
        }

        self.save_reports(group_id, data, week)
        return True

    def get_pending_members(self, group_id: int,
                           members: Dict[str, str]) -> List[dict]:
        """获取未提交周报的成员列表

        Args:
            group_id: 群组ID
            members: 成员字典 {user_id: username}

        Returns:
            未提交成员列表
        """
        data = self.load_reports(group_id)
        submitted_ids = set(data["reports"].keys())

        pending = []
        for user_id, username in members.items():
            if user_id not in submitted_ids:
                pending.append({"user_id": int(user_id), "username": username})

        return pending

    def generate_summary(self, group_id: int, group_name: str,
                        week: str = None, pending_members: List[dict] = None) -> str:
        """生成周报汇总文本

        Args:
            group_id: 群组ID
            group_name: 群组名称
            week: 周标识，默认为当前周
            pending_members: 未提交成员列表

        Returns:
            周报汇总文本
        """
        if week is None:
            week = get_current_week()

        data = self.load_reports(group_id, week)

        summary = f"📊 **{group_name} - {week} 周报汇总**\n"
        summary += f"{'=' * 40}\n\n"

        if not data["reports"]:
            summary += "暂无周报提交\n"
        else:
            for user_id, report in data["reports"].items():
                summary += f"👤 **{report['username']}**\n"
                summary += f"提交时间: {report['submitted_at']}\n"
                summary += f"内容:\n{report['content']}\n"
                summary += f"{'-' * 30}\n\n"

        if pending_members:
            summary += f"\n⚠️ **未提交周报的成员 ({len(pending_members)}人)**:\n"
            for member in pending_members:
                summary += f"- {member['username']}\n"

        return summary

    def export_to_markdown(self, group_id: int, group_name: str,
                         week: str = None) -> Path:
        """导出周报为 Markdown 文件

        Args:
            group_id: 群组ID
            group_name: 群组名称
            week: 周标识，默认为当前周

        Returns:
            导出文件路径
        """
        if week is None:
            week = get_current_week()

        data = self.load_reports(group_id, week)

        md_content = f"# {group_name} - {week} 周报汇总\n\n"
        md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"

        if data["reports"]:
            for user_id, report in data["reports"].items():
                md_content += f"## {report['username']}\n\n"
                md_content += f"**提交时间**: {report['submitted_at']}\n\n"
                md_content += f"{report['content']}\n\n"
                md_content += "---\n\n"

        export_dir = self._get_group_dir(group_id) / "exports"
        export_dir.mkdir(exist_ok=True)
        export_file = export_dir / f"{week}_summary.md"

        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return export_file
