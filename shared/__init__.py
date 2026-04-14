"""
共享模块 - 提供跨服务共用的工具和模型
"""

from .models import BaseResponse, ErrorResponse, PaginatedResponse
from .config import get_settings, Settings
from .exceptions import (
    EduAgentException,
    AgentNotFoundError,
    CourseNotFoundError,
    StudentNotFoundError,
    ValidationException,
    AIServiceException
)
from .utils import (
    generate_uuid,
    get_current_timestamp,
    format_datetime,
    parse_datetime
)

__all__ = [
    # 响应模型
    'BaseResponse',
    'ErrorResponse',
    'PaginatedResponse',
    # 配置
    'get_settings',
    'Settings',
    # 异常
    'EduAgentException',
    'AgentNotFoundError',
    'CourseNotFoundError',
    'StudentNotFoundError',
    'ValidationException',
    'AIServiceException',
    # 工具函数
    'generate_uuid',
    'get_current_timestamp',
    'format_datetime',
    'parse_datetime'
]
