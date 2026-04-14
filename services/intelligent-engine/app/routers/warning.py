"""
学情预警路由
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from shared.models import BaseResponse, PaginatedResponse
from ..engines import WarningEngine, get_warning_engine

router = APIRouter()


@router.get("/list", response_model=BaseResponse[PaginatedResponse])
async def list_warnings(
    course_id: Optional[str] = Query(None, description="课程ID筛选"),
    student_id: Optional[str] = Query(None, description="学生ID筛选"),
    level: Optional[str] = Query(None, description="预警级别: low/medium/high"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    获取预警列表

    支持按课程、学生、级别筛选
    """
    result = await engine.list_warnings(
        course_id=course_id,
        student_id=student_id,
        level=level,
        page=page,
        size=size
    )
    return BaseResponse(data=result)


@router.get("/predict/{student_id}")
async def predict_risk(
    student_id: str,
    course_id: Optional[str] = None,
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    学生风险预测

    分析学生的学习风险等级和影响因素
    """
    result = await engine.predict_risk(
        student_id=student_id,
        course_id=course_id
    )
    return BaseResponse(data=result)


@router.get("/course/{course_id}/analysis")
async def analyze_course(
    course_id: str,
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    课程学情分析

    获取课程整体学情分析报告
    """
    result = await engine.analyze_course(course_id)
    return BaseResponse(data=result)


@router.get("/student/{student_id}/profile")
async def get_student_profile(
    student_id: str,
    course_id: Optional[str] = None,
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    获取学生学情画像

    包含知识点掌握情况、学习进度等
    """
    profile = await engine.get_student_profile(
        student_id=student_id,
        course_id=course_id
    )
    return BaseResponse(data=profile)


@router.post("/acknowledge/{warning_id}")
async def acknowledge_warning(
    warning_id: str,
    action: str,
    note: Optional[str] = None,
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    确认预警并记录处理措施
    """
    result = await engine.acknowledge_warning(
        warning_id=warning_id,
        action=action,
        note=note
    )
    return BaseResponse(data=result)


@router.get("/report/{course_id}")
async def generate_report(
    course_id: str,
    report_type: str = "weekly",
    engine: WarningEngine = Depends(get_warning_engine)
):
    """
    生成学情报告

    支持日报、周报、月报
    """
    report = await engine.generate_report(
        course_id=course_id,
        report_type=report_type
    )
    return BaseResponse(data=report)
