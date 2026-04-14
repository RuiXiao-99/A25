#!/bin/bash

# EduAgent Platform 一键启动脚本
# 用于开发环境快速启动所有服务

echo "=========================================="
echo "  EduAgent Platform - 开发环境启动脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查Python
check_python() {
    echo -e "${YELLOW}检查Python环境...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✓ 找到 $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}✗ 未找到Python3，请先安装Python 3.11+${NC}"
        exit 1
    fi
}

# 检查Node.js
check_node() {
    echo -e "${YELLOW}检查Node.js环境...${NC}"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✓ 找到 Node.js $NODE_VERSION${NC}"
    else
        echo -e "${RED}✗ 未找到Node.js，请先安装Node.js 18+${NC}"
        exit 1
    fi
}

# 安装Python依赖
install_python_deps() {
    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip3 install fastapi uvicorn pydantic pydantic-settings httpx --quiet
    echo -e "${GREEN}✓ Python依赖安装完成${NC}"
}

# 安装前端依赖
install_frontend_deps() {
    echo -e "${YELLOW}安装前端依赖...${NC}"
    cd "$PROJECT_ROOT/frontend"
    if [ -f "package-lock.json" ]; then
        npm ci --quiet
    else
        npm install --quiet
    fi
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
}

# 启动后端服务
start_backend_services() {
    echo -e "${YELLOW}启动后端服务...${NC}"

    # 创建日志目录
    mkdir -p "$PROJECT_ROOT/logs"

    # 启动Agent框架服务
    echo "  启动 Agent Framework (端口8001)..."
    cd "$PROJECT_ROOT/services/agent-framework"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > "$PROJECT_ROOT/logs/agent-framework.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/agent-framework.pid"
    sleep 1

    # 启动知识中间件服务
    echo "  启动 Knowledge Middleware (端口8002)..."
    cd "$PROJECT_ROOT/services/knowledge-middleware"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > "$PROJECT_ROOT/logs/knowledge-middleware.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/knowledge-middleware.pid"
    sleep 1

    # 启动平台适配层服务
    echo "  启动 Platform Adapter (端口8003)..."
    cd "$PROJECT_ROOT/services/platform-adapter"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > "$PROJECT_ROOT/logs/platform-adapter.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/platform-adapter.pid"
    sleep 1

    # 启动智能引擎服务
    echo "  启动 Intelligent Engine (端口8005)..."
    cd "$PROJECT_ROOT/services/intelligent-engine"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8005 > "$PROJECT_ROOT/logs/intelligent-engine.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/intelligent-engine.pid"
    sleep 1

    # 启动API网关
    echo "  启动 API Gateway (端口8000)..."
    cd "$PROJECT_ROOT"
    nohup python3 gateway_server.py > "$PROJECT_ROOT/logs/gateway.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/gateway.pid"
    sleep 1

    echo -e "${GREEN}✓ 后端服务启动完成${NC}"
}

# 启动前端服务
start_frontend() {
    echo -e "${YELLOW}启动前端服务...${NC}"
    cd "$PROJECT_ROOT/frontend"
    nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/frontend.pid"
    sleep 2
    echo -e "${GREEN}✓ 前端服务启动完成${NC}"
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "  服务状态"
    echo "=========================================="

    # 检查各服务是否运行
    for port in 8000 8001 8002 8003 8005 5173; do
        if lsof -i:$port > /dev/null 2>&1; then
            echo -e "  端口 $port: ${GREEN}运行中${NC}"
        else
            echo -e "  端口 $port: ${RED}未启动${NC}"
        fi
    done

    echo ""
    echo "=========================================="
    echo "  访问地址"
    echo "=========================================="
    echo "  前端应用:    http://localhost:5173"
    echo "  API文档:     http://localhost:8000/docs"
    echo ""
    echo "=========================================="
    echo "  日志文件"
    echo "=========================================="
    echo "  日志目录: $PROJECT_ROOT/logs/"
    echo ""
    echo "  查看日志命令示例:"
    echo "    tail -f $PROJECT_ROOT/logs/gateway.log"
    echo "    tail -f $PROJECT_ROOT/logs/agent-framework.log"
    echo ""
}

# 停止所有服务
stop_services() {
    echo -e "${YELLOW}停止所有服务...${NC}"

    for pid_file in "$PROJECT_ROOT/logs/"*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo "  停止进程 $pid"
            fi
            rm -f "$pid_file"
        fi
    done

    # 额外检查端口并清理
    for port in 8000 8001 8002 8003 8005 5173; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            kill -9 $pid 2>/dev/null
            echo "  清理端口 $port (PID: $pid)"
        fi
    done

    echo -e "${GREEN}✓ 所有服务已停止${NC}"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            check_python
            check_node
            install_python_deps
            install_frontend_deps
            start_backend_services
            start_frontend
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            check_python
            check_node
            start_backend_services
            start_frontend
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            tail -f "$PROJECT_ROOT/logs/$2.log"
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status|logs <service>}"
            echo ""
            echo "命令:"
            echo "  start   - 启动所有服务"
            echo "  stop    - 停止所有服务"
            echo "  restart - 重启所有服务"
            echo "  status  - 查看服务状态"
            echo "  logs    - 查看日志 (logs gateway|agent-framework|...)"
            exit 1
            ;;
    esac
}

main "$@"
