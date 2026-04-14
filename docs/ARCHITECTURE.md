# 架构设计文档

## 1. 系统概述

可嵌入式跨课程AI Agent通用架构平台是一个基于微服务架构的智慧教育平台，旨在解决当前教育领域"教学智能化碎片化"问题，实现AI应用标准化部署和深度教学干预。

## 2. 架构设计原则

### 2.1 微服务架构
每个功能模块独立部署，故障隔离，支持独立扩展。

### 2.2 领域驱动设计 (DDD)
清晰的模块边界，业务逻辑内聚。

### 2.3 API优先
RESTful API设计，OpenAPI规范。

### 2.4 配置外置
环境变量 + 配置文件，支持多环境部署。

## 3. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端应用层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  管理后台   │ │ 智能体构建  │ │ 教师端界面  │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API网关层                                │
│         (认证、限流、路由、日志)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        微服务层                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Agent框架    │ │ 知识中间件   │ │ 平台适配层   │            │
│  │ 服务        │ │ 服务        │ │ 服务        │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐                             │
│  │ 数据融合引擎 │ │ 精细化智能   │                             │
│  │ 服务        │ │ 引擎服务    │                             │
│  └──────────────┘ └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ PostgreSQL   │ │ Redis        │ │ MongoDB      │            │
│  │ (主数据库)   │ │ (缓存)      │ │ (文档存储)   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐                             │
│  │ 向量数据库   │ │ 对象存储    │                             │
│  │ (知识检索)   │ │ (文件存储)  │                             │
│  └──────────────┘ └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务层                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ GLM-4 API    │ │ 超星平台API  │ │ 钉钉平台API  │            │
│  │ (智谱AI)     │ │              │ │              │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 4. 服务模块设计

### 4.1 统一Agent框架 (agent-framework)

**端口**: 8001

**职责**:
- 提供Agent SDK核心接口
- 管理Agent生命周期
- 配置管理与热更新
- Agent注册与发现

**核心类**:
```python
class BaseAgent:
    """Agent基类"""
    def initialize(self) -> None
    def process(self, request: Request) -> Response
    def learn(self, feedback: Feedback) -> None
    def export(self) -> AgentConfig

class AgentManager:
    """Agent管理器"""
    def register(self, agent: BaseAgent) -> str
    def discover(self, agent_id: str) -> BaseAgent
    def invoke(self, agent_id: str, request: Request) -> Response
    def monitor(self) -> List[AgentStatus]
```

### 4.2 知识中间件 (knowledge-middleware)

**端口**: 8002

**职责**:
- 课程知识的标准化表示
- 向量存储与检索
- 知识图谱管理
- 知识迁移机制

**核心类**:
```python
class KnowledgeStore:
    """知识存储"""
    def store(self, knowledge: Knowledge) -> str
    def retrieve(self, query: str, top_k: int) -> List[Knowledge]
    def delete(self, knowledge_id: str) -> bool

class KnowledgeGraph:
    """知识图谱"""
    def add_node(self, node: KnowledgeNode) -> None
    def add_edge(self, source: str, target: str, relation: str) -> None
    def traverse(self, start: str, depth: int) -> List[KnowledgeNode]
```

### 4.3 平台适配层 (platform-adapter)

**端口**: 8003

**职责**:
- 提供统一适配器接口
- 实现超星平台适配
- 实现钉钉平台适配
- Webhook回调处理

**核心类**:
```python
class PlatformAdapter(ABC):
    """平台适配器基类"""
    @abstractmethod
    def authenticate(self, credentials: dict) -> Token
    @abstractmethod
    def get_course(self, course_id: str) -> Course
    @abstractmethod
    def submit_assignment(self, assignment: Assignment) -> bool

class ChaoxingAdapter(PlatformAdapter):
    """超星平台适配器"""
    pass

class DingTalkAdapter(PlatformAdapter):
    """钉钉平台适配器"""
    pass
```

### 4.4 数据融合引擎 (data-fusion)

**端口**: 8004

**职责**:
- 跨课程数据采集
- 学生画像构建
- 学习路径分析
- 数据可视化API

**核心类**:
```python
class DataCollector:
    """数据采集器"""
    def collect(self, source: str, data: dict) -> bool
    def transform(self, raw_data: dict) -> StandardData
    def load(self, data: StandardData) -> bool

class StudentProfiler:
    """学生画像"""
    def build_profile(self, student_id: str) -> StudentProfile
    def update_profile(self, student_id: str, event: LearningEvent) -> None
    def get_weakness(self, student_id: str) -> List[KnowledgePoint]
```

### 4.5 精细化智能引擎 (intelligent-engine)

**端口**: 8005

**职责**:
- 智能答疑
- 作业批改与批注
- 学情预警
- 增量练习生成

**核心类**:
```python
class QAEngine:
    """智能答疑引擎"""
    def ask(self, question: str, context: dict) -> Answer

class GradingEngine:
    """作业批改引擎"""
    def grade(self, submission: Submission) -> GradingResult
    def annotate(self, content: str, errors: List[Error]) -> AnnotatedContent

class WarningEngine:
    """学情预警引擎"""
    def analyze(self, student_id: str) -> List[Warning]
    def predict_risk(self, student_id: str) -> RiskLevel

class ExerciseGenerator:
    """练习生成器"""
    def generate(self, knowledge_points: List[str], difficulty: str) -> List[Exercise]
```

## 5. 数据模型设计

### 5.1 核心实体

```sql
-- 课程表
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    knowledge_graph_id UUID,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 智能体表
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学生表
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作业表
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    knowledge_points JSONB,
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 提交记录表
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID REFERENCES assignments(id),
    student_id UUID REFERENCES students(id),
    content TEXT NOT NULL,
    file_urls JSONB,
    annotations JSONB,
    score DECIMAL(5,2),
    feedback TEXT,
    status VARCHAR(20) DEFAULT 'submitted',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP
);

-- 学情记录表
CREATE TABLE learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    course_id UUID REFERENCES courses(id),
    knowledge_point_id VARCHAR(100) NOT NULL,
    mastery_level DECIMAL(3,2) DEFAULT 0,
    practice_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    last_practice_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id, knowledge_point_id)
);
```

## 6. API设计规范

### 6.1 RESTful API约定

- 使用名词复数形式表示资源
- 使用HTTP方法表示操作类型
- 版本号放在URL中: `/api/v1/`

### 6.2 统一响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": { ... },
    "timestamp": "2025-04-13T10:00:00Z"
}
```

### 6.3 错误码规范

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 7. 容错与隔离设计

### 7.1 服务隔离
- 每个微服务独立Docker容器
- 资源限制与配额
- 故障检测与自动恢复

### 7.2 熔断与降级
- 熔断器模式
- 服务降级策略
- 重试机制

### 7.3 日志与监控
- 结构化日志
- 分布式追踪
- 性能监控

## 8. 安全设计

### 8.1 认证与授权
- JWT Token认证
- RBAC权限模型
- API Key管理

### 8.2 数据安全
- 敏感数据加密
- SQL注入防护
- XSS/CSRF防护

## 9. 部署架构

```
┌─────────────────────────────────────────────────┐
│                  负载均衡器                      │
│                   (Nginx)                       │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   API网关   │ │   API网关   │ │   API网关   │
│  (实例1)    │ │  (实例2)    │ │  (实例3)    │
└─────────────┘ └─────────────┘ └─────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
┌─────────────────────────────────────────────────┐
│               微服务集群 (K8s/Docker)            │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   Redis     │ │  MongoDB    │
│   主从      │ │   集群      │ │   副本集    │
└─────────────┘ └─────────────┘ └─────────────┘
```
