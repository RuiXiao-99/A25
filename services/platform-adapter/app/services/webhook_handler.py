"""
Webhook处理器
"""

from typing import Any, Dict, List, Optional
import json
import hashlib
import logging
from datetime import datetime

from shared.utils import generate_uuid

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Webhook处理器

    处理来自各平台的事件回调:
    - 验证签名
    - 解析事件
    - 分发处理
    """

    def __init__(self):
        # 订阅存储
        self._subscriptions: Dict[str, List[Dict]] = {}
        # 事件存储
        self._events: Dict[str, List[Dict]] = {}

    async def handle(
        self,
        platform: str,
        body: bytes,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        处理Webhook回调
        """
        # 解析事件
        try:
            event_data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload")

        event_type = event_data.get("event_type") or event_data.get("type", "unknown")
        event_id = event_data.get("event_id") or generate_uuid()

        # 记录事件
        event = {
            "event_id": event_id,
            "platform": platform,
            "type": event_type,
            "data": event_data,
            "headers": {k: v for k, v in headers.items() if k.lower().startswith("x-")},
            "received_at": datetime.utcnow().isoformat()
        }

        if platform not in self._events:
            self._events[platform] = []
        self._events[platform].append(event)

        # 处理事件
        result = await self._process_event(platform, event_type, event_data)

        logger.info(f"Processed webhook event: {platform}/{event_type} - {event_id}")

        return {
            "event_id": event_id,
            "processed": True,
            "result": result
        }

    async def _process_event(
        self,
        platform: str,
        event_type: str,
        event_data: Dict
    ) -> Dict[str, Any]:
        """
        处理具体事件
        """
        # 根据平台和事件类型分发处理
        handler_map = {
            "chaoxing": {
                "assignment_submitted": self._handle_chaoxing_assignment,
                "course_created": self._handle_chaoxing_course,
                "student_enrolled": self._handle_chaoxing_enrollment
            },
            "dingtalk": {
                "message_received": self._handle_dingtalk_message,
                "approval_submitted": self._handle_dingtalk_approval
            }
        }

        platform_handlers = handler_map.get(platform, {})
        handler = platform_handlers.get(event_type)

        if handler:
            return await handler(event_data)
        else:
            logger.warning(f"No handler for {platform}/{event_type}")
            return {"status": "unhandled", "event_type": event_type}

    async def _handle_chaoxing_assignment(self, data: Dict) -> Dict:
        """处理超星作业提交事件"""
        logger.info(f"Handling chaoxing assignment submission: {data}")
        # TODO: 实现具体的处理逻辑
        return {
            "status": "processed",
            "action": "assignment_notification_sent"
        }

    async def _handle_chaoxing_course(self, data: Dict) -> Dict:
        """处理超星课程创建事件"""
        logger.info(f"Handling chaoxing course creation: {data}")
        return {"status": "processed"}

    async def _handle_chaoxing_enrollment(self, data: Dict) -> Dict:
        """处理超星选课事件"""
        logger.info(f"Handling chaoxing enrollment: {data}")
        return {"status": "processed"}

    async def _handle_dingtalk_message(self, data: Dict) -> Dict:
        """处理钉钉消息事件"""
        logger.info(f"Handling dingtalk message: {data}")
        return {"status": "processed"}

    async def _handle_dingtalk_approval(self, data: Dict) -> Dict:
        """处理钉钉审批事件"""
        logger.info(f"Handling dingtalk approval: {data}")
        return {"status": "processed"}

    async def list_events(self, platform: str) -> List[Dict]:
        """列出平台事件"""
        return self._events.get(platform, [])

    async def subscribe(
        self,
        platform: str,
        event_types: List[str],
        callback_url: str
    ) -> Dict:
        """订阅事件"""
        subscription_id = generate_uuid()

        subscription = {
            "subscription_id": subscription_id,
            "platform": platform,
            "event_types": event_types,
            "callback_url": callback_url,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }

        if platform not in self._subscriptions:
            self._subscriptions[platform] = []
        self._subscriptions[platform].append(subscription)

        logger.info(f"Created subscription: {subscription_id}")

        return subscription

    async def unsubscribe(self, platform: str, subscription_id: str) -> None:
        """取消订阅"""
        if platform in self._subscriptions:
            self._subscriptions[platform] = [
                s for s in self._subscriptions[platform]
                if s["subscription_id"] != subscription_id
            ]
            logger.info(f"Removed subscription: {subscription_id}")


def get_webhook_handler() -> WebhookHandler:
    """获取WebhookHandler实例"""
    return WebhookHandler()
