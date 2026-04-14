"""
钉钉平台适配器
"""

from typing import Any, Dict, List, Optional
import logging
import hashlib
import time

from .base import BaseAdapter
from shared.utils import generate_uuid

logger = logging.getLogger(__name__)


class DingTalkAdapter(BaseAdapter):
    """
    钉钉平台适配器

    实现与钉钉教育平台的对接:
    - 企业认证
    - 班级管理
    - 作业发布
    - 消息通知
    """

    VERSION = "1.0.0"
    PLATFORM_NAME = "钉钉教育平台"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.api_base = config.get("api_base", "https://api.dingtalk.com") if config else "https://api.dingtalk.com"
        self._corp_id = config.get("corp_id", "") if config else ""
        self._agent_id = config.get("agent_id", "") if config else ""

    async def authenticate(self, credentials: Dict) -> str:
        """
        钉钉平台认证

        Args:
            credentials: 包含 app_key, app_secret

        Returns:
            访问令牌
        """
        app_key = credentials.get("app_key")
        app_secret = credentials.get("app_secret")

        if not app_key or not app_secret:
            raise ValueError("Missing credentials: need app_key and app_secret")

        # 实际实现需要调用钉钉API获取access_token
        # 这里模拟认证过程
        token_data = f"{app_key}:{app_secret}:{time.time()}"
        self._token = f"dingtalk_{hashlib.md5(token_data.encode()).hexdigest()}"

        self._logger.info(f"Authenticated with DingTalk platform")
        return self._token

    async def get_courses(self) -> List[Dict]:
        """
        获取班级列表（钉钉中对应班级概念）
        """
        # 模拟返回班级列表
        return [
            {
                "course_id": "dingtalk_class_001",
                "name": "2023级计算机1班",
                "teacher": "王老师",
                "student_count": 45,
                "start_date": "2025-03-01",
                "end_date": "2025-07-01"
            },
            {
                "course_id": "dingtalk_class_002",
                "name": "2023级计算机2班",
                "teacher": "李老师",
                "student_count": 42,
                "start_date": "2025-03-01",
                "end_date": "2025-07-01"
            }
        ]

    async def get_course(self, course_id: str) -> Dict:
        """
        获取班级详情
        """
        # 模拟返回班级详情
        return {
            "course_id": course_id,
            "name": "2023级计算机1班",
            "teacher": "王老师",
            "teacher_id": "teacher_001",
            "student_count": 45,
            "start_date": "2025-03-01",
            "end_date": "2025-07-01",
            "description": "计算机科学基础课程",
            "class_code": "CS2023-1",
            "schedule": [
                {"day": "周一", "time": "08:00-09:40", "subject": "Python程序设计"},
                {"day": "周三", "time": "10:00-11:40", "subject": "数据结构"}
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
            # 同步班级
            courses = await self.get_courses()
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": len(courses),
                "success": len(courses),
                "failed": 0,
                "message": f"同步了{len(courses)}个班级"
            }

        elif sync_type == "students":
            # 同步学生
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": 45,
                "success": 44,
                "failed": 1,
                "message": "同步了44名学生"
            }

        elif sync_type == "assignments":
            # 同步作业
            return {
                "sync_id": sync_id,
                "sync_type": sync_type,
                "status": "completed",
                "total": 8,
                "success": 8,
                "failed": 0,
                "message": "同步了8份作业"
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

        return {
            "total": len(grades),
            "success": len(grades),
            "failed": 0,
            "message": "成绩推送成功"
        }

    async def send_message(
        self,
        user_ids: List[str],
        message: str,
        msg_type: str = "text"
    ) -> Dict:
        """
        发送消息

        Args:
            user_ids: 用户ID列表
            message: 消息内容
            msg_type: 消息类型 (text, link, markdown)

        Returns:
            发送结果
        """
        self._logger.info(f"Sending {msg_type} message to {len(user_ids)} users")

        # 模拟发送消息
        return {
            "message_id": generate_uuid(),
            "msg_type": msg_type,
            "recipient_count": len(user_ids),
            "sent_count": len(user_ids),
            "failed_count": 0,
            "message": "消息发送成功"
        }

    async def get_class_students(self, class_id: str) -> List[Dict]:
        """
        获取班级学生列表
        """
        return [
            {"student_id": "s001", "name": "张三", "student_number": "2023001"},
            {"student_id": "s002", "name": "李四", "student_number": "2023002"},
            {"student_id": "s003", "name": "王五", "student_number": "2023003"}
        ]

    async def create_homework(
        self,
        class_id: str,
        title: str,
        content: str,
        deadline: str
    ) -> Dict:
        """
        创建作业
        """
        homework_id = generate_uuid()

        self._logger.info(f"Creating homework for class {class_id}")

        return {
            "homework_id": homework_id,
            "class_id": class_id,
            "title": title,
            "content": content,
            "deadline": deadline,
            "status": "published",
            "created_at": time.time()
        }
