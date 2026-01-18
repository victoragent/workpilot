# Telegram 周报收集 Bot

一个帮助团队收集、管理和汇总周报的 Telegram Bot。

## ✨ 功能特点

- **自动收集周报**: 识别包含「周报」关键词的消息，自动收录
- **提醒催报**: 定时提醒未提交周报的成员，支持 @mention
- **多群支持**: 一个 Bot 可以服务多个工作群
- **周报汇总**: 自动汇总并支持导出为 Markdown 文件
- **数据持久化**: 周报数据以 JSON 格式存储，方便管理

## 🚀 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新 Bot
3. 按提示设置 Bot 名称
4. 获取 Bot Token (格式类似: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. 部署 Bot

#### 方式一: 本地运行 (使用虚拟环境)

```bash
# 克隆/下载项目
cd workpilot

# 创建 Python 虚拟环境 (推荐使用 venv)
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Bot Token
nano .env  # 或使用其他编辑器

# 运行 Bot
python main.py
```

#### 方式二: Docker 部署 (推荐)

```bash
# 克隆/下载项目
cd workpilot

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Bot Token
nano .env

# 使用 docker-compose 启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 方式四: 使用 systemd (Linux 服务器)

创建服务文件 `/etc/systemd/system/weekly-report-bot.service`:

```ini
[Unit]
Description=Telegram Weekly Report Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/workpilot
Environment=TELEGRAM_BOT_TOKEN=your_token_here
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable workpilot-bot
sudo systemctl start workpilot-bot
```

### 3. 配置群组

1. 将 Bot 添加到你的工作群
2. 设置 Bot 为群管理员（可选，用于更好的 @mention 功能）
3. 在群中发送 `/start` 初始化

## 📖 命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 初始化 Bot，注册群组 |
| `/help` | 查看帮助信息 |
| `/register` | 注册为需要提交周报的成员 |
| `/unregister` | 取消注册 |
| `/submit <内容>` | 提交周报 |
| `/status` | 查看本周提交状态 |
| `/summary` | 查看周报汇总 |
| `/remind` | 手动发送提醒 |
| `/export [周次]` | 导出周报为文件 |
| `/members` | 查看已注册成员列表 |

## 💡 使用示例

### 提交周报

**方式一**: 使用命令
```
/submit
本周完成:
1. 完成用户模块开发
2. 修复登录 bug

下周计划:
1. 开始支付模块
2. 编写单元测试
```

**方式二**: 直接发送 (包含关键词)
```
#周报

本周工作:
- 完成 API 接口开发
- Code Review

遇到的问题:
- 数据库性能问题

下周计划:
- 性能优化
```

### 查看状态
```
/status
```
输出:
```
📊 2024-W03 周报状态

已提交: 3/5

✅ 已提交:
  • 张三
  • 李四
  • 王五

⏳ 未提交 (2人):
  • 赵六
  • 钱七
```

### 发送提醒
```
/remind
```
输出:
```
⏰ 周报提醒

以下同学还未提交本周周报，请尽快提交：

@赵六 @钱七

请使用 /submit 命令提交周报，或发送包含「周报」的消息。
```

## ⚙️ 配置说明

配置文件位于 `data/config.json`，可以手动编辑:

```json
{
  "groups": {
    "群ID": {
      "name": "群名称",
      "members": {
        "用户ID": "用户名"
      }
    }
  },
  "reminder_day": 5,       // 提醒日 (0=周一, 5=周六)
  "reminder_hour": 17,     // 提醒时间 (小时)
  "deadline_day": 0,       // 截止日
  "deadline_hour": 10,     // 截止时间
  "report_keywords": ["周报", "#周报", "本周工作", "weekly report"]
}
```

## 📁 数据存储

```
data/
├── config.json          # 配置文件
└── reports/
    └── {group_id}/
        ├── 2024-W01.json    # 每周数据
        ├── 2024-W02.json
        └── exports/
            └── 2024-W01_summary.md  # 导出文件
```

## 🔧 自定义开发

### 项目结构

```
workpilot/
├── src/
│   ├── __init__.py
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── config.py       # 配置管理
│   │   └── report.py       # 周报数据模型
│   ├── handlers/           # Telegram 消息处理器
│   │   ├── __init__.py
│   │   ├── commands.py     # 命令处理器
│   │   └── messages.py     # 消息处理器
│   ├── services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── bot_service.py      # Bot 核心服务
│   │   ├── report_service.py   # 周报服务
│   │   └── reminder_service.py # 提醒服务
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py       # 日志配置
│   │   └── time_utils.py   # 时间工具
│   └── scheduler.py        # 定时任务配置
├── data/                   # 数据目录
│   ├── config.json        # 配置文件
│   └── reports/           # 周报数据
├── main.py                # 主入口文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 添加新功能

代码采用模块化设计，可以方便地扩展:

```python
# 1. 在 src/handlers/commands.py 添加新命令
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """我的新命令"""
    # 你的逻辑
    await update.message.reply_text("Hello!")

# 2. 在 main.py 注册命令
application.add_handler(CommandHandler("mycommand", my_command))
```

### 修改提醒时间

在 `src/scheduler.py` 中修改定时任务配置:

```python
# 修改提醒时间和星期
reminder_time = time(hour=9, minute=0)  # UTC 时间
job_queue.run_daily(
    scheduled_reminder,
    time=reminder_time,
    days=(4,),  # 0=周一, 4=周五
    name="friday_reminder"
)
```

## 🐛 常见问题

**Q: Bot 没有响应?**
- 检查 Token 是否正确
- 确认 Bot 已添加到群组
- 查看日志确认是否有报错

**Q: @mention 不生效?**
- 确保 Bot 是群管理员
- 用户需要先通过 `/register` 注册

**Q: 如何查看历史周报?**
- 使用 `/export 2024-W01` 导出指定周的周报

更多详细文档请查看 [docs/](docs/) 目录。

## 📄 License

MIT License
