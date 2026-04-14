@echo off
chcp 65001 >nul
title EduAgent Platform - Windows Launcher
echo ==========================================
echo   EduAgent Platform - Windows Launcher
echo   可嵌入式跨课程AI Agent通用架构平台
echo ==========================================
echo.

REM 设置Python路径
set PYTHON=python

REM 检查Python是否安装
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo [信息] Python版本:
%PYTHON% --version
echo.

REM 设置工作目录
cd /d "%~dp0"
echo [信息] 工作目录: %CD%
echo.

REM 检查并创建虚拟环境
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo [信息] 升级pip...
python -m pip install --upgrade pip -q

REM 安装依赖
echo [信息] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，尝试继续...
)

echo.
echo ==========================================
echo   启动服务
echo ==========================================
echo.

REM 创建数据目录
if not exist "data" mkdir data

REM 启动Agent Framework Service (端口8001)
echo [1/5] 启动 Agent Framework Service (端口8001)...
start "Agent Framework" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python -m uvicorn services.agent-framework.app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 2 /nobreak >nul

REM 启动Knowledge Middleware Service (端口8002)
echo [2/5] 启动 Knowledge Middleware Service (端口8002)...
start "Knowledge Middleware" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python -m uvicorn services.knowledge-middleware.app.main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 2 /nobreak >nul

REM 启动Platform Adapter Service (端口8003)
echo [3/5] 启动 Platform Adapter Service (端口8003)...
start "Platform Adapter" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python -m uvicorn services.platform-adapter.app.main:app --host 0.0.0.0 --port 8003 --reload"
timeout /t 2 /nobreak >nul

REM 启动Intelligent Engine Service (端口8005)
echo [4/5] 启动 Intelligent Engine Service (端口8005)...
start "Intelligent Engine" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python -m uvicorn services.intelligent-engine.app.main:app --host 0.0.0.0 --port 8005 --reload"
timeout /t 2 /nobreak >nul

REM 启动API Gateway (端口8000)
echo [5/5] 启动 API Gateway (端口8000)...
start "API Gateway" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python gateway_server.py"
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo   所有服务已启动
echo ==========================================
echo.
echo 服务地址:
echo   - API Gateway:     http://localhost:8000
echo   - Agent Framework: http://localhost:8001
echo   - Knowledge:       http://localhost:8002
echo   - Platform Adapter:http://localhost:8003
echo   - Intelligent:     http://localhost:8005
echo.
echo 文档地址:
echo   - API文档: http://localhost:8000/docs
echo   - Redoc:   http://localhost:8000/redoc
echo.
echo 按任意键关闭所有服务...
pause >nul

REM 关闭所有服务窗口
taskkill /FI "WINDOWTITLE eq Agent Framework*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Knowledge Middleware*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Platform Adapter*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Intelligent Engine*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq API Gateway*" /F >nul 2>&1

echo.
echo 所有服务已关闭
timeout /t 2 /nobreak >nul
