"""
智能答疑引擎
"""

from typing import Any, Dict, List, Optional
import logging
import os
from datetime import datetime

from shared.utils import generate_uuid
from shared.config import get_settings

# 引入 LangChain 相关的包，用于真实调用智谱 GLM-4
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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
        # 知识库（生产环境应使用向量数据库，如 ChromaDB）
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

        # 调用真实的AI模型
        answer = await self._call_ai(prompt)

        # 记录对话
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        self._sessions[session_id] = history

        return {
            "answer": answer,
            "sources": knowledge[:3],  # 返回前3个知识来源
            "confidence": 0.85,  # 目前为预设，后续可根据大模型返回的 token 概率计算
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
        (目前为基础文本匹配，后续可替换为向量检索)
        """
        knowledge = self._knowledge_base.get(course_id, [])
        results = []
        question_lower = question.lower()
        for k in knowledge:
            if any(w in k.get("content", "").lower() for w in question_lower.split()):
                results.append(k)

        if not results:
            results = [
                {
                    "knowledge_id": "kp-001",
                    "title": "系统默认知识提示",
                    "content": "当前课程知识库尚未录入相关详细文档，请结合通用知识进行解答。",
                    "relevance": 0.5
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
            "你是一位专业的课程助教，请基于以下知识库内容回答学生的问题。",
            "如果知识库中的内容不足以回答问题，你可以使用你的专业知识，但请保持态度和善、有引导性。",
            "\n【相关知识】："
        ]

        for k in knowledge[:3]:
            prompt_parts.append(f"- {k.get('title', '')}: {k.get('content', '')[:500]}")

        if history:
            prompt_parts.append("\n【历史对话】：")
            for h in history[-4:]:  # 携带最近4轮对话提供上下文
                role = "学生" if h["role"] == "user" else "助教"
                prompt_parts.append(f"{role}: {h['content']}")

        prompt_parts.append(f"\n【学生最新问题】：{question}")
        prompt_parts.append("\n请给出专业、准确、易懂的回答：")

        return "\n".join(prompt_parts)

    async def _call_ai(self, prompt: str) -> str:
        """
        调用真实的 GLM-4 模型
        """
        # 尝试从配置或环境变量中获取 API KEY
        api_key = getattr(settings, 'GLM_API_KEY', os.getenv('GLM_API_KEY'))
        if not api_key:
            return "系统配置提示：未检测到 GLM_API_KEY。请在环境变量或启动配置中填入你的智谱 API Key 才能唤醒真正的 AI 助教。"

        try:
            # 初始化智谱 GLM-4 模型，利用大模型标准的 OpenAI 兼容接口
            llm = ChatOpenAI(
                temperature=0.7,
                model_name="glm-4",
                openai_api_key=api_key,
                openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
            )
            
            messages = [
                SystemMessage(content="你是一个耐心、专业的大学课程 AI 助教。"),
                HumanMessage(content=prompt)
            ]
            
            # 发起异步调用
            response = await llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"调用大模型失败: {e}")
            return f"抱歉，系统在连接 AI 模型时遇到了一些问题。详细错误：{str(e)}"

    async def _generate_related_questions(
        self,
        question: str,
        course_id: str
    ) -> List[str]:
        """生成相关问题"""
        # 初期先使用固定推荐，后续可以再写一个 _call_ai 请求让大模型动态生成3个相关问题
        return [
            "这个问题在实际应用中如何体现？",
            "能否给我布置一道相关的小练习？",
            "学习这个概念有哪些常见的易错点？"
        ]

def get_qa_engine() -> QAEngine:
    return QAEngine()
