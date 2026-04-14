"""
Agent管理器
"""

import asyncio
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import logging
from dataclasses import asdict

from shared.models import Agent, AgentConfig, PaginatedResponse
from shared.exceptions import AgentNotFoundError
from shared.utils import generate_uuid
from .base_agent import BaseAgent, SimpleAgent, AgentRequest, AgentResponse

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Agent管理器

    负责:
    - Agent的注册、发现、调用
    - Agent生命周期管理
    - Agent状态监控
    """

    def __init__(self):
        # 内存存储（生产环境应使用数据库）
        self._agents: Dict[str, Agent] = {}
        self._agent_instances: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "simple": SimpleAgent
        }
        self._lock = asyncio.Lock()

    async def register_agent_class(self, agent_type: str, cls: Type[BaseAgent]) -> None:
        """
        注册Agent类

        Args:
            agent_type: Agent类型标识
            cls: Agent类
        """
        async with self._lock:
            self._agent_classes[agent_type] = cls
            logger.info(f"Registered agent class: {agent_type}")

    async def create_agent(
        self,
        name: str,
        agent_type: str,
        course_id: Optional[str] = None,
        config: Optional[AgentConfig] = None
    ) -> Agent:
        """
        创建Agent

        Args:
            name: Agent名称
            agent_type: Agent类型
            course_id: 关联课程ID
            config: Agent配置

        Returns:
            创建的Agent
        """
        agent_id = generate_uuid()

        agent = Agent(
            id=agent_id,
            name=name,
            type=agent_type,
            course_id=course_id,
            config=config or AgentConfig(),
            status="created",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        async with self._lock:
            self._agents[agent_id] = agent

        logger.info(f"Created agent: {agent_id} - {name}")
        return agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        获取Agent

        Args:
            agent_id: Agent ID

        Returns:
            Agent对象或None
        """
        return self._agents.get(agent_id)

    async def list_agents(
        self,
        course_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginatedResponse[Agent]:
        """
        列出Agent

        Args:
            course_id: 课程ID筛选
            agent_type: 类型筛选
            status: 状态筛选
            page: 页码
            size: 每页数量

        Returns:
            分页结果
        """
        agents = list(self._agents.values())

        # 筛选
        if course_id:
            agents = [a for a in agents if a.course_id == course_id]
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]
        if status:
            agents = [a for a in agents if a.status == status]

        # 排序
        agents.sort(key=lambda x: x.created_at, reverse=True)

        # 分页
        total = len(agents)
        start = (page - 1) * size
        end = start + size
        items = agents[start:end]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    async def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        status: Optional[str] = None
    ) -> Agent:
        """
        更新Agent

        Args:
            agent_id: Agent ID
            name: 新名称
            config: 新配置
            status: 新状态

        Returns:
            更新后的Agent
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        async with self._lock:
            if name:
                agent.name = name
            if config:
                agent.config = config
                # 如果Agent实例已存在，重载配置
                if agent_id in self._agent_instances:
                    await self._agent_instances[agent_id].reload_config(config)
            if status:
                agent.status = status

            agent.updated_at = datetime.utcnow()
            self._agents[agent_id] = agent

        logger.info(f"Updated agent: {agent_id}")
        return agent

    async def delete_agent(self, agent_id: str) -> None:
        """
        删除Agent

        Args:
            agent_id: Agent ID
        """
        async with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
            if agent_id in self._agent_instances:
                await self._agent_instances[agent_id].shutdown()
                del self._agent_instances[agent_id]

        logger.info(f"Deleted agent: {agent_id}")

    async def invoke_agent(
        self,
        agent_id: str,
        request: Dict[str, Any]
    ) -> AgentResponse:
        """
        调用Agent

        Args:
            agent_id: Agent ID
            request: 请求数据

        Returns:
            响应结果
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        # 获取或创建Agent实例
        instance = await self._get_or_create_instance(agent_id, agent)

        # 构建请求
        agent_request = AgentRequest(
            query=request.get("query", ""),
            context=request.get("context", {}),
            session_id=request.get("session_id"),
            user_id=request.get("user_id"),
            metadata=request.get("metadata", {})
        )

        # 调用处理
        try:
            response = await instance.process(agent_request)
            return response
        except Exception as e:
            logger.error(f"Agent {agent_id} process error: {e}")
            return AgentResponse(
                result=None,
                success=False,
                error=str(e)
            )

    async def reload_agent(self, agent_id: str) -> None:
        """
        重载Agent

        Args:
            agent_id: Agent ID
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        async with self._lock:
            # 销毁旧实例
            if agent_id in self._agent_instances:
                await self._agent_instances[agent_id].shutdown()
                del self._agent_instances[agent_id]

        logger.info(f"Reloaded agent: {agent_id}")

    async def _get_or_create_instance(
        self,
        agent_id: str,
        agent: Agent
    ) -> BaseAgent:
        """
        获取或创建Agent实例
        """
        if agent_id in self._agent_instances:
            return self._agent_instances[agent_id]

        # 获取Agent类
        agent_cls = self._agent_classes.get(agent.type, SimpleAgent)

        # 创建实例
        instance = agent_cls(
            agent_id=agent_id,
            name=agent.name,
            agent_type=agent.type,
            config=agent.config,
            course_id=agent.course_id
        )

        # 初始化
        await instance.initialize()

        async with self._lock:
            self._agent_instances[agent_id] = instance

        return instance

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        获取Agent状态

        Args:
            agent_id: Agent ID

        Returns:
            状态信息
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        instance = self._agent_instances.get(agent_id)

        return {
            "agent_id": agent_id,
            "status": agent.status,
            "initialized": instance.is_initialized if instance else False,
            "active": instance.is_active if instance else False,
            "last_updated": agent.updated_at.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态
        """
        return {
            "total_agents": len(self._agents),
            "active_instances": len(self._agent_instances),
            "registered_classes": list(self._agent_classes.keys())
        }


# FastAPI依赖注入
async def get_agent_manager() -> AgentManager:
    """获取AgentManager实例"""
    from fastapi import Request
    # 这里返回一个全局实例，实际使用时通过app.state注入
    return AgentManager()
