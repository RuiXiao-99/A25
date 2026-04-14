"""
平台适配器基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    平台适配器基类

    所有平台适配器必须继承此类并实现以下方法:
    - authenticate(): 平台认证
    - get_courses(): 获取课程列表
    - get_course(): 获取课程详情
    - sync_data(): 同步数据
    """

    VERSION = "1.0.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._token: Optional[str] = None
        self._initialized = False
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def authenticate(self, credentials: Dict) -> str:
        """
        平台认证

        Args:
            credentials: 认证凭证（如用户名密码、API Key等）

        Returns:
            访问令牌
        """
        pass

    @abstractmethod
    async def get_courses(self) -> List[Dict]:
        """
        获取课程列表

        Returns:
            课程信息列表
        """
        pass

    @abstractmethod
    async def get_course(self, course_id: str) -> Dict:
        """
        获取课程详情

        Args:
            course_id: 课程ID

        Returns:
            课程详情
        """
        pass

    @abstractmethod
    async def sync_data(
        self,
        sync_type: str,
        course_id: Optional[str] = None
    ) -> Dict:
        """
        同步数据

        Args:
            sync_type: 同步类型 (courses, students, assignments, grades)
            course_id: 课程ID（可选）

        Returns:
            同步结果
        """
        pass

    async def submit_assignment(
        self,
        assignment_id: str,
        student_id: str,
        content: str,
        file_urls: Optional[List[str]] = None
    ) -> Dict:
        """
        提交作业

        Args:
            assignment_id: 作业ID
            student_id: 学生ID
            content: 内容
            file_urls: 文件URL列表

        Returns:
            提交结果
        """
        raise NotImplementedError("submit_assignment not implemented")

    async def push_grades(self, grades: List[Dict]) -> Dict:
        """
        推送成绩

        Args:
            grades: 成绩列表

        Returns:
            推送结果
        """
        raise NotImplementedError("push_grades not implemented")

    async def test_connection(self) -> Dict:
        """
        测试连接

        Returns:
            测试结果
        """
        try:
            # 尝试获取课程列表来测试连接
            courses = await self.get_courses()
            return {
                "status": "success",
                "message": "Connection successful",
                "course_count": len(courses)
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": str(e)
            }

    @classmethod
    def get_features(cls) -> List[str]:
        """
        获取适配器支持的功能

        Returns:
            功能列表
        """
        features = ["courses", "sync"]
        try:
            cls.submit_assignment(None, None, None)  # type: ignore
        except NotImplementedError:
            pass
        else:
            features.append("submit")

        try:
            cls.push_grades(None)  # type: ignore
        except NotImplementedError:
            pass
        else:
            features.append("grades")

        return features

    def set_token(self, token: str) -> None:
        """设置访问令牌"""
        self._token = token

    def get_token(self) -> Optional[str]:
        """获取访问令牌"""
        return self._token
