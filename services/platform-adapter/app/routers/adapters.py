"""
平台适配器路由
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.models import BaseResponse
from shared.exceptions import ValidationException, PlatformAdapterException
from ..services.adapter_registry import AdapterRegistry, get_adapter_registry

router = APIRouter()


class AdapterInfo(BaseModel):
    """适配器信息"""
    platform: str
    name: str
    version: str
    status: str
    features: List[str]


class CourseInfo(BaseModel):
    """课程信息"""
    course_id: str
    name: str
    teacher: str
    student_count: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SyncRequest(BaseModel):
    """同步请求"""
    sync_type: str = Field(..., description="同步类型: courses, students, assignments, grades")
    course_id: Optional[str] = None


class SyncResult(BaseModel):
    """同步结果"""
    sync_id: str
    sync_type: str
    status: str
    total: int
    success: int
    failed: int
    message: str


@router.get("", response_model=BaseResponse[List[AdapterInfo]])
async def list_adapters(
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    获取已注册的适配器列表
    """
    adapters = await registry.list_adapters()
    return BaseResponse(data=adapters)


@router.get("/{platform}", response_model=BaseResponse[AdapterInfo])
async def get_adapter(
    platform: str,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    获取指定平台的适配器信息
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")
    return BaseResponse(data=adapter)


@router.post("/{platform}/auth")
async def authenticate(
    platform: str,
    credentials: dict,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    平台认证

    使用平台凭证获取访问令牌
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    token = await adapter.authenticate(credentials)
    return BaseResponse(data={"token": token})


@router.get("/{platform}/courses", response_model=BaseResponse[List[CourseInfo]])
async def get_courses(
    platform: str,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    获取平台课程列表
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    courses = await adapter.get_courses()
    return BaseResponse(data=courses)


@router.get("/{platform}/courses/{course_id}")
async def get_course(
    platform: str,
    course_id: str,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    获取课程详情
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    course = await adapter.get_course(course_id)
    return BaseResponse(data=course)


@router.post("/{platform}/sync", response_model=BaseResponse[SyncResult])
async def sync_data(
    platform: str,
    request: SyncRequest,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    同步平台数据

    支持同步课程、学生、作业、成绩等数据
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    result = await adapter.sync_data(
        sync_type=request.sync_type,
        course_id=request.course_id
    )
    return BaseResponse(data=result)


@router.post("/{platform}/submit")
async def submit_assignment(
    platform: str,
    assignment_id: str,
    student_id: str,
    content: str,
    file_urls: List[str] = None,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    提交作业到平台
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    result = await adapter.submit_assignment(
        assignment_id=assignment_id,
        student_id=student_id,
        content=content,
        file_urls=file_urls or []
    )
    return BaseResponse(data=result)


@router.post("/{platform}/grades")
async def push_grades(
    platform: str,
    grades: List[dict],
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    推送成绩到平台
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    result = await adapter.push_grades(grades)
    return BaseResponse(data=result)


@router.post("/{platform}/test")
async def test_connection(
    platform: str,
    registry: AdapterRegistry = Depends(get_adapter_registry)
):
    """
    测试平台连接
    """
    adapter = await registry.get_adapter(platform)
    if not adapter:
        raise PlatformAdapterException(platform, "Adapter not found")

    result = await adapter.test_connection()
    return BaseResponse(data=result)
