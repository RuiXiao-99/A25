"""
增量练习生成器
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import random

from shared.models import PaginatedResponse
from shared.utils import generate_uuid

logger = logging.getLogger(__name__)


class ExerciseGenerator:
    """
    增量练习生成器

    功能:
    - 根据薄弱知识点生成针对性练习
    - 练习推荐
    - 自动批改
    - 学习效果跟踪
    """

    def __init__(self):
        # 练习存储
        self._exercises: Dict[str, Dict] = {}
        # 提交记录
        self._submissions: Dict[str, List[Dict]] = {}
        # 学生练习历史
        self._student_history: Dict[str, List[Dict]] = {}

    async def generate(
        self,
        student_id: str,
        knowledge_points: List[str],
        difficulty: str = "medium",
        count: int = 5,
        exercise_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        生成练习
        """
        exercises = []

        types = exercise_types or ["choice", "coding", "essay"]

        for i in range(count):
            exercise_type = random.choice(types)
            exercise = await self._create_exercise(
                knowledge_point=random.choice(knowledge_points),
                exercise_type=exercise_type,
                difficulty=difficulty
            )
            exercises.append(exercise)
            self._exercises[exercise["id"]] = exercise

        logger.info(f"Generated {len(exercises)} exercises for student {student_id}")
        return exercises

    async def recommend(
        self,
        student_id: str,
        course_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        推荐练习

        基于学情分析自动推荐
        """
        # 获取学生薄弱知识点（模拟）
        weak_points = await self._get_weak_knowledge_points(student_id, course_id)

        exercises = []
        for kp in weak_points[:limit]:
            exercise = await self._create_exercise(
                knowledge_point=kp,
                exercise_type=random.choice(["choice", "coding"]),
                difficulty="medium"
            )
            exercises.append(exercise)
            self._exercises[exercise["id"]] = exercise

        return exercises

    async def submit_answer(
        self,
        exercise_id: str,
        student_id: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        提交答案
        """
        exercise = self._exercises.get(exercise_id)
        if not exercise:
            return {"success": False, "message": "Exercise not found"}

        # 自动批改
        is_correct, score, feedback = await self._auto_grade(exercise, answer)

        # 记录提交
        submission = {
            "submission_id": generate_uuid(),
            "exercise_id": exercise_id,
            "student_id": student_id,
            "answer": answer,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "submitted_at": datetime.utcnow().isoformat()
        }

        if student_id not in self._student_history:
            self._student_history[student_id] = []
        self._student_history[student_id].append(submission)

        logger.info(f"Student {student_id} submitted exercise {exercise_id}, score: {score}")

        return {
            "success": True,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "correct_answer": exercise.get("answer") if not is_correct else None
        }

    async def get_history(
        self,
        student_id: str,
        course_id: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginatedResponse:
        """
        获取练习历史
        """
        history = self._student_history.get(student_id, [])

        # 排序
        history.sort(key=lambda x: x["submitted_at"], reverse=True)

        # 分页
        total = len(history)
        start = (page - 1) * size
        end = start + size
        items = history[start:end]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    async def get_stats(
        self,
        student_id: str,
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取练习统计
        """
        history = self._student_history.get(student_id, [])

        if not history:
            return {
                "total_count": 0,
                "correct_count": 0,
                "correct_rate": 0,
                "avg_score": 0,
                "improvement_trend": "stable"
            }

        total_count = len(history)
        correct_count = sum(1 for h in history if h["is_correct"])
        scores = [h["score"] for h in history]

        # 计算进步趋势
        if len(scores) >= 5:
            recent_avg = sum(scores[-5:]) / 5
            earlier_avg = sum(scores[:5]) / 5
            if recent_avg > earlier_avg + 10:
                trend = "improving"
            elif recent_avg < earlier_avg - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_count": total_count,
            "correct_count": correct_count,
            "correct_rate": round(correct_count / total_count * 100, 1) if total_count > 0 else 0,
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "improvement_trend": trend,
            "recent_scores": scores[-5:],
            "knowledge_point_stats": await self._get_knowledge_point_stats(history)
        }

    async def record_feedback(
        self,
        exercise_id: str,
        student_id: str,
        helpful: bool,
        comment: Optional[str]
    ) -> None:
        """
        记录练习反馈
        """
        exercise = self._exercises.get(exercise_id)
        if exercise:
            if "feedbacks" not in exercise:
                exercise["feedbacks"] = []
            exercise["feedbacks"].append({
                "student_id": student_id,
                "helpful": helpful,
                "comment": comment,
                "recorded_at": datetime.utcnow().isoformat()
            })
            logger.info(f"Recorded feedback for exercise {exercise_id}")

    async def _create_exercise(
        self,
        knowledge_point: str,
        exercise_type: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        创建练习题目
        """
        exercise_id = generate_uuid()

        # 模拟题目生成
        if exercise_type == "choice":
            return {
                "id": exercise_id,
                "type": "choice",
                "title": f"关于{knowledge_point}的选择题",
                "content": f"以下关于{knowledge_point}的描述，哪一项是正确的？",
                "knowledge_points": [knowledge_point],
                "difficulty": difficulty,
                "options": [
                    "A. 这是第一个选项",
                    "B. 这是第二个选项（正确答案）",
                    "C. 这是第三个选项",
                    "D. 这是第四个选项"
                ],
                "answer": "B",
                "hints": [f"提示：复习{knowledge_point}的基本概念"],
                "created_at": datetime.utcnow().isoformat()
            }
        elif exercise_type == "coding":
            return {
                "id": exercise_id,
                "type": "coding",
                "title": f"{knowledge_point}编程练习",
                "content": f"请编写代码实现{knowledge_point}的功能。",
                "knowledge_points": [knowledge_point],
                "difficulty": difficulty,
                "hints": ["考虑边界条件", "注意代码效率"],
                "answer": "# 参考答案\ndef solution():\n    pass",
                "created_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "id": exercise_id,
                "type": "essay",
                "title": f"{knowledge_point}简答题",
                "content": f"请简述{knowledge_point}的原理和应用。",
                "knowledge_points": [knowledge_point],
                "difficulty": difficulty,
                "hints": ["从定义出发", "举例说明"],
                "answer": "参考答案：...",
                "created_at": datetime.utcnow().isoformat()
            }

    async def _auto_grade(
        self,
        exercise: Dict,
        answer: str
    ) -> tuple:
        """
        自动批改
        """
        exercise_type = exercise["type"]

        if exercise_type == "choice":
            is_correct = answer.strip().upper() == exercise.get("answer", "").upper()
            score = 100 if is_correct else 0
            feedback = "回答正确！" if is_correct else f"正确答案是：{exercise.get('answer')}"
            return is_correct, score, feedback

        elif exercise_type == "coding":
            # 简单的代码评分（模拟）
            score = random.randint(60, 95)
            is_correct = score >= 80
            feedback = "代码实现基本正确" if is_correct else "代码存在一些问题，请检查"
            return is_correct, score, feedback

        else:
            # 主观题评分
            score = random.randint(50, 90)
            is_correct = score >= 60
            feedback = "回答较为完整" if score >= 70 else "建议补充更多细节"
            return is_correct, score, feedback

    async def _get_weak_knowledge_points(
        self,
        student_id: str,
        course_id: Optional[str]
    ) -> List[str]:
        """
        获取学生薄弱知识点
        """
        # 模拟返回薄弱知识点
        return [
            "递归算法",
            "动态规划",
            "数据结构",
            "算法复杂度",
            "递推关系"
        ]

    async def _get_knowledge_point_stats(
        self,
        history: List[Dict]
    ) -> List[Dict]:
        """
        获取知识点统计
        """
        kp_stats = {}

        for h in history:
            # 获取练习的知识点（模拟）
            kp = "综合知识"  # 实际应从exercise获取
            if kp not in kp_stats:
                kp_stats[kp] = {"count": 0, "correct": 0, "total_score": 0}
            kp_stats[kp]["count"] += 1
            if h["is_correct"]:
                kp_stats[kp]["correct"] += 1
            kp_stats[kp]["total_score"] += h["score"]

        return [
            {
                "knowledge_point": kp,
                "count": stats["count"],
                "correct_rate": round(stats["correct"] / stats["count"] * 100, 1),
                "avg_score": round(stats["total_score"] / stats["count"], 1)
            }
            for kp, stats in kp_stats.items()
        ]


def get_exercise_generator() -> ExerciseGenerator:
    """获取ExerciseGenerator实例"""
    return ExerciseGenerator()
