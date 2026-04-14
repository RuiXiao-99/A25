"""
作业批改路由
"""

from fastapi import APIRouter, Depends, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.models import BaseResponse
from ..engines import GradingEngine, get_grading_engine

router = APIRouter()


class SubmissionRequest(BaseModel):
    """提交请求"""
    assignment_id: str = Field(..., description="作业ID")
    student_id: str = Field(..., description="学生ID")
    content: str = Field(..., description="提交内容")
    file_urls: List[str] = Field(default_factory=list, description="附件URL")


class Annotation(BaseModel):
    """批注模型"""
    position: dict = Field(description="批注位置")
    type: str = Field(description="批注类型: error/warning/suggestion")
    content: str = Field(description="批注内容")
    suggestion: Optional[str] = Field(None, description="改进建议")


class GradingResult(BaseModel):
    """批改结果"""
    submission_id: str
    score: float
    annotations: List[Annotation]
    feedback: str
    knowledge_gaps: List[str] = Field(default_factory=list)
    graded_at: str


@router.post("/submit", response_model=BaseResponse[GradingResult])
async def submit_for_grading(
    request: SubmissionRequest,
    engine: GradingEngine = Depends(get_grading_engine)
):
    """
    提交作业进行批改

    支持文本、代码等多种类型的作业批改
    """
    result = await engine.grade(
        assignment_id=request.assignment_id,
        student_id=request.student_id,
        content=request.content,
        file_urls=request.file_urls
    )
    return BaseResponse(data=result)


@router.post("/upload")
async def upload_assignment(
    assignment_id: str,
    student_id: str,
    file: UploadFile = File(...),
    engine: GradingEngine = Depends(get_grading_engine)
):
    """
    上传文件进行批改

    支持PDF、Word、图片等格式
    """
    content = await file.read()
    result = await engine.grade_file(
        assignment_id=assignment_id,
        student_id=student_id,
        file_content=content,
        filename=file.filename
    )
    return BaseResponse(data=result)


@router.get("/result/{submission_id}")
async def get_grading_result(
    submission_id: str,
    engine: GradingEngine = Depends(get_grading_engine)
):
    """获取批改结果"""
    result = await engine.get_result(submission_id)
    return BaseResponse(data=result)


@router.get("/annotations/{submission_id}")
async def get_annotations(
    submission_id: str,
    engine: GradingEngine = Depends(get_grading_engine)
):
    """获取批注详情"""
    annotations = await engine.get_annotations(submission_id)
    return BaseResponse(data=annotations)


@router.post("/feedback/{submission_id}")
async def submit_feedback(
    submission_id: str,
    rating: int,
    comment: Optional[str] = None,
    engine: GradingEngine = Depends(get_grading_engine)
):
    """
    提交批改反馈

    用于改进批改模型
    """
    await engine.record_feedback(
        submission_id=submission_id,
        rating=rating,
        comment=comment
    )
    return BaseResponse(message="Feedback recorded successfully")
