# 部署指南

## 1. 环境要求

### 1.1 基础环境

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| Docker | 24+ | 容器化部署 |
| Docker Compose | 2.20+ | 多容器编排 |

### 1.2 外部服务

| 服务 | 版本 | 说明 |
|------|------|------|
| PostgreSQL | 15+ | 主数据库 |
| Redis | 7+ | 缓存服务 |
| MongoDB | 6+ | 文档存储 |

### 1.3 AI服务

- 智谱AI GLM-4 API Key

## 2. 本地开发环境

### 2.1 克隆项目

```bash
git clone <repository-url>
cd eduagent-platform
```

### 2.2 后端环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置
```

### 2.3 前端环境配置

```bash
cd frontend
npm install
npm run dev
```

### 2.4 启动依赖服务

```bash
# 使用Docker启动数据库服务
docker-compose up -d postgres redis mongodb
```

### 2.5 启动后端服务

```bash
# 启动各个微服务
cd services/agent-framework
uvicorn app.main:app --reload --port 8001

cd services/knowledge-middleware
uvicorn app.main:app --reload --port 8002

# ... 其他服务类似
```

## 3. Docker部署

### 3.1 构建镜像

```bash
# 构建所有服务镜像
docker-compose build
```

### 3.2 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]
```

### 3.3 停止服务

```bash
docker-compose down
```

## 4. 生产环境部署

### 4.1 使用Kubernetes (推荐)

#### 4.1.1 准备工作

```bash
# 确保kubectl已配置
kubectl cluster-info
```

#### 4.1.2 创建命名空间

```bash
kubectl create namespace eduagent
```

#### 4.1.3 部署配置

```bash
# 创建ConfigMap和Secret
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# 部署服务
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/services.yaml

# 部署Ingress
kubectl apply -f k8s/ingress.yaml
```

### 4.2 使用Docker Compose

#### 4.2.1 配置文件

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  gateway:
    image: eduagent/gateway:latest
    ports:
      - "80:80"
    environment:
      - ENV=production
    depends_on:
      - agent-framework
      - knowledge-middleware

  agent-framework:
    image: eduagent/agent-framework:latest
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # ... 其他服务
```

#### 4.2.2 启动生产环境

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 5. 数据库配置

### 5.1 PostgreSQL

```sql
-- 创建数据库
CREATE DATABASE eduagent;

-- 创建用户
CREATE USER eduagent WITH PASSWORD 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE eduagent TO eduagent;
```

### 5.2 Redis

```bash
# redis.conf 配置
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 5.3 MongoDB

```javascript
// 创建用户
db.createUser({
    user: "eduagent",
    pwd: "your_password",
    roles: ["readWrite"]
})
```

## 6. 环境变量配置

### 6.1 必需配置

```bash
# .env 文件

# 数据库配置
DATABASE_URL=postgresql://eduagent:password@localhost:5432/eduagent
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/eduagent

# AI服务配置
GLM_API_KEY=your_glm_api_key
GLM_API_BASE=https://open.bigmodel.cn/api/paas/v4

# 安全配置
JWT_SECRET=your_jwt_secret
API_KEY_SALT=your_salt

# 服务端口
GATEWAY_PORT=8000
AGENT_FRAMEWORK_PORT=8001
KNOWLEDGE_MIDDLEWARE_PORT=8002
PLATFORM_ADAPTER_PORT=8003
DATA_FUSION_PORT=8004
INTELLIGENT_ENGINE_PORT=8005
```

### 6.2 可选配置

```bash
# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 限流配置
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# 缓存配置
CACHE_TTL=3600
```

## 7. 健康检查

### 7.1 服务健康检查

```bash
# 检查各服务健康状态
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### 7.2 数据库连接检查

```bash
# PostgreSQL
pg_isready -h localhost -p 5432

# Redis
redis-cli ping

# MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"
```

## 8. 监控与日志

### 8.1 日志配置

日志输出到标准输出，支持JSON格式：

```json
{
    "timestamp": "2025-04-13T10:00:00Z",
    "level": "INFO",
    "service": "agent-framework",
    "message": "Agent registered successfully",
    "agent_id": "agent-001"
}
```

### 8.2 监控指标

- 请求QPS
- 响应时间
- 错误率
- 资源使用率

## 9. 备份与恢复

### 9.1 数据库备份

```bash
# PostgreSQL备份
pg_dump eduagent > backup_$(date +%Y%m%d).sql

# MongoDB备份
mongodump --db eduagent --out backup_$(date +%Y%m%d)
```

### 9.2 数据恢复

```bash
# PostgreSQL恢复
psql eduagent < backup_20250413.sql

# MongoDB恢复
mongorestore --db eduagent backup_20250413/eduagent
```

## 10. 故障排查

### 10.1 常见问题

#### 服务无法启动
- 检查端口是否被占用
- 检查环境变量是否正确配置
- 检查依赖服务是否正常运行

#### 数据库连接失败
- 检查数据库服务是否运行
- 检查连接字符串是否正确
- 检查网络连通性

#### AI服务调用失败
- 检查API Key是否有效
- 检查API配额是否充足
- 检查网络连接

### 10.2 日志查看

```bash
# Docker日志
docker-compose logs -f [service_name]

# Kubernetes日志
kubectl logs -f deployment/[deployment_name] -n eduagent
```
