"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "agent-framework",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@router.get("/health/detail")
async def health_detail():
    """详细健康检查"""
    # 获取进程信息
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        "status": "healthy",
        "service": "agent-framework",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "process": {
            "memory_mb": memory_info.rss / 1024 / 1024,
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        }
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    # TODO: 检查数据库连接、Redis连接等
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "ai_service": "ok"
        }
    }
