"""Command handlers for Telegram bot"""

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.services.bot_service import BotService
from src.services.report_service import ReportService
from src.services.reminder_service import ReminderService
from src.utils.logger import setup_logger
from src.utils.time_utils import get_current_week


logger = setup_logger(__name__)


# 创建服务实例
bot_service = BotService()
report_service = ReportService(bot_service)
reminder_service = ReminderService(bot_service)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    chat = update.effective_chat
    user = update.effective_user

    if chat.type in ['group', 'supergroup']:
        # 注册群组
        bot_service.register_group(chat.id, chat.title)

        # 尝试获取群组成员列表
        try:
            # 获取群组成员（需要 Bot 是管理员）
            members = await context.bot.get_chat_administrators(chat.id)

            # 构建成员字典
            members_dict = {}
            for member in members:
                # 跳过 Bot 自己
                if member.user.id == context.bot.id:
                    continue
                # 包含所有管理员
                if member.user.full_name or member.user.username:
                    members_dict[member.user.id] = member.user.full_name or member.user.username

            # 如果成功获取了管理员，保存到配置
            if members_dict:
                bot_service.sync_members_from_group(chat.id, members_dict)
                member_count = len(members_dict)
        except Exception as e:
            logger.warning(f"无法获取群 {chat.id} 的成员列表: {e}")
            member_count = 0

        # 发送欢迎消息
        help_text = f"👋 你好！我是周报收集助手\n\n"
        help_text += f"已注册群组: {chat.title}\n\n"

        if member_count > 0:
            help_text += f"✅ 已自动添加 {member_count} 位管理员到周报名单\n\n"
        else:
            help_text += f"⚠️ 未获取到成员列表，请确保 Bot 是群管理员\n"
            help_text += f"或手动使用 /register 注册\n\n"

        help_text += f"**可用命令:**\n"
        help_text += f"/sync - 同步群组成员列表\n"
        help_text += f"/submit - 提交周报 (或直接发送包含「周报」的消息)\n"
        help_text += f"/status - 查看本周周报提交状态\n"
        help_text += f"/summary - 查看本周周报汇总\n"
        help_text += f"/remind - 手动触发提醒\n"
        help_text += f"/export - 导出周报为文件\n"
        help_text += f"/help - 查看帮助"

        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
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
• `/sync` - 同步群组成员列表（需要 Bot 是管理员）
• `/unregister` - 取消注册（不需要提交周报）
• `/submit` - 提交周报
• `/status` - 查看提交状态

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

**说明:**
- Bot 会自动同步群组成员，无需手动注册
- 如需退出周报名单，使用 `/unregister`
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def sync_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """同步群组成员"""
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    try:
        # 获取群组成员（需要 Bot 是管理员）
        members = await context.bot.get_chat_administrators(chat.id)

        # 构建成员字典
        members_dict = {}
        for member in members:
            # 跳过 Bot 自己
            if member.user.id == context.bot.id:
                continue
            # 包含所有管理员
            if member.user.full_name or member.user.username:
                members_dict[member.user.id] = member.user.full_name or member.user.username

        # 保存到配置
        bot_service.sync_members_from_group(chat.id, members_dict)

        await update.message.reply_text(
            f"✅ 已同步 {len(members_dict)} 位成员\n"
            f"他们现在需要提交周报了！"
        )
    except Exception as e:
        logger.error(f"同步成员失败: {e}")
        await update.message.reply_text(
            f"❌ 同步失败: {str(e)}\n\n"
            f"请确保 Bot 是群管理员"
        )


async def register_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """注册成员（保留用于兼容）"""
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    bot_service.add_member(chat.id, user.id, user.full_name or user.username)
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

    bot_service.remove_member(chat.id, user.id)
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
    bot_service.add_member(chat.id, user.id, user.full_name or user.username)

    # 保存周报
    bot_service.add_report(chat.id, user.id, user.full_name or user.username, content)

    await update.message.reply_text(
        f"✅ 周报已收到！\n"
        f"提交者: {user.full_name}\n"
        f"周次: {get_current_week()}"
    )


async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看提交状态"""
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    status_text = report_service.get_status_text(chat.id)
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示周报汇总"""
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    summary = report_service.get_summary_text(chat.id)

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

    pending = bot_service.get_pending_members(chat.id)

    if not pending:
        await update.message.reply_text("🎉 所有人都已提交周报！")
        return

    reminder_text = reminder_service._build_reminder_text(pending)

    await update.message.reply_text(reminder_text, parse_mode=ParseMode.MARKDOWN)


async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """导出周报"""
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    week = context.args[0] if context.args else None
    export_file = report_service.get_export_file(chat.id, week)

    await update.message.reply_document(
        document=open(export_file, 'rb'),
        filename=export_file.name,
        caption=f"📄 周报汇总文件 ({week or get_current_week()})"
    )


async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出成员"""
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("请在群组中使用此命令")
        return

    text = report_service.get_members_text(chat.id)
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def exclude_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """排除用户（不需要提交周报）"""
    chat = update.effective_chat
    user = update.effective_user

    # 只有回复消息时才能获取到要排除的用户
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text(
            "请回复要排除的用户消息，然后使用此命令\n"
            "例如: 用户发送消息后，你回复该消息并发送 /exclude"
        )
        return

    target_user = update.message.reply_to_message.from_user

    # 添加到排除列表
    bot_service.config.add_excluded_user(target_user.id, target_user.full_name or target_user.username)

    # 从当前群组成员中移除
    bot_service.config.remove_member(chat.id, target_user.id)

    await update.message.reply_text(
        f"✅ {target_user.full_name} 已添加到排除列表\n"
        f"他们不再需要提交周报了"
    )


async def include_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """从排除列表移除用户（恢复需要提交周报）"""
    chat = update.effective_chat
    user = update.effective_user

    # 只有回复消息时才能获取到要恢复的用户
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text(
            "请回复要恢复的用户消息，然后使用此命令\n"
            "例如: 用户发送消息后，你回复该消息并发送 /include"
        )
        return

    target_user = update.message.reply_to_message.from_user

    # 从排除列表移除
    bot_service.config.remove_excluded_user(target_user.id)

    await update.message.reply_text(
        f"✅ {target_user.full_name} 已从排除列表移除\n"
        f"他们现在需要提交周报了"
    )


async def list_excluded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看排除列表"""
    excluded_users = bot_service.config.get_excluded_users()

    if not excluded_users:
        await update.message.reply_text("📋 排除列表为空，所有人都需要提交周报")
        return

    text = f"📋 **排除列表** ({len(excluded_users)}人)\n\n"
    text += "以下用户不需要提交周报:\n"
    for user_id, username in excluded_users.items():
        text += f"• {username} (ID: {user_id})\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
