"""
工具函数模块
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypeVar, Generic
import json
import hashlib


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """获取当前时间戳（UTC）"""
    return datetime.utcnow()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """格式化日期时间"""
    if dt is None:
        return ""
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(dt_str, fmt)


def generate_hash(content: str, algorithm: str = "sha256") -> str:
    """生成哈希值"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content.encode("utf-8"))
    return hash_obj.hexdigest()


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮蔽敏感数据"""
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)
    return (
        data[:visible_chars]
        + mask_char * (len(data) - visible_chars * 2)
        + data[-visible_chars:]
    )


def deep_merge(base: Dict, update: Dict) -> Dict:
    """深度合并字典"""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    """展平嵌套字典"""
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分块"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


class Singleton:
    """单例模式装饰器"""

    _instances = {}

    def __init__(self, cls):
        self._cls = cls

    def __call__(self, *args, **kwargs):
        if self._cls not in self._instances:
            self._instances[self._cls] = self._cls(*args, **kwargs)
        return self._instances[self._cls]


T = TypeVar("T")


class Result(Generic[T]):
    """结果封装类"""

    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        """创建成功结果"""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        """创建失败结果"""
        return cls(success=False, error=error)

    def is_ok(self) -> bool:
        """是否成功"""
        return self.success

    def is_fail(self) -> bool:
        """是否失败"""
        return not self.success

    def unwrap(self) -> T:
        """解包结果（失败时抛出异常）"""
        if not self.success:
            raise ValueError(f"Called unwrap on failed result: {self.error}")
        return self.data

    def unwrap_or(self, default: T) -> T:
        """解包结果或返回默认值"""
        if self.success:
            return self.data
        return default
