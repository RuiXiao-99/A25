# 前后端连接指南

本文档说明如何让前后端正常配合使用。

## 架构说明

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   前端 (Vue 3)   │────▶│   API 网关      │────▶│   后端微服务     │
│   Port: 5173    │     │   Port: 8000    │     │   8001-8005     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 方式一：开发环境（推荐新手）

### 1. 启动后端服务

```bash
# 进入项目目录
cd /workspace/eduagent-platform

# 安装Python依赖
pip3 install fastapi uvicorn pydantic pydantic-settings

# 启动各个后端服务（需要开多个终端）

# 终端1 - Agent框架服务 (端口8001)
cd services/agent-framework
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 终端2 - 知识中间件服务 (端口8002)
cd services/knowledge-middleware
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 终端3 - 平台适配层服务 (端口8003)
cd services/platform-adapter
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# 终端4 - 智能引擎服务 (端口8005)
cd services/intelligent-engine
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

### 2. 启动API网关

```bash
# 终端5 - 启动API网关 (端口8000)
cd /workspace/eduagent-platform
python3 gateway_server.py
```

### 3. 启动前端

```bash
# 终端6 - 启动前端开发服务器
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

打开浏览器访问: http://localhost:5173

---

## 方式二：简化开发（快速测试）

如果只想快速测试，可以使用以下方式：

### 修改前端配置连接单个服务

编辑 `frontend/vite.config.ts`：

```typescript
server: {
  port: 5173,
  proxy: {
    '/api/v1/agents': {
      target: 'http://localhost:8001',
      changeOrigin: true,
      rewrite: (path) => path
    },
    '/api/v1/knowledge': {
      target: 'http://localhost:8002',
      changeOrigin: true
    },
    '/api/v1/qa': {
      target: 'http://localhost:8005',
      changeOrigin: true
    },
    '/api/v1/grading': {
      target: 'http://localhost:8005',
      changeOrigin: true
    },
    '/api/v1/warning': {
      target: 'http://localhost:8005',
      changeOrigin: true
    },
    '/api/v1/exercise': {
      target: 'http://localhost:8005',
      changeOrigin: true
    }
  }
}
```

然后只需启动需要的服务即可。

---

## 方式三：生产环境部署

### 使用 Docker Compose（推荐）

```bash
# 确保已安装 Docker 和 Docker Compose

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 访问应用
# 前端: http://localhost
# API文档: http://localhost:8000/docs
```

### 手动部署

1. **构建前端**
```bash
cd frontend
npm run build
# 生成的文件在 frontend/dist/ 目录
```

2. **配置Nginx**
```nginx
server {
    listen 80;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/v1/agents {
        proxy_pass http://localhost:8001;
    }

    location /api/v1/knowledge {
        proxy_pass http://localhost:8002;
    }

    location /api/v1/qa,
    location /api/v1/grading,
    location /api/v1/warning,
    location /api/v1/exercise {
        proxy_pass http://localhost:8005;
    }
}
```

---

## API 端口映射表

| 服务 | 端口 | API路径前缀 |
|------|------|-------------|
| API网关 | 8000 | /api/v1/* |
| Agent框架 | 8001 | /api/v1/agents |
| 知识中间件 | 8002 | /api/v1/knowledge |
| 平台适配层 | 8003 | /api/v1/adapters, /api/v1/webhooks |
| 智能引擎 | 8005 | /api/v1/qa, /api/v1/grading, /api/v1/warning, /api/v1/exercise |

---

## 常见问题

### Q: 前端请求返回 404

检查后端服务是否已启动，端口是否正确。

### Q: 跨域错误 (CORS)

后端服务已配置CORS，允许来自 `localhost:3000` 和 `localhost:5173` 的请求。

如需添加其他域名，修改各服务的 CORS_ORIGINS 配置。

### Q: 如何测试单个API

访问各服务的 API 文档：
- http://localhost:8001/docs - Agent框架
- http://localhost:8002/docs - 知识中间件
- http://localhost:8003/docs - 平台适配层
- http://localhost:8005/docs - 智能引擎
