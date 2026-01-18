"""Configuration model"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Config:
    """配置管理类"""

    def __init__(self, config_file: Path = None):
        """初始化配置

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or Path("data/config.json")
        self.data = self._load_config()

    def _load_config(self) -> dict:
        """加载配置文件

        Returns:
            配置字典
        """
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_config()

    def _get_default_config(self) -> dict:
        """获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "groups": {},  # group_id: {"name": str, "members": {user_id: username}}
            "admin_users": [],  # 管理员用户ID列表
            "reminder_day": 5,  # 周五提醒 (0=周一, 6=周日)
            "reminder_hour": 17,  # 下午5点提醒
            "deadline_day": 0,  # 周一截止
            "deadline_hour": 10,  # 上午10点截止
            "report_keywords": ["周报", "#周报", "本周工作", "weekly report"]
        }

    def save(self):
        """保存配置到文件"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_groups(self) -> Dict:
        """获取所有群组配置

        Returns:
            群组配置字典
        """
        return self.data.get("groups", {})

    def get_group(self, group_id: int) -> Optional[dict]:
        """获取指定群组配置

        Args:
            group_id: 群组ID

        Returns:
            群组配置字典，不存在则返回 None
        """
        return self.data.get("groups", {}).get(str(group_id))

    def register_group(self, group_id: int, group_name: str):
        """注册新群组

        Args:
            group_id: 群组ID
            group_name: 群组名称
        """
        if str(group_id) not in self.data["groups"]:
            self.data["groups"][str(group_id)] = {
                "name": group_name,
                "members": {}
            }
            self.save()

    def add_member(self, group_id: int, user_id: int, username: str):
        """添加成员到群组

        Args:
            group_id: 群组ID
            user_id: 用户ID
            username: 用户名
        """
        group_id_str = str(group_id)
        if group_id_str in self.data["groups"]:
            self.data["groups"][group_id_str]["members"][str(user_id)] = username
            self.save()

    def remove_member(self, group_id: int, user_id: int):
        """从群组移除成员

        Args:
            group_id: 群组ID
            user_id: 用户ID
        """
        group_id_str = str(group_id)
        user_id_str = str(user_id)
        if group_id_str in self.data["groups"]:
            members = self.data["groups"][group_id_str]["members"]
            if user_id_str in members:
                del members[user_id_str]
                self.save()

    def get_report_keywords(self) -> List[str]:
        """获取周报关键词列表

        Returns:
            关键词列表
        """
        return self.data.get("report_keywords", ["周报", "#周报"])
