"""
适配器注册表
"""

from typing import Any, Dict, List, Optional, Type
import logging

from shared.exceptions import PlatformAdapterException
from ..adapters.base import BaseAdapter
from ..adapters.chaoxing import ChaoxingAdapter
from ..adapters.dingtalk import DingTalkAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    适配器注册表

    管理:
    - 适配器注册与发现
    - 适配器实例缓存
    - 平台配置管理
    """

    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._adapter_classes: Dict[str, Type[BaseAdapter]] = {
            "chaoxing": ChaoxingAdapter,
            "dingtalk": DingTalkAdapter
        }
        self._configs: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        """初始化注册表"""
        logger.info("Initializing adapter registry")

        # 注册内置适配器
        for platform, cls in self._adapter_classes.items():
            logger.info(f"Registered adapter: {platform}")

    async def register_adapter(
        self,
        platform: str,
        adapter: BaseAdapter
    ) -> None:
        """注册适配器"""
        self._adapters[platform] = adapter
        logger.info(f"Registered adapter instance: {platform}")

    async def get_adapter(self, platform: str) -> Optional[BaseAdapter]:
        """获取适配器"""
        if platform in self._adapters:
            return self._adapters[platform]

        # 动态创建适配器实例
        if platform in self._adapter_classes:
            adapter_cls = self._adapter_classes[platform]
            config = self._configs.get(platform, {})
            adapter = adapter_cls(config)
            self._adapters[platform] = adapter
            return adapter

        return None

    async def list_adapters(self) -> List[Dict[str, Any]]:
        """列出所有适配器"""
        result = []
        for platform, cls in self._adapter_classes.items():
            adapter_info = {
                "platform": platform,
                "name": cls.__name__,
                "version": getattr(cls, "VERSION", "1.0.0"),
                "status": "registered",
                "features": cls.get_features()
            }

            if platform in self._adapters:
                adapter_info["status"] = "active"

            result.append(adapter_info)

        return result

    def set_config(self, platform: str, config: Dict) -> None:
        """设置平台配置"""
        self._configs[platform] = config

    def get_config(self, platform: str) -> Optional[Dict]:
        """获取平台配置"""
        return self._configs.get(platform)


# FastAPI依赖注入
def get_adapter_registry() -> AdapterRegistry:
    """获取AdapterRegistry实例"""
    return AdapterRegistry()
