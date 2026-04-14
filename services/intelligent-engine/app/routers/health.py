"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "intelligent-engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    return {
        "status": "ready",
        "checks": {
            "qa_engine": "ok",
            "grading_engine": "ok",
            "warning_engine": "ok",
            "exercise_generator": "ok"
        }
    }
