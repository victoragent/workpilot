# WorkPilot Bot - 服务器部署指南

本文档详细说明如何在 Linux 服务器上部署和管理 WorkPilot Bot。

## 目录

- [方法一: 使用启动脚本 (推荐)](#方法一-使用启动脚本-推荐)
- [方法二: 使用 systemd 服务 (推荐生产环境)](#方法二-使用-systemd-服务-推荐生产环境)
- [方法三: 使用 Screen/Tmux](#方法三-使用-screentmux)
- [方法四: 使用 Supervisor](#方法四-使用-supervisor)
- [常用操作](#常用操作)

---

## 方法一: 使用启动脚本 (推荐)

最简单的方式，适合快速部署和测试。

### 1. 上传项目到服务器

```bash
# 使用 scp 上传
scp -r workpilot/ user@server:/home/user/

# 或使用 git clone
git clone https://github.com/victoragent/workpilot.git
cd workpilot
```

### 2. 安装依赖

```bash
# 运行安装脚本
bash install.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件
nano .env

# 添加 Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. 后台启动 Bot

```bash
# 启动 Bot
./start.sh

# 查看状态
./status.sh

# 查看日志
tail -f logs/workpilot.log

# 停止 Bot
./stop.sh

# 重启 Bot
./restart.sh
```

### 脚本说明

**start.sh** - 启动 Bot
- 自动检查虚拟环境和配置
- 后台运行 Bot
- 保存 PID 到 `workpilot.pid`
- 日志输出到 `logs/workpilot.log`

**stop.sh** - 停止 Bot
- 读取 PID 并停止进程
- 清理 PID 文件

**status.sh** - 查看状态
- 显示运行状态
- 显示资源使用情况
- 显示最近的日志

**restart.sh** - 重启 Bot
- 先停止再启动

---

## 方法二: 使用 systemd 服务 (推荐生产环境)

systemd 是 Linux 的标准服务管理器，可以自动重启、开机自启。

### 1. 创建服务文件

```bash
# 复制服务文件模板
cp workpilot.service /tmp/workpilot.service

# 编辑服务文件，修改以下内容:
nano /tmp/workpilot.service
```

**需要修改的内容:**
- `User=` - 你的用户名
- `Group=` - 你的组名
- `WorkingDirectory=` - 项目实际路径
- `Environment="PATH=..."` - 虚拟环境路径
- `EnvironmentFile=` - .env 文件路径
- `ExecStart=` - Python 解释器路径
- `StandardOutput/Error=` - 日志文件路径

**示例配置:**
```ini
[Unit]
Description=WorkPilot Telegram Bot
After=network.target

[Service]
Type=simple
User=wally
Group=wally
WorkingDirectory=/home/wally/codebase/workpilot
Environment="PATH=/home/wally/codebase/workpilot/venv/bin"
EnvironmentFile=-/home/wally/codebase/workpilot/.env
ExecStart=/home/wally/codebase/workpilot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wally/codebase/workpilot/logs/workpilot.log
StandardError=append:/home/wally/codebase/workpilot/logs/workpilot.log

[Install]
WantedBy=multi-user.target
```

### 2. 安装服务

```bash
# 复制服务文件到 systemd 目录
sudo cp /tmp/workpilot.service /etc/systemd/system/workpilot.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable workpilot

# 启动服务
sudo systemctl start workpilot
```

### 3. 管理服务

```bash
# 查看服务状态
sudo systemctl status workpilot

# 启动服务
sudo systemctl start workpilot

# 停止服务
sudo systemctl stop workpilot

# 重启服务
sudo systemctl restart workpilot

# 查看实时日志
sudo journalctl -u workpilot -f

# 查看最近日志
sudo journalctl -u workpilot -n 100

# 查看完整日志
sudo journalctl -u workpilot
```

### 4. 服务管理技巧

**查看服务是否开机自启:**
```bash
sudo systemctl is-enabled workpilot
```

**禁用开机自启:**
```bash
sudo systemctl disable workpilot
```

**重新加载配置（修改服务文件后）:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart workpilot
```

---

## 方法三: 使用 Screen/Tmux

适合临时测试或手动管理。

### 使用 Screen

```bash
# 安装 screen
sudo apt install screen  # Ubuntu/Debian
sudo yum install screen  # CentOS/RHEL

# 创建会话并启动 Bot
screen -S workpilot
source venv/bin/activate
python main.py

# 分离会话: Ctrl+A, 然后按 D

# 重新连接会话
screen -r workpilot

# 查看所有会话
screen -ls

# 杀死会话
screen -S workpilot -X quit
```

### 使用 Tmux

```bash
# 安装 tmux
sudo apt install tmux  # Ubuntu/Debian
sudo yum install tmux  # CentOS/RHEL

# 创建会话并启动 Bot
tmux new -s workpilot
source venv/bin/activate
python main.py

# 分离会话: Ctrl+B, 然后按 D

# 重新连接会话
tmux attach -t workpilot

# 查看所有会话
tmux ls

# 杀死会话
tmux kill-session -t workpilot
```

---

## 方法四: 使用 Supervisor

Supervisor 是一个进程管理系统，适合管理多个进程。

### 1. 安装 Supervisor

```bash
# Ubuntu/Debian
sudo apt install supervisor

# CentOS/RHEL
sudo yum install supervisor

# 或使用 pip
pip install supervisor
```

### 2. 创建配置文件

```bash
sudo nano /etc/supervisor/conf.d/workpilot.conf
```

**配置内容:**
```ini
[program:workpilot]
command=/path/to/workpilot/venv/bin/python main.py
directory=/path/to/workpilot
user=your_username
autostart=true
autorestart=true
startsecs=10
startretries=3
redirect_stderr=true
stdout_logfile=/path/to/workpilot/logs/workpilot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### 3. 管理进程

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动进程
sudo supervisorctl start workpilot

# 停止进程
sudo supervisorctl stop workpilot

# 重启进程
sudo supervisorctl restart workpilot

# 查看状态
sudo supervisorctl status

# 查看日志
sudo supervisorctl tail workpilot

# 查看实时日志
sudo supervisorctl tail -f workpilot
```

---

## 常用操作

### 查看日志

```bash
# 使用启动脚本
tail -f logs/workpilot.log

# 使用 systemd
sudo journalctl -u workpilot -f

# 查看最近 100 行
tail -n 100 logs/workpilot.log

# 搜索关键词
grep "ERROR" logs/workpilot.log
```

### 监控资源使用

```bash
# 查看进程
ps aux | grep python

# 查看资源使用
top -p $(cat workpilot.pid)

# 实时监控
htop
```

### 设置日志轮转

防止日志文件过大：

```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/workpilot
```

**配置内容:**
```
/path/to/workpilot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### 防火墙配置

如果服务器有防火墙，需要确保允许出站连接：

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow out 443/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 故障排查

### Bot 无法启动

1. **检查虚拟环境**
   ```bash
   source venv/bin/activate
   python main.py  # 查看错误信息
   ```

2. **检查环境变量**
   ```bash
   cat .env
   ```

3. **检查依赖**
   ```bash
   pip list | grep telegram
   ```

4. **检查日志**
   ```bash
   tail -f logs/workpilot.log
   ```

### Bot 频繁重启

1. **检查 Token 是否正确**
2. **检查网络连接**
   ```bash
   curl -I https://api.telegram.org
   ```
3. **查看详细错误日志**
   ```bash
   journalctl -u workpilot -n 100
   ```

### 内存占用过高

1. **检查内存使用**
   ```bash
   ps aux | grep python
   ```

2. **设置内存限制（systemd）**
   ```ini
   [Service]
   MemoryLimit=256M
   ```

3. **添加定时重启**
   ```bash
   # 添加到 crontab
   0 3 * * * /path/to/workpilot/restart.sh
   ```

---

## 推荐方案

| 场景 | 推荐方案 |
|------|----------|
| 开发测试 | Screen/Tmux |
| 个人使用 | 启动脚本 (start.sh) |
| 生产环境 | systemd 服务 |
| 多进程管理 | Supervisor |

---

## 安全建议

1. **保护 .env 文件**
   ```bash
   chmod 600 .env
   ```

2. **使用专用用户运行 Bot**
   ```bash
   sudo useradd -r -s /bin/false workpilot
   ```

3. **限制文件权限**
   ```bash
   chmod -R 755 /path/to/workpilot
   chmod 600 /path/to/workpilot/.env
   ```

4. **定期更新依赖**
   ```bash
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

---

## 下一步

部署完成后，请参考：
- [README.md](../README.md) - 使用指南
- [INSTALL.md](INSTALL.md) - 详细安装说明
