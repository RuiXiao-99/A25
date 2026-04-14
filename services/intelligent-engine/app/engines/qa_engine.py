"""
智能答疑引擎
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from shared.utils import generate_uuid
from shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class QAEngine:
    """
    智能答疑引擎

    功能:
    - 基于课程知识库的精准问答
    - 多轮对话支持
    - 知识点关联推荐
    """

    def __init__(self):
        # 会话存储（生产环境应使用Redis）
        self._sessions: Dict[str, List[Dict]] = {}
        # 知识库（生产环境应使用向量数据库）
        self._knowledge_base: Dict[str, List[Dict]] = {}

    async def ask(
        self,
        question: str,
        course_id: str,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        回答问题
        """
        # 创建或获取会话
        if not session_id:
            session_id = generate_uuid()

        # 获取对话历史
        history = self._sessions.get(session_id, [])

        # 检索相关知识
        knowledge = await self._retrieve_knowledge(question, course_id)

        # 构建提示词
        prompt = self._build_prompt(question, knowledge, history, context)

        # 调用AI模型（模拟）
        answer = await self._call_ai(prompt)

        # 记录对话
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        self._sessions[session_id] = history

        return {
            "answer": answer,
            "sources": knowledge[:3],  # 返回前3个知识来源
            "confidence": 0.85,  # 模拟置信度
            "related_questions": await self._generate_related_questions(question, course_id),
            "session_id": session_id
        }

    async def chat(
        self,
        message: str,
        session_id: str,
        course_id: str
    ) -> Dict[str, Any]:
        """
        多轮对话
        """
        return await self.ask(
            question=message,
            course_id=course_id,
            session_id=session_id
        )

    async def get_history(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        return self._sessions.get(session_id, [])

    async def clear_history(self, session_id: str) -> None:
        """清空对话历史"""
        if session_id in self._sessions:
            del self._sessions[session_id]

    async def _retrieve_knowledge(
        self,
        question: str,
        course_id: str
    ) -> List[Dict]:
        """
        检索相关知识

        生产环境应调用向量数据库
        """
        # 模拟知识检索
        knowledge = self._knowledge_base.get(course_id, [])

        # 简单的关键词匹配（模拟）
        results = []
        question_lower = question.lower()
        for k in knowledge:
            if any(w in k.get("content", "").lower() for w in question_lower.split()):
                results.append(k)

        # 如果没有匹配，返回模拟数据
        if not results:
            results = [
                {
                    "knowledge_id": "kp-001",
                    "title": "相关知识",
                    "content": "这是与问题相关的知识内容...",
                    "relevance": 0.8
                }
            ]

        return results

    def _build_prompt(
        self,
        question: str,
        knowledge: List[Dict],
        history: List[Dict],
        context: Optional[Dict]
    ) -> str:
        """构建提示词"""
        prompt_parts = [
            "你是一位专业的课程助教，请基于以下知识回答学生的问题。",
            "\n相关知识："
        ]

        for k in knowledge[:3]:
            prompt_parts.append(f"- {k.get('title', '')}: {k.get('content', '')[:200]}")

        if history:
            prompt_parts.append("\n对话历史：")
            for h in history[-4:]:  # 最近4轮对话
                role = "学生" if h["role"] == "user" else "助教"
                prompt_parts.append(f"{role}: {h['content']}")

        prompt_parts.append(f"\n学生问题：{question}")
        prompt_parts.append("\n请给出专业、准确的回答：")

        return "\n".join(prompt_parts)

    async def _call_ai(self, prompt: str) -> str:
        """
        调用AI模型

        生产环境应调用GLM-4 API
        """
        # 模拟AI响应
        return f"根据您的提问，我来为您详细解答。这是一个很好的问题，涉及到课程的核心知识点。..."

    async def _generate_related_questions(
        self,
        question: str,
        course_id: str
    ) -> List[str]:
        """生成相关问题"""
        # 模拟生成相关问题
        return [
            "这个问题在实际应用中如何体现？",
            "有哪些相关的知识点需要了解？",
            "能否举个具体的例子说明？"
        ]


def get_qa_engine() -> QAEngine:
    """获取QAEngine实例"""
    return QAEngine()
