"""
共享数据模型
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="响应时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {},
                "timestamp": "2025-04-13T10:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(default=None, description="详细错误信息")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="响应时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "请求参数错误",
                "detail": "agent_id 不能为空",
                "timestamp": "2025-04-13T10:00:00Z"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页数量")
    pages: int = Field(default=0, description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }


class BaseEntity(BaseModel):
    """基础实体模型"""
    id: str = Field(description="实体ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="更新时间"
    )

    class Config:
        from_attributes = True


class Course(BaseEntity):
    """课程模型"""
    name: str = Field(description="课程名称")
    code: str = Field(description="课程代码")
    description: Optional[str] = Field(default=None, description="课程描述")
    status: str = Field(default="active", description="课程状态")


class AgentConfig(BaseModel):
    """智能体配置"""
    model: str = Field(default="glm-4", description="使用的模型")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=2048, ge=1, le=8192, description="最大token数")
    system_prompt: Optional[str] = Field(default=None, description="系统提示词")
    knowledge_base_ids: List[str] = Field(
        default_factory=list,
        description="关联的知识库ID列表"
    )


class Agent(BaseEntity):
    """智能体模型"""
    name: str = Field(description="智能体名称")
    type: str = Field(description="智能体类型")
    course_id: Optional[str] = Field(default=None, description="关联课程ID")
    config: AgentConfig = Field(
        default_factory=AgentConfig,
        description="智能体配置"
    )
    status: str = Field(default="active", description="智能体状态")


class Student(BaseEntity):
    """学生模型"""
    user_id: str = Field(description="用户ID")
    name: str = Field(description="学生姓名")
    email: Optional[str] = Field(default=None, description="邮箱")
    profile_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="画像数据"
    )


class Assignment(BaseEntity):
    """作业模型"""
    course_id: str = Field(description="课程ID")
    title: str = Field(description="作业标题")
    content: str = Field(description="作业内容")
    type: str = Field(description="作业类型")
    knowledge_points: List[str] = Field(
        default_factory=list,
        description="涉及的知识点"
    )
    deadline: Optional[datetime] = Field(default=None, description="截止时间")


class Submission(BaseEntity):
    """提交记录模型"""
    assignment_id: str = Field(description="作业ID")
    student_id: str = Field(description="学生ID")
    content: str = Field(description="提交内容")
    file_urls: List[str] = Field(
        default_factory=list,
        description="附件URL列表"
    )
    annotations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="批注列表"
    )
    score: Optional[float] = Field(default=None, description="分数")
    feedback: Optional[str] = Field(default=None, description="反馈")
    status: str = Field(default="submitted", description="状态")


class KnowledgePoint(BaseModel):
    """知识点模型"""
    id: str = Field(description="知识点ID")
    name: str = Field(description="知识点名称")
    description: Optional[str] = Field(default=None, description="描述")
    parent_id: Optional[str] = Field(default=None, description="父知识点ID")
    course_id: str = Field(description="所属课程ID")
    tags: List[str] = Field(default_factory=list, description="标签")


class LearningRecord(BaseModel):
    """学习记录模型"""
    student_id: str = Field(description="学生ID")
    course_id: str = Field(description="课程ID")
    knowledge_point_id: str = Field(description="知识点ID")
    mastery_level: float = Field(
        default=0,
        ge=0,
        le=1,
        description="掌握程度(0-1)"
    )
    practice_count: int = Field(default=0, description="练习次数")
    correct_count: int = Field(default=0, description="正确次数")
    last_practice_at: Optional[datetime] = Field(
        default=None,
        description="最后练习时间"
    )


class Warning(BaseEntity):
    """预警模型"""
    student_id: str = Field(description="学生ID")
    course_id: str = Field(description="课程ID")
    level: str = Field(description="预警级别")
    type: str = Field(description="预警类型")
    description: str = Field(description="预警描述")
    knowledge_points: List[str] = Field(
        default_factory=list,
        description="相关知识点"
    )
