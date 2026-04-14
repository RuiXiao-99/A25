"""
适配器模块
"""

from .base import BaseAdapter
from .chaoxing import ChaoxingAdapter
from .dingtalk import DingTalkAdapter

__all__ = ["BaseAdapter", "ChaoxingAdapter", "DingTalkAdapter"]
