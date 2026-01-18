# WorkPilot 安装指南

本文档详细说明如何在不同环境中安装和部署 WorkPilot Telegram Bot。

## 目录

- [系统要求](#系统要求)
- [方法一: 使用安装脚本 (推荐)](#方法一-使用安装脚本-推荐)
- [方法二: 手动安装](#方法二-手动安装)
- [方法三: Docker 部署](#方法三-docker-部署)
- [方法四: systemd 服务 (Linux)](#方法四-systemd-服务-linux)
- [常见问题](#常见问题)

---

## 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Linux, macOS, Windows
- **网络**: 能够访问 Telegram API

---

## 方法一: 使用安装脚本 (推荐)

我们提供了自动安装脚本，可以快速完成环境配置。

### Linux / macOS

```bash
# 1. 克隆或下载项目
cd workpilot

# 2. 运行安装脚本
bash install.sh

# 3. 按照提示输入 Bot Token

# 4. 激活虚拟环境并运行
source venv/bin/activate
python main.py
```

### Windows

```powershell
# 1. 克隆或下载项目
cd workpilot

# 2. 运行安装脚本 (需要 PowerShell)
.\install.ps1

# 3. 按照提示输入 Bot Token

# 4. 激活虚拟环境并运行
.\venv\Scripts\Activate.ps1
python main.py
```

---

## 方法二: 手动安装

如果你想完全控制安装过程，可以手动执行以下步骤。

### 步骤 1: 创建 Python 虚拟环境

虚拟环境可以隔离项目依赖，避免与系统 Python 环境冲突。

**Linux / macOS:**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**Windows:**
```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (CMD)
venv\Scripts\activate.bat

# 激活虚拟环境 (PowerShell)
venv\Scripts\Activate.ps1
```

### 步骤 2: 安装依赖

```bash
# 升级 pip (可选但推荐)
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Bot Token
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中设置:

```env
TELEGRAM_BOT_TOKEN=你的_Bot_Token
```

### 步骤 4: 运行 Bot

```bash
python main.py
```

看到 "Bot 启动成功！" 消息表示运行正常。

---

## 方法三: Docker 部署

使用 Docker 可以避免环境配置问题，适合服务器部署。

### 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

### 部署步骤

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env  # 填入 Bot Token

# 2. 构建并启动容器
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止容器
docker-compose down

# 5. 重启容器
docker-compose restart
```

### Docker Compose 配置说明

`docker-compose.yml` 文件:

```yaml
version: '3.8'

services:
  workpilot:
    build: .
    container_name: workpilot-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./data:/app/data
```

---

## 方法四: systemd 服务 (Linux)

将 Bot 配置为系统服务，可以开机自启动并自动重启。

### 步骤 1: 创建服务文件

```bash
sudo nano /etc/systemd/system/workpilot-bot.service
```

### 步骤 2: 粘贴以下内容

```ini
[Unit]
Description=WorkPilot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/workpilot
Environment="TELEGRAM_BOT_TOKEN=your_bot_token_here"
ExecStart=/path/to/workpilot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**请修改以下内容:**
- `User`: 你的用户名
- `WorkingDirectory`: 项目实际路径
- `Environment`: 你的 Bot Token
- `ExecStart`: Python 解释器的完整路径

### 步骤 3: 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启动
sudo systemctl enable workpilot-bot

# 启动服务
sudo systemctl start workpilot-bot

# 查看服务状态
sudo systemctl status workpilot-bot

# 查看日志
sudo journalctl -u workpilot-bot -f

# 停止服务
sudo systemctl stop workpilot-bot

# 重启服务
sudo systemctl restart workpilot-bot
```

---

## 获取 Bot Token

在开始安装之前，你需要先创建一个 Telegram Bot 并获取 Token:

1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令
3. 按提示输入 Bot 名称
4. 获取 Bot Token (格式: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. 保存 Token，安装时需要使用

---

## 常见问题

### 1. Python 版本过低

**错误信息:**
```
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

**解决方案:**
```bash
# 检查 Python 版本
python3 --version

# 如果版本低于 3.9，请升级 Python
# macOS (使用 Homebrew):
brew install python@3.11

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.11
```

### 2. 虚拟环境激活失败

**Windows PowerShell 错误:**
```
无法加载文件 venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本
```

**解决方案:**
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 然后再激活虚拟环境
.\venv\Scripts\Activate.ps1
```

### 3. 依赖安装失败

**错误信息:**
```
error: Microsoft Visual C++ 14.0 is required...
```

**解决方案 (Windows):**
- 安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 或使用预编译的 wheel 包

### 4. Bot Token 无效

**错误信息:**
```
Unauthorized: invalid token
```

**解决方案:**
1. 检查 `.env` 文件中的 Token 是否正确
2. 确保没有多余的空格或引号
3. 重新从 @BotFather 获取 Token

### 5. Bot 没有响应

**排查步骤:**
1. 检查 Bot 是否运行中: `ps aux | grep python`
2. 查看日志是否有错误
3. 确认 Bot 已添加到群组
4. 在群组中发送 `/start` 初始化

### 6. 端口被占用

如果使用其他服务占用了相关资源，可以:
- 检查并停止冲突的服务
- 修改配置使用不同的端口

---

## 验证安装

安装完成后，可以通过以下步骤验证:

1. **检查 Bot 是否运行**
   ```bash
   # 查看进程
   ps aux | grep "python main.py"

   # 或查看日志
   tail -f bot.log
   ```

2. **在 Telegram 中测试**
   - 私聊 Bot，发送 `/start`
   - 将 Bot 添加到群组
   - 在群组中发送 `/start`
   - 发送 `/help` 查看命令列表

3. **测试提交周报**
   ```
   /submit 本周完成: 测试周报功能
   ```

---

## 更新 Bot

当有新版本时:

```bash
# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\Activate.ps1  # Windows

# 更新依赖
pip install --upgrade -r requirements.txt

# 重启 Bot
# 如果使用 systemd:
sudo systemctl restart workpilot-bot

# 如果使用 docker-compose:
docker-compose restart

# 如果直接运行:
# 先停止 (Ctrl+C)，再重新运行
python main.py
```

---

## 卸载

### 完全卸载

```bash
# 停止并删除 systemd 服务
sudo systemctl stop workpilot-bot
sudo systemctl disable workpilot-bot
sudo rm /etc/systemd/system/workpilot-bot.service
sudo systemctl daemon-reload

# 删除项目文件
rm -rf workpilot

# 删除虚拟环境 (如果在项目外)
rm -rf venv
```

---

## 技术支持

如果遇到问题:

1. 查看 [README.md](README.md) 了解基本用法
2. 检查日志文件排查错误
3. 提交 Issue 到项目仓库

---

## 下一步

安装完成后，请查看 [README.md](README.md) 了解如何使用 Bot 的各项功能。
