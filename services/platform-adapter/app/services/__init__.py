"""
服务模块
"""

from .adapter_registry import AdapterRegistry, get_adapter_registry
from .webhook_handler import WebhookHandler, get_webhook_handler

__all__ = [
    "AdapterRegistry", "get_adapter_registry",
    "WebhookHandler", "get_webhook_handler"
]
