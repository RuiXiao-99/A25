"""
Webhook回调路由
"""

from fastapi import APIRouter, Request, Depends
from typing import Dict, Any
import logging

from shared.models import BaseResponse
from ..services.webhook_handler import WebhookHandler, get_webhook_handler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{platform}")
async def handle_webhook(
    platform: str,
    request: Request,
    handler: WebhookHandler = Depends(get_webhook_handler)
):
    """
    处理平台Webhook回调

    支持以下平台:
    - chaoxing: 超星平台
    - dingtalk: 钉钉平台
    """
    # 获取请求体
    body = await request.body()
    headers = dict(request.headers)

    # 验证签名（如果需要）
    # signature = headers.get("x-webhook-signature")

    try:
        # 处理Webhook
        result = await handler.handle(
            platform=platform,
            body=body,
            headers=headers
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/{platform}/events")
async def list_webhook_events(
    platform: str,
    handler: WebhookHandler = Depends(get_webhook_handler)
):
    """
    获取Webhook事件列表
    """
    events = await handler.list_events(platform)
    return BaseResponse(data=events)


@router.post("/{platform}/subscribe")
async def subscribe_webhook(
    platform: str,
    event_types: list,
    callback_url: str,
    handler: WebhookHandler = Depends(get_webhook_handler)
):
    """
    订阅Webhook事件
    """
    result = await handler.subscribe(
        platform=platform,
        event_types=event_types,
        callback_url=callback_url
    )
    return BaseResponse(data=result)


@router.delete("/{platform}/subscribe/{subscription_id}")
async def unsubscribe_webhook(
    platform: str,
    subscription_id: str,
    handler: WebhookHandler = Depends(get_webhook_handler)
):
    """
    取消Webhook订阅
    """
    await handler.unsubscribe(platform, subscription_id)
    return BaseResponse(message=f"Unsubscribed {subscription_id}")
