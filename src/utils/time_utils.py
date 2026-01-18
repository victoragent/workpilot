"""Time utility functions"""

from datetime import datetime


def get_current_week() -> str:
    """获取当前周的标识 (格式: 2024-W01)

    Returns:
        当前周的标识字符串
    """
    now = datetime.now()
    return now.strftime("%Y-W%W")
