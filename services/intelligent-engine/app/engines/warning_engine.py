"""
学情预警引擎
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta
import random

from shared.models import PaginatedResponse
from shared.utils import generate_uuid

logger = logging.getLogger(__name__)


class WarningEngine:
    """
    学情预警引擎

    功能:
    - 学生风险预测
    - 学情分析与预警
    - 课程整体分析
    - 学情报告生成
    """

    def __init__(self):
        # 预警存储（生产环境应使用数据库）
        self._warnings: Dict[str, Dict] = {}
        # 学生画像
        self._student_profiles: Dict[str, Dict] = {}
        # 预警确认记录
        self._acknowledgments: Dict[str, List[Dict]] = {}

    async def list_warnings(
        self,
        course_id: Optional[str] = None,
        student_id: Optional[str] = None,
        level: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginatedResponse:
        """
        获取预警列表
        """
        warnings = list(self._warnings.values())

        # 筛选
        if course_id:
            warnings = [w for w in warnings if w.get("course_id") == course_id]
        if student_id:
            warnings = [w for w in warnings if w.get("student_id") == student_id]
        if level:
            warnings = [w for w in warnings if w.get("level") == level]

        # 排序
        warnings.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # 分页
        total = len(warnings)
        start = (page - 1) * size
        end = start + size
        items = warnings[start:end]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    async def predict_risk(
        self,
        student_id: str,
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        学生风险预测
        """
        # 获取学生画像
        profile = await self._get_or_create_profile(student_id, course_id)

        # 计算风险因子
        factors = await self._calculate_risk_factors(student_id, course_id)

        # 计算总体风险
        risk_score = sum(f["weight"] * f["value"] for f in factors) / sum(f["weight"] for f in factors)

        # 确定风险等级
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # 生成建议
        recommendations = await self._generate_recommendations(factors, risk_level)

        # 如果风险较高，创建预警
        if risk_level in ["high", "medium"]:
            await self._create_warning(
                student_id=student_id,
                course_id=course_id or "unknown",
                level=risk_level,
                warning_type="risk_prediction",
                description=f"学生存在{risk_level}风险，风险评分: {risk_score:.2f}"
            )

        return {
            "student_id": student_id,
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "factors": factors,
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    async def analyze_course(self, course_id: str) -> Dict[str, Any]:
        """
        课程学情分析
        """
        # 获取课程相关预警
        course_warnings = [
            w for w in self._warnings.values()
            if w.get("course_id") == course_id
        ]

        # 统计分析
        total_students = 50  # 模拟数据
        at_risk_students = len(set(w["student_id"] for w in course_warnings if w["level"] == "high"))

        # 按知识点统计薄弱点
        knowledge_gaps = {}
        for w in course_warnings:
            for kp in w.get("knowledge_points", []):
                knowledge_gaps[kp] = knowledge_gaps.get(kp, 0) + 1

        # 排序获取最薄弱的知识点
        top_gaps = sorted(knowledge_gaps.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "course_id": course_id,
            "total_students": total_students,
            "at_risk_students": at_risk_students,
            "risk_rate": round(at_risk_students / total_students * 100, 1) if total_students > 0 else 0,
            "warning_distribution": {
                "high": len([w for w in course_warnings if w["level"] == "high"]),
                "medium": len([w for w in course_warnings if w["level"] == "medium"]),
                "low": len([w for w in course_warnings if w["level"] == "low"])
            },
            "top_knowledge_gaps": [{"knowledge_point": k, "count": v} for k, v in top_gaps],
            "analyzed_at": datetime.utcnow().isoformat()
        }

    async def get_student_profile(
        self,
        student_id: str,
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取学生学情画像
        """
        return await self._get_or_create_profile(student_id, course_id)

    async def acknowledge_warning(
        self,
        warning_id: str,
        action: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        确认预警
        """
        warning = self._warnings.get(warning_id)
        if not warning:
            return {"success": False, "message": "Warning not found"}

        # 记录确认
        acknowledgment = {
            "warning_id": warning_id,
            "action": action,
            "note": note,
            "acknowledged_at": datetime.utcnow().isoformat()
        }

        if warning_id not in self._acknowledgments:
            self._acknowledgments[warning_id] = []
        self._acknowledgments[warning_id].append(acknowledgment)

        # 更新预警状态
        warning["status"] = "acknowledged"
        warning["acknowledged_at"] = acknowledgment["acknowledged_at"]

        return {"success": True, "warning": warning}

    async def generate_report(
        self,
        course_id: str,
        report_type: str = "weekly"
    ) -> Dict[str, Any]:
        """
        生成学情报告
        """
        # 获取课程分析
        analysis = await self.analyze_course(course_id)

        # 根据报告类型确定时间范围
        if report_type == "daily":
            start_date = datetime.utcnow() - timedelta(days=1)
        elif report_type == "weekly":
            start_date = datetime.utcnow() - timedelta(weeks=1)
        elif report_type == "monthly":
            start_date = datetime.utcnow() - timedelta(days=30)
        else:
            start_date = datetime.utcnow() - timedelta(weeks=1)

        # 生成报告
        report = {
            "report_id": generate_uuid(),
            "course_id": course_id,
            "report_type": report_type,
            "period": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "summary": {
                "total_warnings": analysis["warning_distribution"]["high"] + analysis["warning_distribution"]["medium"],
                "at_risk_students": analysis["at_risk_students"],
                "risk_rate": analysis["risk_rate"]
            },
            "details": analysis,
            "recommendations": [
                "建议重点关注高风险学生，进行一对一辅导",
                "针对薄弱知识点开展专题讲解",
                "增加课堂互动，提升学生参与度"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

        return report

    async def _get_or_create_profile(
        self,
        student_id: str,
        course_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        获取或创建学生画像
        """
        key = f"{student_id}_{course_id or 'all'}"

        if key not in self._student_profiles:
            # 创建默认画像
            self._student_profiles[key] = {
                "student_id": student_id,
                "course_id": course_id,
                "overall_mastery": random.uniform(0.5, 0.9),
                "knowledge_points": [
                    {"name": "基础概念", "mastery": random.uniform(0.6, 0.95)},
                    {"name": "核心原理", "mastery": random.uniform(0.5, 0.85)},
                    {"name": "实践应用", "mastery": random.uniform(0.4, 0.8)}
                ],
                "learning_style": "visual",
                "engagement_score": random.uniform(0.5, 0.9),
                "last_active": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }

        return self._student_profiles[key]

    async def _calculate_risk_factors(
        self,
        student_id: str,
        course_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        计算风险因子
        """
        # 模拟风险因子计算
        factors = [
            {
                "factor": "作业完成率",
                "weight": 0.3,
                "value": random.uniform(0.4, 0.9),
                "description": "近期作业完成情况"
            },
            {
                "factor": "知识点掌握度",
                "weight": 0.4,
                "value": random.uniform(0.3, 0.85),
                "description": "核心知识点掌握情况"
            },
            {
                "factor": "学习活跃度",
                "weight": 0.2,
                "value": random.uniform(0.5, 0.95),
                "description": "平台登录与学习时长"
            },
            {
                "factor": "练习正确率",
                "weight": 0.1,
                "value": random.uniform(0.4, 0.9),
                "description": "练习题目正确率"
            }
        ]

        return factors

    async def _generate_recommendations(
        self,
        factors: List[Dict],
        risk_level: str
    ) -> List[str]:
        """
        生成建议
        """
        recommendations = []

        for factor in factors:
            if factor["value"] < 0.6:
                if "作业" in factor["factor"]:
                    recommendations.append("建议按时完成作业，培养良好学习习惯")
                elif "知识点" in factor["factor"]:
                    recommendations.append("建议加强基础知识复习，夯实学习基础")
                elif "活跃度" in factor["factor"]:
                    recommendations.append("建议增加学习时间，保持学习连续性")
                elif "正确率" in factor["factor"]:
                    recommendations.append("建议多做练习，提高解题能力")

        if risk_level == "high":
            recommendations.insert(0, "建议尽快与教师沟通，制定个性化学习计划")

        return recommendations

    async def _create_warning(
        self,
        student_id: str,
        course_id: str,
        level: str,
        warning_type: str,
        description: str,
        knowledge_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建预警
        """
        warning_id = generate_uuid()

        warning = {
            "id": warning_id,
            "student_id": student_id,
            "course_id": course_id,
            "level": level,
            "type": warning_type,
            "description": description,
            "knowledge_points": knowledge_points or [],
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

        self._warnings[warning_id] = warning
        logger.info(f"Created warning: {warning_id} for student {student_id}")

        return warning


def get_warning_engine() -> WarningEngine:
    """获取WarningEngine实例"""
    return WarningEngine()
