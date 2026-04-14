"""
适配器注册表 - 数据库版本

使用SQLite持久化存储平台配置
"""

import json
from typing import Any, Dict, List, Optional, Type
import logging

from shared.exceptions import PlatformAdapterException
from shared.database import dao_factory, db_manager
from ..adapters.base import BaseAdapter
from ..adapters.chaoxing import ChaoxingAdapter
from ..adapters.dingtalk import DingTalkAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    适配器注册表 (数据库版本)

    管理:
    - 适配器注册与发现
    - 适配器实例缓存
    - 平台配置管理 (持久化到数据库)
    """

    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._adapter_classes: Dict[str, Type[BaseAdapter]] = {
            "chaoxing": ChaoxingAdapter,
            "dingtalk": DingTalkAdapter
        }
        self._dao = dao_factory.platform_config()

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
            config = await self.get_config(platform) or {}
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

    async def set_config(self, platform: str, config: Dict) -> None:
        """设置平台配置 (持久化到数据库)"""
        # 检查是否已存在
        existing = await self._dao.get_by_platform(platform)
        
        if existing:
            # 更新
            await self._dao.update(existing["id"], {"config": config})
        else:
            # 创建
            from shared.utils import generate_uuid
            await self._dao.insert({
                "id": generate_uuid(),
                "platform": platform,
                "config": config,
                "is_active": True
            })
        
        logger.info(f"Set config for platform: {platform}")

    async def get_config(self, platform: str) -> Optional[Dict]:
        """获取平台配置 (从数据库读取)"""
        row = await self._dao.get_by_platform(platform)
        if row:
            config = row.get("config")
            if isinstance(config, str):
                config = json.loads(config)
            return config
        return None
    
    async def list_configs(self) -> List[Dict[str, Any]]:
        """列出所有平台配置"""
        rows = await self._dao.list_all(limit=100)
        result = []
        for row in rows:
            config = row.get("config")
            if isinstance(config, str):
                config = json.loads(config)
            result.append({
                "id": row["id"],
                "platform": row["platform"],
                "config": config,
                "is_active": bool(row.get("is_active", 1)),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at")
            })
        return result
    
    async def delete_config(self, platform: str) -> bool:
        """删除平台配置"""
        row = await self._dao.get_by_platform(platform)
        if row:
            await self._dao.delete(row["id"])
            # 同时移除缓存的适配器实例
            if platform in self._adapters:
                del self._adapters[platform]
            logger.info(f"Deleted config for platform: {platform}")
            return True
        return False


# FastAPI依赖注入
def get_adapter_registry() -> AdapterRegistry:
    """获取AdapterRegistry实例"""
    return AdapterRegistry()
