# EduAgent Platform - Windows 版本使用指南

## 项目简介

可嵌入式跨课程AI Agent通用架构平台 - Windows完整运行版本

本项目是第十七届中国大学生服务外包创新创业大赛A25赛题的实现，使用SQLite数据库替代PostgreSQL/MongoDB/Redis，实现Windows环境下的完整运行。

## 技术架构

### 后端服务
- **Agent Framework Service** (端口8001) - 统一AI Agent框架
- **Knowledge Middleware Service** (端口8002) - 知识中间件
- **Platform Adapter Service** (端口8003) - 平台适配层
- **Intelligent Engine Service** (端口8005) - 精细化智能引擎
- **API Gateway** (端口8000) - 统一API网关

### 数据库
- **SQLite** - 单文件数据库，无需额外安装

### 技术栈
- Python 3.10+
- FastAPI
- SQLite + aiosqlite (异步支持)
- LangChain + GLM-4 (智谱AI)

## 快速开始

### 方式一：运行演示程序（推荐首次使用）

```batch
# 1. 确保已安装Python 3.10+
python --version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行演示程序
python demo.py
```

演示程序将展示平台的所有核心功能，包括：
- 课程管理
- 知识库管理
- 智能体管理
- 学生管理
- 作业与批改
- 学习记录
- 学情预警
- 问答历史
- 平台配置

### 方式二：启动完整服务

```batch
# 双击运行启动脚本
start_windows.bat
```

或手动启动：

```batch
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate.bat

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动各个服务（每个服务一个终端窗口）

# 终端1 - Agent Framework
python -m uvicorn services.agent-framework.app.main:app --host 0.0.0.0 --port 8001 --reload

# 终端2 - Knowledge Middleware
python -m uvicorn services.knowledge-middleware.app.main:app --host 0.0.0.0 --port 8002 --reload

# 终端3 - Platform Adapter
python -m uvicorn services.platform-adapter.app.main:app --host 0.0.0.0 --port 8003 --reload

# 终端4 - Intelligent Engine
python -m uvicorn services.intelligent-engine.app.main:app --host 0.0.0.0 --port 8005 --reload

# 终端5 - API Gateway
python gateway_server.py
```

## 访问服务

服务启动后，可以通过以下地址访问：

- **API网关**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Redoc文档**: http://localhost:8000/redoc

各个服务的独立文档：
- Agent Framework: http://localhost:8001/docs
- Knowledge Middleware: http://localhost:8002/docs
- Platform Adapter: http://localhost:8003/docs
- Intelligent Engine: http://localhost:8005/docs

## 数据库

数据库文件位置：`data/eduagent.db`

可以使用以下工具查看：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLiteStudio](https://sqlitestudio.pl/)
- VS Code SQLite扩展

### 数据表结构

| 表名 | 说明 |
|------|------|
| courses | 课程信息 |
| agents | AI智能体配置 |
| knowledge_points | 知识点 |
| students | 学生信息 |
| assignments | 作业 |
| submissions | 作业提交记录 |
| learning_records | 学习记录 |
| warnings | 学情预警 |
| qa_history | 问答历史 |
| platform_configs | 平台适配配置 |

## API接口示例

### 1. 创建课程

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python程序设计",
    "code": "CS101",
    "description": "Python编程基础"
  }'
```

### 2. 创建知识点

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/points" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python基础语法",
    "course_id": "your-course-id",
    "description": "变量、数据类型、运算符"
  }'
```

### 3. 创建智能体

```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python助教",
    "type": "teaching_assistant",
    "course_id": "your-course-id",
    "config": {
      "model": "glm-4",
      "temperature": 0.7
    }
  }'
```

### 4. 智能答疑

```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是Python的装饰器？",
    "course_id": "your-course-id"
  }'
```

## 配置智谱AI

要使用真实的AI功能，需要配置智谱AI的API Key：

### 方式1：环境变量

```batch
set GLM_API_KEY=your-api-key-here
```

### 方式2：创建.env文件

```
GLM_API_KEY=your-api-key-here
```

获取API Key: [智谱AI开放平台](https://open.bigmodel.cn/)

## 项目结构

```
A25-main/
├── data/                       # SQLite数据库文件
│   └── eduagent.db            # 主数据库
├── services/                   # 微服务模块
│   ├── agent-framework/       # Agent框架服务
│   ├── knowledge-middleware/  # 知识中间件服务
│   ├── platform-adapter/      # 平台适配服务
│   └── intelligent-engine/    # 智能引擎服务
├── shared/                     # 共享模块
│   ├── database.py            # 数据库访问层
│   ├── models.py              # 数据模型
│   ├── config.py              # 配置
│   └── utils.py               # 工具函数
├── gateway_server.py          # API网关
├── demo.py                    # 演示程序
├── start_windows.bat          # Windows启动脚本
├── requirements.txt           # 依赖列表
└── README_WINDOWS.md          # 本文件
```

## 常见问题

### 1. 端口被占用

如果启动时提示端口被占用，可以修改对应服务的端口：

编辑 `shared/config.py` 中的端口配置，或设置环境变量：

```batch
set AGENT_FRAMEWORK_PORT=8001
set KNOWLEDGE_MIDDLEWARE_PORT=8002
```

### 2. 依赖安装失败

如果某些依赖安装失败，可以尝试：

```batch
# 升级pip
python -m pip install --upgrade pip

# 单独安装失败的包
pip install aiosqlite
```

### 3. 数据库锁定

SQLite在并发访问时可能出现锁定，这是正常现象。如需高并发，建议后期迁移到PostgreSQL。

## 团队开发建议

### 代码质量把控

1. **模块化开发**: 每个功能独立提交，故障隔离
2. **Git规范**: 使用feature分支，PR合并
3. **文档**: 每个模块添加README和版本记录
4. **日志**: 使用loguru记录关键操作

### 调试技巧

1. 使用 `print()` 或 `logger.debug()` 调试
2. 查看SQLite数据库直接验证数据
3. 使用API文档页面测试接口

## 后续优化方向

1. **数据库迁移**: 生产环境建议使用PostgreSQL
2. **缓存层**: 添加Redis缓存热点数据
3. **向量检索**: 集成ChromaDB或Milvus
4. **前端集成**: 连接Vue前端应用
5. **容器化**: 提供Docker部署方案

## 技术支持

- 项目文档: `docs/` 目录
- API文档: 启动服务后访问 `/docs`
- 数据库: 使用DB Browser for SQLite查看

## 许可证

MIT License

## 团队

中国计量大学 - 教育数字化创新团队
