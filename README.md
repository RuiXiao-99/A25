# 可嵌入式跨课程AI Agent通用架构平台

## 项目简介

本项目是第十七届中国大学生服务外包创新创业大赛A25赛题的实现，旨在开发一套支持多课程AI Agent快速开发的通用平台架构。

## 核心功能

- **统一AI Agent框架**: 提供标准化的智能体开发SDK
- **知识中间件**: 课程知识的标准化表示、存储和检索
- **平台适配层**: 支持与超星、钉钉等主流教学平台对接
- **数据融合引擎**: 跨课程学习数据的统一采集和分析
- **精细化智能引擎**: 智能答疑、作业批改、学情预警、增量练习生成

## 技术栈

### 后端
- Python 3.11+
- FastAPI (微服务架构)
- LangChain + GLM-4 (智谱AI)
- PostgreSQL + Redis + MongoDB

### 前端
- Vue 3 + TypeScript
- Element Plus
- Pinia + Vite

## 项目结构

```
eduagent-platform/
├── services/                    # 微服务模块
│   ├── agent-framework/         # 统一Agent框架
│   ├── knowledge-middleware/    # 知识中间件
│   ├── platform-adapter/        # 平台适配层
│   ├── data-fusion/             # 数据融合引擎
│   └── intelligent-engine/      # 精细化智能引擎
├── gateway/                     # API网关
├── frontend/                    # 前端应用
├── docs/                        # 文档
└── docker/                      # Docker配置
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### 安装与运行

```bash
# 克隆项目
git clone <repository-url>
cd eduagent-platform

# 后端服务
cd services/agent-framework
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端应用
cd frontend
npm install
npm run dev
```

## 文档

- [架构设计](docs/ARCHITECTURE.md)
- [API文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)
- [贡献指南](docs/CONTRIBUTING.md)

## 版本历史

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本变更记录。

## 许可证

MIT License

## 团队

中国计量大学 - 教育数字化创新团队
