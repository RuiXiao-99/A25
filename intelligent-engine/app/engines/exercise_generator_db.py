"""
增量练习生成器 - 数据库版本

使用SQLite持久化存储练习和提交记录
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import random

from shared.models import PaginatedResponse
from shared.utils import generate_uuid
from shared.database import dao_factory, db_manager

logger = logging.getLogger(__name__)


class ExerciseGenerator:
    """
    增量练习生成器 (数据库版本)

    功能:
    - 根据薄弱知识点生成针对性练习
    - 练习推荐
    - 自动批改
    - 学习效果跟踪
    - 数据持久化
    """

    def __init__(self):
        # 练习存储（内存缓存）
        self._exercises: Dict[str, Dict] = {}
        # 学习记录DAO
        self._learning_dao = dao_factory.learning_record()

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
        # 获取学生薄弱知识点（从数据库）
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
        answer: str,
        course_id: Optional[str] = None,
        knowledge_point_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        提交答案
        """
        exercise = self._exercises.get(exercise_id)
        if not exercise:
            return {"success": False, "message": "Exercise not found"}

        # 自动批改
        is_correct, score, feedback = await self._auto_grade(exercise, answer)

        # 更新学习记录
        if knowledge_point_id and course_id:
            await self._update_learning_record(
                student_id=student_id,
                course_id=course_id,
                knowledge_point_id=knowledge_point_id,
                is_correct=is_correct
            )

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
        # 从学习记录获取
        rows = await self._learning_dao.list_by_student(student_id, course_id, limit=size)
        
        # 获取总数
        if course_id:
            count_sql = """
                SELECT COUNT(*) as count FROM learning_records 
                WHERE student_id = ? AND course_id = ?
            """
            async with db_manager.connection.execute(count_sql, (student_id, course_id)) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0
        else:
            count_sql = "SELECT COUNT(*) as count FROM learning_records WHERE student_id = ?"
            async with db_manager.connection.execute(count_sql, (student_id,)) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

        items = [
            {
                "knowledge_point_id": r["knowledge_point_id"],
                "mastery_level": r.get("mastery_level", 0),
                "practice_count": r.get("practice_count", 0),
                "correct_count": r.get("correct_count", 0),
                "last_practice_at": r.get("last_practice_at"),
                "updated_at": r.get("updated_at")
            }
            for r in rows
        ]

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
        # 从学习记录获取统计
        rows = await self._learning_dao.list_by_student(student_id, course_id, limit=1000)

        if not rows:
            return {
                "total_count": 0,
                "correct_count": 0,
                "correct_rate": 0,
                "avg_mastery": 0,
                "improvement_trend": "stable"
            }

        total_count = sum(r.get("practice_count", 0) for r in rows)
        correct_count = sum(r.get("correct_count", 0) for r in rows)
        mastery_levels = [r.get("mastery_level", 0) for r in rows]

        # 计算进步趋势
        if len(rows) >= 3:
            recent_mastery = sum(mastery_levels[-3:]) / 3
            earlier_mastery = sum(mastery_levels[:3]) / 3
            if recent_mastery > earlier_mastery + 0.1:
                trend = "improving"
            elif recent_mastery < earlier_mastery - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_count": total_count,
            "correct_count": correct_count,
            "correct_rate": round(correct_count / total_count * 100, 1) if total_count > 0 else 0,
            "avg_mastery": round(sum(mastery_levels) / len(mastery_levels), 2) if mastery_levels else 0,
            "improvement_trend": trend,
            "knowledge_point_count": len(rows),
            "knowledge_point_stats": [
                {
                    "knowledge_point_id": r["knowledge_point_id"],
                    "mastery_level": r.get("mastery_level", 0),
                    "practice_count": r.get("practice_count", 0),
                    "correct_count": r.get("correct_count", 0)
                }
                for r in rows
            ]
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
        获取学生薄弱知识点（从数据库）
        """
        # 从学习记录获取掌握程度较低的知识点
        rows = await self._learning_dao.list_by_student(student_id, course_id, limit=100)
        
        # 筛选掌握程度低于0.6的知识点
        weak_points = []
        for row in rows:
            if row.get("mastery_level", 1) < 0.6:
                weak_points.append(row["knowledge_point_id"])
        
        # 如果没有薄弱点，返回默认列表
        if not weak_points:
            return [
                "递归算法",
                "动态规划",
                "数据结构",
                "算法复杂度",
                "递推关系"
            ]
        
        return weak_points

    async def _update_learning_record(
        self,
        student_id: str,
        course_id: str,
        knowledge_point_id: str,
        is_correct: bool
    ) -> None:
        """
        更新学习记录
        """
        from shared.database import dao_factory
        
        # 检查是否已存在记录
        existing = await self._learning_dao.get_by_student_and_knowledge(
            student_id, knowledge_point_id
        )
        
        now = datetime.utcnow()
        
        if existing:
            # 更新现有记录
            practice_count = existing.get("practice_count", 0) + 1
            correct_count = existing.get("correct_count", 0) + (1 if is_correct else 0)
            mastery_level = correct_count / practice_count if practice_count > 0 else 0
            
            await self._learning_dao.update(existing["id"], {
                "practice_count": practice_count,
                "correct_count": correct_count,
                "mastery_level": mastery_level,
                "last_practice_at": now,
                "updated_at": now
            })
        else:
            # 创建新记录
            await self._learning_dao.insert({
                "id": generate_uuid(),
                "student_id": student_id,
                "course_id": course_id,
                "knowledge_point_id": knowledge_point_id,
                "mastery_level": 1.0 if is_correct else 0.0,
                "practice_count": 1,
                "correct_count": 1 if is_correct else 0,
                "last_practice_at": now,
                "created_at": now,
                "updated_at": now
            })


def get_exercise_generator() -> ExerciseGenerator:
    """获取ExerciseGenerator实例"""
    return ExerciseGenerator()
