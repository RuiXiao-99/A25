"""
智能体管理路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from shared.models import (
    BaseResponse, PaginatedResponse, Agent, AgentConfig
)
from shared.exceptions import AgentNotFoundError, ValidationException
from ..services.agent_manager import AgentManager, get_agent_manager

router = APIRouter()


@router.get("", response_model=BaseResponse[PaginatedResponse[Agent]])
async def list_agents(
    course_id: Optional[str] = Query(None, description="课程ID筛选"),
    type: Optional[str] = Query(None, description="智能体类型筛选"),
    status: Optional[str] = Query("active", description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    获取智能体列表

    - **course_id**: 按课程ID筛选
    - **type**: 按类型筛选 (qa, grading, etc.)
    - **status**: 按状态筛选
    - **page**: 页码
    - **size**: 每页数量
    """
    result = await manager.list_agents(
        course_id=course_id,
        agent_type=type,
        status=status,
        page=page,
        size=size
    )
    return BaseResponse(data=result)


@router.post("", response_model=BaseResponse[Agent])
async def create_agent(
    name: str,
    type: str,
    course_id: Optional[str] = None,
    config: Optional[AgentConfig] = None,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    创建智能体

    - **name**: 智能体名称
    - **type**: 智能体类型 (qa, grading, warning, exercise)
    - **course_id**: 关联的课程ID
    - **config**: 智能体配置
    """
    if not name:
        raise ValidationException("Agent name is required", "name")

    if type not in ["qa", "grading", "warning", "exercise"]:
        raise ValidationException(
            f"Invalid agent type: {type}. Must be one of: qa, grading, warning, exercise",
            "type"
        )

    agent = await manager.create_agent(
        name=name,
        agent_type=type,
        course_id=course_id,
        config=config or AgentConfig()
    )
    return BaseResponse(data=agent)


@router.get("/{agent_id}", response_model=BaseResponse[Agent])
async def get_agent(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    获取智能体详情

    - **agent_id**: 智能体ID
    """
    agent = await manager.get_agent(agent_id)
    if not agent:
        raise AgentNotFoundError(agent_id)
    return BaseResponse(data=agent)


@router.put("/{agent_id}", response_model=BaseResponse[Agent])
async def update_agent(
    agent_id: str,
    name: Optional[str] = None,
    config: Optional[AgentConfig] = None,
    status: Optional[str] = None,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    更新智能体

    - **agent_id**: 智能体ID
    - **name**: 新名称
    - **config**: 新配置
    - **status**: 新状态
    """
    agent = await manager.get_agent(agent_id)
    if not agent:
        raise AgentNotFoundError(agent_id)

    updated_agent = await manager.update_agent(
        agent_id=agent_id,
        name=name,
        config=config,
        status=status
    )
    return BaseResponse(data=updated_agent)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    删除智能体

    - **agent_id**: 智能体ID
    """
    agent = await manager.get_agent(agent_id)
    if not agent:
        raise AgentNotFoundError(agent_id)

    await manager.delete_agent(agent_id)
    return BaseResponse(message=f"Agent {agent_id} deleted successfully")


@router.post("/{agent_id}/invoke")
async def invoke_agent(
    agent_id: str,
    request: dict,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    调用智能体

    - **agent_id**: 智能体ID
    - **request**: 请求数据
    """
    agent = await manager.get_agent(agent_id)
    if not agent:
        raise AgentNotFoundError(agent_id)

    result = await manager.invoke_agent(agent_id, request)
    return BaseResponse(data=result)


@router.post("/{agent_id}/reload")
async def reload_agent(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    重载智能体配置

    - **agent_id**: 智能体ID
    """
    agent = await manager.get_agent(agent_id)
    if not agent:
        raise AgentNotFoundError(agent_id)

    await manager.reload_agent(agent_id)
    return BaseResponse(message=f"Agent {agent_id} reloaded successfully")
