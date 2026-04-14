"""
Agent管理器 - 数据库版本

使用SQLite持久化存储Agent数据
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import logging

from shared.models import Agent, AgentConfig, PaginatedResponse
from shared.exceptions import AgentNotFoundError
from shared.utils import generate_uuid
from shared.database import dao_factory, db_manager
from .base_agent import BaseAgent, SimpleAgent, AgentRequest, AgentResponse

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Agent管理器 (数据库版本)

    负责:
    - Agent的注册、发现、调用
    - Agent生命周期管理
    - Agent状态监控
    """

    def __init__(self):
        self._agent_instances: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "simple": SimpleAgent
        }
        self._lock = asyncio.Lock()
        self._dao = dao_factory.agent()

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
        now = datetime.utcnow()

        agent = Agent(
            id=agent_id,
            name=name,
            type=agent_type,
            course_id=course_id,
            config=config or AgentConfig(),
            status="created",
            created_at=now,
            updated_at=now
        )

        # 保存到数据库
        await self._dao.insert({
            "id": agent_id,
            "name": name,
            "type": agent_type,
            "course_id": course_id,
            "config": agent.config.model_dump(),
            "status": "created",
            "created_at": now,
            "updated_at": now
        })

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
        row = await self._dao.get_by_id(agent_id)
        if not row:
            return None
        
        return self._row_to_agent(row)

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
        # 构建查询条件
        conditions = []
        params = []
        
        if course_id:
            conditions.append("course_id = ?")
            params.append(course_id)
        if agent_type:
            conditions.append("type = ?")
            params.append(agent_type)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        # 构建SQL
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as count FROM agents WHERE {where_clause}"
        async with db_manager.connection.execute(count_sql, params) as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0
        
        # 获取分页数据
        offset = (page - 1) * size
        sql = f"""
            SELECT * FROM agents 
            WHERE {where_clause} 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        
        rows = await db_manager.fetchall(sql, tuple(params))
        agents = [self._row_to_agent(row) for row in rows]

        return PaginatedResponse(
            items=agents,
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
        agent = await self.get_agent(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        update_data = {}
        if name:
            update_data["name"] = name
        if config:
            update_data["config"] = config.model_dump()
            # 如果Agent实例已存在，重载配置
            if agent_id in self._agent_instances:
                await self._agent_instances[agent_id].reload_config(config)
        if status:
            update_data["status"] = status

        if update_data:
            await self._dao.update(agent_id, update_data)

        logger.info(f"Updated agent: {agent_id}")
        return await self.get_agent(agent_id)

    async def delete_agent(self, agent_id: str) -> None:
        """
        删除Agent

        Args:
            agent_id: Agent ID
        """
        async with self._lock:
            # 销毁实例
            if agent_id in self._agent_instances:
                await self._agent_instances[agent_id].shutdown()
                del self._agent_instances[agent_id]
            
            # 从数据库删除
            await self._dao.delete(agent_id)

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
        agent = await self.get_agent(agent_id)
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
        agent = await self.get_agent(agent_id)
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
        agent = await self.get_agent(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        instance = self._agent_instances.get(agent_id)

        return {
            "agent_id": agent_id,
            "status": agent.status,
            "initialized": instance.is_initialized if instance else False,
            "active": instance.is_active if instance else False,
            "last_updated": agent.updated_at.isoformat() if agent.updated_at else None
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            健康状态
        """
        # 获取总数
        count_sql = "SELECT COUNT(*) as count FROM agents"
        async with db_manager.connection.execute(count_sql) as cursor:
            row = await cursor.fetchone()
            total_agents = row[0] if row else 0

        return {
            "total_agents": total_agents,
            "active_instances": len(self._agent_instances),
            "registered_classes": list(self._agent_classes.keys())
        }

    def _row_to_agent(self, row: Dict[str, Any]) -> Agent:
        """将数据库行转换为Agent对象"""
        config_data = row.get("config")
        if isinstance(config_data, str):
            config_data = json.loads(config_data)
        
        config = AgentConfig(**config_data) if config_data else AgentConfig()
        
        return Agent(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            course_id=row.get("course_id"),
            config=config,
            status=row.get("status", "active"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.utcnow()
        )


# FastAPI依赖注入
async def get_agent_manager() -> AgentManager:
    """获取AgentManager实例"""
    return AgentManager()
