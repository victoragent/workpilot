"""Scheduler configuration for automated tasks"""

import logging
from datetime import time

from telegram.ext import Application

from ..handlers.messages import scheduled_reminder
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


def setup_scheduled_jobs(application: Application):
    """设置定时任务

    Args:
        application: Telegram Application 实例
    """
    job_queue = application.job_queue

    # 每周五下午5点提醒 (北京时间 17:00 = UTC 09:00)
    reminder_time = time(hour=9, minute=0)

    job_queue.run_daily(
        scheduled_reminder,
        time=reminder_time,
        days=(4,),  # 周五 (0=周一, 4=周五)
        name="friday_reminder"
    )

    # 周一上午再提醒一次 (北京时间 09:00 = UTC 01:00)
    deadline_time = time(hour=1, minute=0)
    job_queue.run_daily(
        scheduled_reminder,
        time=deadline_time,
        days=(0,),  # 周一
        name="monday_reminder"
    )

    logger.info("定时任务已设置")
