"""
Agent基类定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from shared.models import AgentConfig
from shared.utils import generate_uuid


logger = logging.getLogger(__name__)


@dataclass
class AgentRequest:
    """Agent请求"""
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent响应"""
    result: Any
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Agent基类

    所有智能体必须继承此类并实现以下方法：
    - initialize(): 初始化Agent
    - process(request): 处理请求
    - learn(feedback): 学习更新（可选）
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        config: AgentConfig,
        course_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.config = config
        self.course_id = course_id
        self.status = "initialized"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._initialized = False

        self._logger = logging.getLogger(f"agent.{agent_id}")

    async def initialize(self) -> None:
        """
        初始化Agent

        子类应重写此方法以执行自定义初始化逻辑
        """
        if self._initialized:
            self._logger.warning(f"Agent {self.agent_id} already initialized")
            return

        try:
            self._logger.info(f"Initializing agent {self.agent_id}")
            await self._do_initialize()
            self._initialized = True
            self.status = "active"
            self._logger.info(f"Agent {self.agent_id} initialized successfully")
        except Exception as e:
            self.status = "error"
            self._logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            raise

    @abstractmethod
    async def _do_initialize(self) -> None:
        """
        实际初始化逻辑（子类实现）
        """
        pass

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        处理请求

        Args:
            request: Agent请求对象

        Returns:
            AgentResponse: 处理结果
        """
        pass

    async def learn(self, feedback: Dict[str, Any]) -> None:
        """
        学习更新

        子类可重写此方法以实现学习逻辑

        Args:
            feedback: 反馈数据
        """
        self._logger.info(f"Agent {self.agent_id} received feedback: {feedback}")
        # 默认不做任何处理，子类可重写

    def export_config(self) -> Dict[str, Any]:
        """
        导出Agent配置

        Returns:
            配置字典
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "config": self.config.model_dump(),
            "course_id": self.course_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def reload_config(self, config: AgentConfig) -> None:
        """
        重载配置

        Args:
            config: 新配置
        """
        self.config = config
        self.updated_at = datetime.utcnow()
        self._logger.info(f"Agent {self.agent_id} config reloaded")

    async def shutdown(self) -> None:
        """
        关闭Agent

        子类可重写此方法以执行清理逻辑
        """
        self.status = "shutdown"
        self._logger.info(f"Agent {self.agent_id} shutdown")

    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized

    @property
    def is_active(self) -> bool:
        """是否处于活动状态"""
        return self.status == "active"

    def __repr__(self) -> str:
        return f"<BaseAgent id={self.agent_id} name={self.name} type={self.agent_type} status={self.status}>"


class SimpleAgent(BaseAgent):
    """
    简单Agent实现

    用于测试和演示
    """

    async def _do_initialize(self) -> None:
        """初始化"""
        # 模拟初始化延迟
        import asyncio
        await asyncio.sleep(0.1)

    async def process(self, request: AgentRequest) -> AgentResponse:
        """处理请求"""
        return AgentResponse(
            result=f"Processed: {request.query}",
            success=True,
            metadata={"agent_id": self.agent_id}
        )
