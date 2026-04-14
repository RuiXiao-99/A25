# 贡献指南

感谢您对本项目的关注！本文档将帮助您了解如何参与项目开发。

## 行为准则

- 尊重所有贡献者
- 保持专业和建设性的讨论
- 接受建设性批评
- 关注对社区最有利的事情

## 开发流程

### 1. Fork项目

```bash
# 在GitHub上Fork项目后
git clone https://github.com/YOUR_USERNAME/eduagent-platform.git
cd eduagent-platform
git remote add upstream https://github.com/ORIGINAL_REPO/eduagent-platform.git
```

### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 3. 开发与测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black .
isort .

# 代码检查
flake8
mypy .
```

### 4. 提交代码

#### Commit规范

使用约定式提交格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型说明**:
- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关
- `perf`: 性能优化

**示例**:
```
feat(agent): 添加Agent热更新功能

- 支持配置文件热更新
- 添加更新回调机制
- 优化Agent重载性能

Closes #123
```

### 5. 推送与创建PR

```bash
git push origin feature/your-feature-name
```

然后在GitHub上创建Pull Request。

## 代码规范

### Python代码规范

遵循PEP 8规范，使用以下工具：

```bash
# 格式化
black --line-length 100 .
isort --profile black .

# 检查
flake8 --max-line-length 100
mypy --ignore-missing-imports .
```

#### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写下划线 | `agent_manager.py` |
| 类 | 大驼峰 | `AgentManager` |
| 函数/方法 | 小写下划线 | `register_agent()` |
| 常量 | 大写下划线 | `MAX_RETRY_COUNT` |
| 私有属性 | 单下划线前缀 | `_internal_state` |

#### 文档字符串

```python
def process_request(self, request: Request) -> Response:
    """
    处理请求并返回响应。

    Args:
        request: 请求对象，包含用户输入和上下文信息。

    Returns:
        Response: 处理后的响应对象。

    Raises:
        ValueError: 当请求参数无效时抛出。
        AgentNotFoundError: 当指定的Agent不存在时抛出。

    Example:
        >>> manager = AgentManager()
        >>> response = manager.process_request(request)
    """
    pass
```

#### 类型注解

```python
from typing import List, Dict, Optional, Union

def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
    """获取Agent实例"""
    pass

def list_agents(
    self,
    course_id: Optional[str] = None,
    status: str = "active"
) -> List[Dict[str, Any]]:
    """列出Agent"""
    pass
```

### TypeScript/Vue代码规范

```bash
# 格式化
npm run lint

# 类型检查
npm run type-check
```

#### Vue组件规范

```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Props定义
interface Props {
  title: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// 响应式状态
const loading = ref(false)

// 计算属性
const buttonText = computed(() => {
  return loading.value ? '处理中...' : '提交'
})
</script>

<style scoped>
.component-name {
  /* 样式 */
}
</style>
```

## 测试规范

### 单元测试

```python
# tests/test_agent_manager.py
import pytest
from app.services.agent_manager import AgentManager

class TestAgentManager:
    """AgentManager测试类"""

    @pytest.fixture
    def manager(self):
        """创建测试用的Manager实例"""
        return AgentManager()

    def test_register_agent(self, manager):
        """测试Agent注册"""
        agent = MockAgent()
        agent_id = manager.register(agent)
        assert agent_id is not None
        assert manager.discover(agent_id) == agent

    def test_invoke_agent(self, manager):
        """测试Agent调用"""
        agent = MockAgent()
        agent_id = manager.register(agent)
        response = manager.invoke(agent_id, MockRequest())
        assert response is not None
```

### 集成测试

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_agent():
    """测试创建Agent API"""
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "Test Agent",
            "type": "qa",
            "course_id": "test-course"
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Agent"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_agent_manager.py

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 运行特定标记的测试
pytest -m "not slow"
```

## 模块开发指南

### 新增微服务

1. 在 `services/` 目录下创建新目录
2. 创建以下文件结构：

```
services/new-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI应用入口
│   ├── config.py        # 配置管理
│   ├── models.py        # 数据模型
│   ├── services.py      # 业务逻辑
│   ├── routers/         # API路由
│   │   ├── __init__.py
│   │   └── api.py
│   └── utils/           # 工具函数
├── tests/
│   └── test_main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

3. 更新 `docker-compose.yml` 添加新服务
4. 更新API网关路由配置

### 新增平台适配器

1. 继承 `PlatformAdapter` 基类
2. 实现所有抽象方法
3. 注册到适配器工厂

```python
# services/platform-adapter/app/adapters/new_platform.py
from app.base import PlatformAdapter

class NewPlatformAdapter(PlatformAdapter):
    """新平台适配器"""

    def authenticate(self, credentials: dict) -> Token:
        """认证"""
        pass

    def get_course(self, course_id: str) -> Course:
        """获取课程"""
        pass

    def submit_assignment(self, assignment: Assignment) -> bool:
        """提交作业"""
        pass
```

## 文档贡献

### 文档类型

- API文档
- 架构文档
- 部署指南
- 用户手册
- 开发指南

### 文档规范

- 使用Markdown格式
- 保持简洁清晰
- 添加适当的示例代码
- 及时更新文档

## 发布流程

1. 更新 `CHANGELOG.md`
2. 更新版本号
3. 创建Git标签
4. 构建Docker镜像
5. 部署到生产环境

## 获取帮助

- 提交Issue: [GitHub Issues](https://github.com/xxx/eduagent-platform/issues)
- 加入讨论: [GitHub Discussions](https://github.com/xxx/eduagent-platform/discussions)
- 邮件联系: dev@eduagent.edu.cn

## 许可证

本项目采用MIT许可证，贡献的代码将自动适用此许可证。
