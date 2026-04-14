"""
自定义异常模块
"""

from typing import Any, Dict, Optional


class EduAgentException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        code: int = 500,
        detail: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.detail = detail
        self.data = data or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "code": self.code,
            "message": self.message,
            "detail": self.detail
        }
        if self.data:
            result["data"] = self.data
        return result


class AgentNotFoundError(EduAgentException):
    """Agent未找到异常"""

    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            code=404,
            detail="The specified agent does not exist or has been deleted.",
            data={"agent_id": agent_id}
        )


class CourseNotFoundError(EduAgentException):
    """课程未找到异常"""

    def __init__(self, course_id: str):
        super().__init__(
            message=f"Course not found: {course_id}",
            code=404,
            detail="The specified course does not exist.",
            data={"course_id": course_id}
        )


class StudentNotFoundError(EduAgentException):
    """学生未找到异常"""

    def __init__(self, student_id: str):
        super().__init__(
            message=f"Student not found: {student_id}",
            code=404,
            detail="The specified student does not exist.",
            data={"student_id": student_id}
        )


class ValidationException(EduAgentException):
    """验证异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code=400,
            detail=f"Validation failed for field: {field}" if field else message,
            data={"field": field} if field else {}
        )


class AIServiceException(EduAgentException):
    """AI服务异常"""

    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(
            message=f"AI service error: {message}",
            code=503,
            detail="The AI service is temporarily unavailable. Please try again later.",
            data={"provider": provider}
        )


class RateLimitException(EduAgentException):
    """限流异常"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            code=429,
            detail=f"Too many requests. Please retry after {retry_after} seconds.",
            data={"retry_after": retry_after}
        )


class AuthenticationException(EduAgentException):
    """认证异常"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code=401,
            detail="Invalid credentials or expired token."
        )


class AuthorizationException(EduAgentException):
    """授权异常"""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            code=403,
            detail="You do not have permission to access this resource."
        )


class DatabaseException(EduAgentException):
    """数据库异常"""

    def __init__(self, message: str, operation: str = "unknown"):
        super().__init__(
            message=f"Database error: {message}",
            code=500,
            detail="A database error occurred. Please contact support if the problem persists.",
            data={"operation": operation}
        )


class CacheException(EduAgentException):
    """缓存异常"""

    def __init__(self, message: str):
        super().__init__(
            message=f"Cache error: {message}",
            code=500,
            detail="A cache error occurred."
        )


class PlatformAdapterException(EduAgentException):
    """平台适配器异常"""

    def __init__(self, platform: str, message: str):
        super().__init__(
            message=f"Platform adapter error ({platform}): {message}",
            code=500,
            detail=f"Failed to communicate with {platform} platform.",
            data={"platform": platform}
        )
