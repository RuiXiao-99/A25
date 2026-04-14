"""
增量练习路由
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.models import BaseResponse
from ..engines import ExerciseGenerator, get_exercise_generator

router = APIRouter()


class Exercise(BaseModel):
    """练习模型"""
    id: str
    type: str = Field(description="类型: choice/coding/essay")
    title: str
    content: str
    knowledge_points: List[str]
    difficulty: str = Field(description="难度: easy/medium/hard")
    hints: List[str] = Field(default_factory=list)
    options: Optional[List[str]] = None  # 选择题选项
    answer: Optional[str] = None  # 参考答案


class GenerateRequest(BaseModel):
    """生成练习请求"""
    student_id: str
    knowledge_points: List[str]
    difficulty: str = "medium"
    count: int = 5
    exercise_types: Optional[List[str]] = None


@router.post("/generate")
async def generate_exercises(
    request: GenerateRequest,
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    生成增量练习

    根据学生薄弱知识点生成针对性练习
    """
    exercises = await generator.generate(
        student_id=request.student_id,
        knowledge_points=request.knowledge_points,
        difficulty=request.difficulty,
        count=request.count,
        exercise_types=request.exercise_types
    )
    return BaseResponse(data=exercises)


@router.post("/submit")
async def submit_exercise(
    exercise_id: str,
    student_id: str,
    answer: str,
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    提交练习答案

    自动批改并更新学生学情
    """
    result = await generator.submit_answer(
        exercise_id=exercise_id,
        student_id=student_id,
        answer=answer
    )
    return BaseResponse(data=result)


@router.get("/recommend/{student_id}")
async def recommend_exercises(
    student_id: str,
    course_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    推荐练习

    基于学情分析自动推荐练习
    """
    exercises = await generator.recommend(
        student_id=student_id,
        course_id=course_id,
        limit=limit
    )
    return BaseResponse(data=exercises)


@router.get("/history/{student_id}")
async def get_exercise_history(
    student_id: str,
    course_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    获取练习历史
    """
    history = await generator.get_history(
        student_id=student_id,
        course_id=course_id,
        page=page,
        size=size
    )
    return BaseResponse(data=history)


@router.get("/stats/{student_id}")
async def get_exercise_stats(
    student_id: str,
    course_id: Optional[str] = None,
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    获取练习统计

    正确率、完成数、进步趋势等
    """
    stats = await generator.get_stats(
        student_id=student_id,
        course_id=course_id
    )
    return BaseResponse(data=stats)


@router.post("/feedback/{exercise_id}")
async def submit_exercise_feedback(
    exercise_id: str,
    student_id: str,
    helpful: bool,
    comment: Optional[str] = None,
    generator: ExerciseGenerator = Depends(get_exercise_generator)
):
    """
    提交练习反馈

    用于改进练习生成质量
    """
    await generator.record_feedback(
        exercise_id=exercise_id,
        student_id=student_id,
        helpful=helpful,
        comment=comment
    )
    return BaseResponse(message="Feedback recorded")
