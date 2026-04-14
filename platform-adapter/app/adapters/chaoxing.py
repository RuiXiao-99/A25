"""
超星平台适配器
"""

from typing import Any, Dict, List, Optional
import logging
import hashlib
import time

from .base import BaseAdapter
from shared.utils import generate_uuid

logger = logging.getLogger(__name__)


class ChaoxingAdapter(BaseAdapter):
    """
    超星平台适配器

    实现与超星学习平台的对接:
    - 用户认证
    - 课程管理
    - 作业提交
    - 成绩同步
    """

    VERSION = "1.0.0"
    PLATFORM_NAME = "超星学习平台"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.api_base = config.get("api_base", "https://api.chaoxing.com") if config else "https://api.chaoxing.com"

    async def authenticate(self, credentials: Dict) -> str:
        """
        超星平台认证

        Args:
            credentials: 包含 username, password 或 api_key

        Returns:
            访问令牌
        """
        username = credentials.get("username")
        password = credentials.get("password")
        api_key = credentials.get("api_key")

        if api_key:
            # API Key认证
            self._token = f"Bearer {api_key}"
        elif username and password:
            # 用户名密码认证
            # 实际实现需要调用超星API
            # 这里模拟认证过程
            token_data = f"{username}:{password}:{time.time()}"
            self._token = f"chaoxing_{hashlib.md5(token_data.encode()).hexdigest()}"
        else:
            raise ValueError("Missing credentials: need username/password or api_key")

        self._logger.info(f"Authenticated with Chaoxing platform")
        return self._token

    async def get_courses(self) -> List[Dict]:
        """
        获取课程列表
        """
        # 模拟返回课程列表
        # 实际实现需要调用超星API
        return [
            {
                "course_id": "chaoxing_course_001",
                "name": "Python程序设计",
                "teacher": "张老师",
                "student_count": 120,
                "start_date": "2025-03-01",
                "end_date": "2025-07-01"
            },
            {
                "course_id": "chaoxing_course_002",
                "name": "数据结构与算法",
                "teacher": "李老师",
                "student_count": 95,
                "start_date": "2025-03-01",
                "end_date": "2025-07-01"
            }
        ]

    async def get_course(self, course_id: str) -> Dict:
        """
        获取课程详情
        """
        # 模拟返回课程详情
        return {
            "course_id": course_id,
            "name": "Python程序设计",
            "teacher": "张老师",
            "teacher_id": "teacher_001",
            "student_count": 120,
            "start_date": "2025-03-01",
            "end_date": "2025-07-01",
            "description": "Python编程基础课程",
            "chapters": [
                {"id": "ch1", "name": "Python简介", "order": 1},
                {"id": "ch2", "name": "变量与数据类型", "order": 2},
                {"id": "ch3", "name": "控制结构", "order": 3}
            ],
            "assignments": [
                {"id": "hw1", "name": "第一次作业", "deadline": "2025-04-15"},
                {"id": "hw2", "name": "第二次作业", "deadline": "2025-04-30"}
            ]
        }

    async def sync_data(
        self,
        sync_type: str,
        course_id: Optional[str] = None
    ) -> Dict:
        """
        同步数据
        """
        sync_id = generate_uuid()

        if sync_type == "courses":
            # 同步课程
            courses = await self.get_courses()
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": len(courses),
                "success": len(courses),
                "failed": 0,
                "message": f"同步了{len(courses)}门课程"
            }

        elif sync_type == "students":
            # 同步学生
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": 120,
                "success": 118,
                "failed": 2,
                "message": "同步了118名学生"
            }

        elif sync_type == "assignments":
            # 同步作业
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": 10,
                "success": 10,
                "failed": 0,
                "message": "同步了10份作业"
            }

        elif sync_type == "grades":
            # 同步成绩
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": 118,
                "success": 115,
                "failed": 3,
                "message": "同步了115条成绩记录"
            }

        else:
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "failed",
                "total": 0,
                "success": 0,
                "failed": 0,
                "message": f"未知的同步类型: {sync_type}"
            }

    async def submit_assignment(
        self,
        assignment_id: str,
        student_id: str,
        content: str,
        file_urls: Optional[List[str]] = None
    ) -> Dict:
        """
        提交作业
        """
        submission_id = generate_uuid()

        self._logger.info(f"Submitting assignment {assignment_id} for student {student_id}")

        # 模拟提交
        return {
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "status": "submitted",
            "submitted_at": time.time(),
            "message": "作业提交成功"
        }

    async def push_grades(self, grades: List[Dict]) -> Dict:
        """
        推送成绩
        """
        self._logger.info(f"Pushing {len(grades)} grade records")

        success_count = 0
        failed_count = 0
        errors = []

        for grade in grades:
            try:
                # 模拟推送成绩
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(str(e))

        return {
            "total": len(grades),
            "success": success_count,
            "failed": failed_count,
            "errors": errors[:10]  # 只返回前10个错误
        }

    async def get_students(self, course_id: str) -> List[Dict]:
        """
        获取课程学生列表
        """
        # 模拟返回学生列表
        return [
            {"student_id": "s001", "name": "张三", "student_number": "2023001"},
            {"student_id": "s002", "name": "李四", "student_number": "2023002"},
            {"student_id": "s003", "name": "王五", "student_number": "2023003"}
        ]

    async def get_assignments(self, course_id: str) -> List[Dict]:
        """
        获取课程作业列表
        """
        return [
            {
                "assignment_id": "hw1",
                "title": "Python基础练习",
                "deadline": "2025-04-15T23:59:59",
                "total_score": 100,
                "type": "homework"
            },
            {
                "assignment_id": "hw2",
                "title": "函数与模块",
                "deadline": "2025-04-30T23:59:59",
                "total_score": 100,
                "type": "homework"
            }
        ]
