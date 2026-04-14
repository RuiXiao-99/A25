@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   EduAgent Platform - Windows 开发环境启动脚本
echo ==========================================

:: 设置项目根目录
set PROJECT_ROOT=%~dp0
cd /d %PROJECT_ROOT%

:: 1. 检查环境
echo [1/5] 检查环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+ 或激活 Anaconda 环境。
    pause
    exit /b
)

node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+。
    pause
    exit /b
)
echo 找到环境，准备继续...

:: 2. 启动基础数据库服务 (Docker)
echo [2/5] 启动 Docker 容器 (数据库/缓存)...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [警告] Docker 启动失败。请确保 Docker Desktop 已运行。
)

:: 3. 安装依赖 (仅在初次运行或需要更新时)
echo [3/5] 检查并安装 Python 依赖...
pip install fastapi uvicorn pydantic pydantic-settings httpx langchain-openai langchain --quiet

:: 4. 启动后端微服务
echo [4/5] 正在启动后端服务 (将在新窗口中运行)...

:: 启动各微服务
start "Agent Framework" cmd /k "cd /d %PROJECT_ROOT%services\agent-framework && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
timeout /t 2 >nul

start "Knowledge Middleware" cmd /k "cd /d %PROJECT_ROOT%services\knowledge-middleware && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002"
timeout /t 2 >nul

start "Platform Adapter" cmd /k "cd /d %PROJECT_ROOT%services\platform-adapter && python -m uvicorn app.main:app --host 0.0.0.0 --port 8003"
timeout /t 2 >nul

start "Intelligent Engine" cmd /k "cd /d %PROJECT_ROOT%services\intelligent-engine && python -m uvicorn app.main:app --host 0.0.0.0 --port 8005"
timeout /t 2 >nul

:: 启动 API Gateway
start "API Gateway" cmd /k "cd /d %PROJECT_ROOT% && python gateway_server.py"
timeout /t 2 >nul

:: 5. 启动前端服务
echo [5/5] 正在启动前端服务...
cd /d %PROJECT_ROOT%frontend
if not exist "node_modules\" (
    echo 初次运行，正在安装前端依赖...
    npm install
)
start "Frontend App" cmd /k "npm run dev"

echo ==========================================
echo   启动完成！
echo   前端应用: http://localhost:5173
echo   API 文档: http://localhost:8000/docs
echo ==========================================
pause