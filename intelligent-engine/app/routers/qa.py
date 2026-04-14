"""
智能答疑路由
"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.models import BaseResponse
from ..engines import QAEngine, get_qa_engine

router = APIRouter()


class QuestionRequest(BaseModel):
    """提问请求"""
    question: str = Field(..., description="问题内容")
    course_id: str = Field(..., description="课程ID")
    agent_id: Optional[str] = Field(None, description="智能体ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: dict = Field(default_factory=dict, description="上下文信息")


class Answer(BaseModel):
    """回答模型"""
    answer: str
    sources: List[dict] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    related_questions: List[str] = Field(default_factory=list)


@router.post("/ask", response_model=BaseResponse[Answer])
async def ask_question(
    request: QuestionRequest,
    engine: QAEngine = Depends(get_qa_engine)
):
    """
    智能问答

    支持多轮对话，基于课程知识库进行精准回答
    """
    result = await engine.ask(
        question=request.question,
        course_id=request.course_id,
        agent_id=request.agent_id,
        session_id=request.session_id,
        context=request.context
    )
    return BaseResponse(data=result)


@router.post("/chat")
async def chat(
    message: str,
    session_id: str,
    course_id: str,
    engine: QAEngine = Depends(get_qa_engine)
):
    """
    多轮对话

    基于会话上下文的连续对话
    """
    result = await engine.chat(
        message=message,
        session_id=session_id,
        course_id=course_id
    )
    return BaseResponse(data=result)


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    engine: QAEngine = Depends(get_qa_engine)
):
    """获取对话历史"""
    history = await engine.get_history(session_id)
    return BaseResponse(data=history)


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    engine: QAEngine = Depends(get_qa_engine)
):
    """清空对话历史"""
    await engine.clear_history(session_id)
    return BaseResponse(message=f"History cleared for session {session_id}")
