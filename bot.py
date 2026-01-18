"""
Telegram 周报收集 Bot
功能：
1. 收集群成员周报
2. 自动提醒未提交周报的成员
3. 汇总周报并存储
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    JobQueue,
)
from telegram.constants import ParseMode

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 配置文件路径
DATA_DIR = Path("data")
CONFIG_FILE = DATA_DIR / "config.json"
REPORTS_DIR = DATA_DIR / "reports"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


class WeeklyReportBot:
    """周报收集 Bot 核心类"""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "groups": {},  # group_id: {"name": str, "members": {user_id: username}}
            "admin_users": [],  # 管理员用户ID列表
            "reminder_day": 5,  # 周五提醒 (0=周一, 6=周日)
            "reminder_hour": 17,  # 下午5点提醒
            "deadline_day": 0,  # 周一截止
            "deadline_hour": 10,  # 上午10点截止
            "report_keywords": ["周报", "#周报", "本周工作", "weekly report"]
        }
    
    def _save_config(self):
        """保存配置"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_current_week(self) -> str:
        """获取当前周的标识 (格式: 2024-W01)"""
        now = datetime.now()
        return now.strftime("%Y-W%W")
    
    def get_week_report_file(self, group_id: int, week: str = None) -> Path:
        """获取周报文件路径"""
        if week is None:
            week = self.get_current_week()
        group_dir = REPORTS_DIR / str(group_id)
        group_dir.mkdir(exist_ok=True)
        return group_dir / f"{week}.json"
    
    def load_week_reports(self, group_id: int, week: str = None) -> dict:
        """加载某周的周报数据"""
        file_path = self.get_week_report_file(group_id, week)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"week": week or self.get_current_week(), "reports": {}}
    
    def save_week_reports(self, group_id: int, data: dict, week: str = None):
        """保存周报数据"""
        file_path = self.get_week_report_file(group_id, week)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_report(self, group_id: int, user_id: int, username: str, content: str) -> bool:
        """添加周报"""
        week = self.get_current_week()
        data = self.load_week_reports(group_id, week)
        
        data["reports"][str(user_id)] = {
            "username": username,
            "content": content,
            "submitted_at": datetime.now().isoformat()
        }
        
        self.save_week_reports(group_id, data, week)
        logger.info(f"用户 {username} ({user_id}) 在群 {group_id} 提交了周报")
        return True
    
    def get_pending_members(self, group_id: int) -> List[dict]:
        """获取未提交周报的成员列表"""
        week = self.get_current_week()
        data = self.load_week_reports(group_id, week)
        submitted_ids = set(data["reports"].keys())
        
        group_config = self.config["groups"].get(str(group_id), {})
        members = group_config.get("members", {})
        
        pending = []
        for user_id, username in members.items():
            if user_id not in submitted_ids:
                pending.append({"user_id": int(user_id), "username": username})
        
        return pending
    
    def register_group(self, group_id: int, group_name: str):
        """注册群组"""
        if str(group_id) not in self.config["groups"]:
            self.config["groups"][str(group_id)] = {
                "name": group_name,
                "members": {}
            }
            self._save_config()
            logger.info(f"注册新群组: {group_name} ({group_id})")
    
    def add_member(self, group_id: int, user_id: int, username: str):
        """添加成员到需要提交周报的列表"""
        group_id_str = str(group_id)
        if group_id_str in self.config["groups"]:
            self.config["groups"][group_id_str]["members"][str(user_id)] = username
            self._save_config()
            logger.info(f"添加成员 {username} ({user_id}) 到群 {group_id}")
    
    def remove_member(self, group_id: int, user_id: int):
        """从周报列表中移除成员"""
        group_id_str = str(group_id)
        user_id_str = str(user_id)
        if group_id_str in self.config["groups"]:
            members = self.config["groups"][group_id_str]["members"]
            if user_id_str in members:
                del members[user_id_str]
                self._save_config()
                logger.info(f"移除成员 {user_id} 从群 {group_id}")
    
    def generate_summary(self, group_id: int, week: str = None) -> str:
        """生成周报汇总"""
        if week is None:
            week = self.get_current_week()
        
        data = self.load_week_reports(group_id, week)
        group_config = self.config["groups"].get(str(group_id), {})
        group_name = group_config.get("name", "未知群组")
        
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
        
        # 添加未提交列表
        pending = self.get_pending_members(group_id)
        if pending:
            summary += f"\n⚠️ **未提交周报的成员 ({len(pending)}人)**:\n"
            for member in pending:
                summary += f"- {member['username']}\n"
        
        return summary
    
    def export_to_markdown(self, group_id: int, week: str = None) -> Path:
        """导出周报为 Markdown 文件"""
        if week is None:
            week = self.get_current_week()
        
        data = self.load_week_reports(group_id, week)
        group_config = self.config["groups"].get(str(group_id), {})
        group_name = group_config.get("name", "未知群组")
        
        md_content = f"# {group_name} - {week} 周报汇总\n\n"
        md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"
        
        if data["reports"]:
            for user_id, report in data["reports"].items():
                md_content += f"## {report['username']}\n\n"
                md_content += f"**提交时间**: {report['submitted_at']}\n\n"
                md_content += f"{report['content']}\n\n"
                md_content += "---\n\n"
        
        # 保存文件
        export_dir = REPORTS_DIR / str(group_id) / "exports"
        export_dir.mkdir(exist_ok=True)
        export_file = export_dir / f"{week}_summary.md"
        
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return export_file


# 创建全局 bot 实例
report_bot = WeeklyReportBot()


# ============ Telegram 命令处理器 ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type in ['group', 'supergroup']:
        report_bot.register_group(chat.id, chat.title)
        await update.message.reply_text(
            f"👋 你好！我是周报收集助手\n\n"
            f"已注册群组: {chat.title}\n\n"
            f"**可用命令:**\n"
            f"/register - 注册为需要提交周报的成员\n"
            f"/unregister - 取消注册\n"
            f"/submit - 提交周报 (或直接发送包含「周报」的消息)\n"
            f"/status - 查看本周周报提交状态\n"
            f"/summary - 查看本周周报汇总\n"
            f"/remind - 手动触发提醒\n"
            f"/export - 导出周报为文件\n"
            f"/help - 查看帮助"
        )
    else:
        await update.message.reply_text(
            "请将我添加到工作群中使用！\n"
            "添加后发送 /start 初始化。"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = """
📖 **周报收集 Bot 使用指南**

**成员命令:**
• `/register` - 注册为需要提交周报的成员
• `/unregister` - 取消注册
• `/submit` - 提交周报
• `/status` - 查看提交状态
• `/mystatus` - 查看个人提交状态

**管理命令:**
• `/summary` - 查看周报汇总
• `/remind` - 发送提醒
• `/export` - 导出周报文件
• `/members` - 查看成员列表

**提交周报方式:**
1. 使用 `/submit` 命令后跟周报内容
2. 直接发送包含「周报」关键词的消息

**示例:**
```
/submit
本周完成:
1. 完成XX功能开发
2. 修复XX bug

下周计划:
1. 开始YY模块
```

或直接发送:
```
#周报
本周完成: ...
```
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def register_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """注册成员"""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    report_bot.add_member(chat.id, user.id, user.full_name or user.username)
    await update.message.reply_text(
        f"✅ {user.full_name} 已注册！\n"
        f"每周请记得提交周报哦~"
    )


async def unregister_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消注册"""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    report_bot.remove_member(chat.id, user.id)
    await update.message.reply_text(f"✅ {user.full_name} 已取消注册")


async def submit_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """提交周报"""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    # 获取周报内容
    content = ' '.join(context.args) if context.args else None
    
    if not content:
        await update.message.reply_text(
            "请在命令后附上周报内容，例如:\n"
            "/submit 本周完成了XX，下周计划YY"
        )
        return
    
    # 自动注册成员（如果还没注册）
    report_bot.add_member(chat.id, user.id, user.full_name or user.username)
    
    # 保存周报
    report_bot.add_report(chat.id, user.id, user.full_name or user.username, content)
    
    await update.message.reply_text(
        f"✅ 周报已收到！\n"
        f"提交者: {user.full_name}\n"
        f"周次: {report_bot.get_current_week()}"
    )


async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看提交状态"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    week = report_bot.get_current_week()
    data = report_bot.load_week_reports(chat.id, week)
    pending = report_bot.get_pending_members(chat.id)
    
    submitted_count = len(data["reports"])
    total_members = len(report_bot.config["groups"].get(str(chat.id), {}).get("members", {}))
    
    status_text = f"📊 **{week} 周报状态**\n\n"
    status_text += f"已提交: {submitted_count}/{total_members}\n\n"
    
    if data["reports"]:
        status_text += "✅ **已提交:**\n"
        for user_id, report in data["reports"].items():
            status_text += f"  • {report['username']}\n"
    
    if pending:
        status_text += f"\n⏳ **未提交 ({len(pending)}人):**\n"
        for member in pending:
            status_text += f"  • {member['username']}\n"
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示周报汇总"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    summary = report_bot.generate_summary(chat.id)
    
    # 如果内容太长，分段发送
    if len(summary) > 4000:
        parts = [summary[i:i+4000] for i in range(0, len(summary), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)


async def send_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送提醒"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    pending = report_bot.get_pending_members(chat.id)
    
    if not pending:
        await update.message.reply_text("🎉 所有人都已提交周报！")
        return
    
    # 构建提醒消息，@未提交的成员
    reminder_text = "⏰ **周报提醒**\n\n以下同学还未提交本周周报，请尽快提交：\n\n"
    
    mentions = []
    for member in pending:
        # 使用 Markdown 格式的 mention
        mentions.append(f"[{member['username']}](tg://user?id={member['user_id']})")
    
    reminder_text += " ".join(mentions)
    reminder_text += "\n\n请使用 /submit 命令提交周报，或发送包含「周报」的消息。"
    
    await update.message.reply_text(reminder_text, parse_mode=ParseMode.MARKDOWN)


async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """导出周报"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    week = context.args[0] if context.args else None
    export_file = report_bot.export_to_markdown(chat.id, week)
    
    await update.message.reply_document(
        document=open(export_file, 'rb'),
        filename=export_file.name,
        caption=f"📄 周报汇总文件 ({week or report_bot.get_current_week()})"
    )


async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出成员"""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return
    
    group_config = report_bot.config["groups"].get(str(chat.id), {})
    members = group_config.get("members", {})
    
    if not members:
        await update.message.reply_text("暂无注册成员，请使用 /register 注册")
        return
    
    text = f"👥 **已注册成员 ({len(members)}人)**\n\n"
    for user_id, username in members.items():
        text += f"• {username}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息，检测是否包含周报关键词"""
    chat = update.effective_chat
    user = update.effective_user
    message = update.message
    
    if not message or not message.text:
        return
    
    if chat.type not in ['group', 'supergroup']:
        return
    
    text = message.text
    keywords = report_bot.config.get("report_keywords", ["周报", "#周报"])
    
    # 检查是否包含周报关键词
    is_report = any(keyword in text for keyword in keywords)
    
    if is_report and len(text) > 10:  # 确保有足够的内容
        # 自动注册成员
        report_bot.add_member(chat.id, user.id, user.full_name or user.username)
        
        # 保存周报
        report_bot.add_report(chat.id, user.id, user.full_name or user.username, text)
        
        await message.reply_text(
            f"✅ 检测到周报内容，已自动收录！\n"
            f"提交者: {user.full_name}"
        )


async def scheduled_reminder(context: ContextTypes.DEFAULT_TYPE):
    """定时提醒任务"""
    bot = context.bot
    
    for group_id, group_config in report_bot.config["groups"].items():
        pending = report_bot.get_pending_members(int(group_id))
        
        if pending:
            reminder_text = "⏰ **自动提醒**\n\n以下同学还未提交本周周报：\n\n"
            
            mentions = []
            for member in pending:
                mentions.append(f"[{member['username']}](tg://user?id={member['user_id']})")
            
            reminder_text += " ".join(mentions)
            reminder_text += "\n\n请尽快提交周报！"
            
            try:
                await bot.send_message(
                    chat_id=int(group_id),
                    text=reminder_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"已向群 {group_id} 发送提醒")
            except Exception as e:
                logger.error(f"发送提醒失败: {e}")


def setup_scheduled_jobs(application: Application):
    """设置定时任务"""
    job_queue = application.job_queue
    
    # 每周五下午5点提醒
    # 注意: time 参数使用 UTC 时间，需要根据你的时区调整
    from datetime import time
    reminder_time = time(hour=9, minute=0)  # UTC 9:00 = 北京时间 17:00
    
    job_queue.run_daily(
        scheduled_reminder,
        time=reminder_time,
        days=(4,),  # 周五 (0=周一, 4=周五)
        name="friday_reminder"
    )
    
    # 周一上午再提醒一次
    deadline_time = time(hour=1, minute=0)  # UTC 1:00 = 北京时间 9:00
    job_queue.run_daily(
        scheduled_reminder,
        time=deadline_time,
        days=(0,),  # 周一
        name="monday_reminder"
    )
    
    logger.info("定时任务已设置")


def main():
    """主函数"""
    # 从环境变量获取 Bot Token
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("请设置 TELEGRAM_BOT_TOKEN 环境变量")
        print("错误: 请设置 TELEGRAM_BOT_TOKEN 环境变量")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # 创建应用
    application = Application.builder().token(token).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register_member))
    application.add_handler(CommandHandler("unregister", unregister_member))
    application.add_handler(CommandHandler("submit", submit_report))
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("summary", show_summary))
    application.add_handler(CommandHandler("remind", send_reminder))
    application.add_handler(CommandHandler("export", export_report))
    application.add_handler(CommandHandler("members", list_members))
    
    # 添加消息处理器（检测周报关键词）
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # 设置定时任务
    setup_scheduled_jobs(application)
    
    # 启动 Bot
    logger.info("Bot 启动中...")
    print("Bot 启动成功！按 Ctrl+C 停止")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
