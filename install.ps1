# WorkPilot Windows 安装脚本

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "WorkPilot 安装向导" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "❌ 错误: 未找到 Python" -ForegroundColor Red
    Write-Host "请先安装 Python 3.9 或更高版本" -ForegroundColor Yellow
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = & $pythonCmd -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
Write-Host "✓ 检测到 Python $pythonVersion" -ForegroundColor Green

# 检查虚拟环境
if (Test-Path "venv") {
    Write-Host "⚠️  虚拟环境已存在" -ForegroundColor Yellow
    $response = Read-Host "是否删除并重新创建? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "删除旧的虚拟环境..."
        Remove-Item -Recurse -Force venv
    } else {
        Write-Host "使用现有虚拟环境"
    }
}

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..."
    & $pythonCmd -m venv venv
    Write-Host "✓ 虚拟环境创建成功" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host "激活虚拟环境..."
& "venv\Scripts\Activate.ps1"

# 升级 pip
Write-Host "升级 pip..."
python -m pip install --upgrade pip | Out-Null

# 安装依赖
Write-Host "安装依赖包..."
pip install -r requirements.txt

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "配置 Bot Token" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "请从 @BotFather 获取你的 Bot Token"
    Write-Host "Token 格式类似: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    Write-Host ""

    $botToken = Read-Host "请输入你的 Bot Token"

    if ([string]::IsNullOrWhiteSpace($botToken)) {
        Write-Host "❌ Token 不能为空" -ForegroundColor Red
        Write-Host "你可以稍后手动创建 .env 文件" -ForegroundColor Yellow
    } else {
        (Get-Content .env.example) -replace 'your_bot_token_here', $botToken | Set-Content .env
        Write-Host "✓ .env 文件已创建" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env 文件已存在" -ForegroundColor Green
}

# 创建数据目录
New-Item -ItemType Directory -Force -Path "data\reports" | Out-Null

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "安装完成!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法:"
Write-Host "  1. 激活虚拟环境: .\venv\Scripts\Activate.ps1"
Write-Host "  2. 运行 Bot:       python main.py"
Write-Host ""
Write-Host "如果还未配置 Bot Token，请编辑 .env 文件"
Write-Host ""
