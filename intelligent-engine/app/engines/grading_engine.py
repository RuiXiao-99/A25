"""
作业批改引擎
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import re

from shared.utils import generate_uuid
from shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class GradingEngine:
    """
    作业批改引擎

    功能:
    - 多模态作业批改（文本、代码、图片）
    - 精细化批注生成
    - 知识点错误分析
    - 改进建议生成
    """

    def __init__(self):
        # 批改结果存储（生产环境应使用数据库）
        self._results: Dict[str, Dict] = {}
        # 作业模板
        self._assignment_templates: Dict[str, Dict] = {}

    async def grade(
        self,
        assignment_id: str,
        student_id: str,
        content: str,
        file_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        批改作业
        """
        submission_id = generate_uuid()

        # 获取作业模板
        template = self._assignment_templates.get(assignment_id, {})

        # 分析提交内容
        analysis = await self._analyze_content(content, template)

        # 生成批注
        annotations = await self._generate_annotations(content, analysis)

        # 计算分数
        score = await self._calculate_score(analysis, template)

        # 生成反馈
        feedback = await self._generate_feedback(annotations, analysis)

        # 识别知识薄弱点
        knowledge_gaps = await self._identify_knowledge_gaps(analysis)

        result = {
            "submission_id": submission_id,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "score": score,
            "annotations": annotations,
            "feedback": feedback,
            "knowledge_gaps": knowledge_gaps,
            "graded_at": datetime.utcnow().isoformat()
        }

        # 存储结果
        self._results[submission_id] = result

        logger.info(f"Graded submission: {submission_id}, score: {score}")
        return result

    async def grade_file(
        self,
        assignment_id: str,
        student_id: str,
        file_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """
        批改文件作业

        支持PDF、Word、图片等格式
        """
        # 解析文件内容（模拟）
        content = await self._parse_file(file_content, filename)

        return await self.grade(
            assignment_id=assignment_id,
            student_id=student_id,
            content=content
        )

    async def get_result(self, submission_id: str) -> Optional[Dict]:
        """获取批改结果"""
        return self._results.get(submission_id)

    async def get_annotations(self, submission_id: str) -> List[Dict]:
        """获取批注详情"""
        result = self._results.get(submission_id)
        return result.get("annotations", []) if result else []

    async def record_feedback(
        self,
        submission_id: str,
        rating: int,
        comment: Optional[str]
    ) -> None:
        """记录批改反馈"""
        result = self._results.get(submission_id)
        if result:
            result["feedback_rating"] = rating
            result["feedback_comment"] = comment
            logger.info(f"Recorded feedback for submission: {submission_id}")

    async def _analyze_content(
        self,
        content: str,
        template: Dict
    ) -> Dict[str, Any]:
        """
        分析提交内容

        返回内容分析结果
        """
        analysis = {
            "word_count": len(content.split()),
            "has_code": "```" in content or "def " in content,
            "sections": [],
            "errors": [],
            "strengths": []
        }

        # 简单的内容分析（模拟）
        if analysis["word_count"] < 100:
            analysis["errors"].append("内容过短，可能不够完整")

        if analysis["has_code"]:
            # 代码分析
            code_analysis = await self._analyze_code(content)
            analysis["code_analysis"] = code_analysis

        return analysis

    async def _analyze_code(self, content: str) -> Dict:
        """分析代码内容"""
        return {
            "has_errors": False,
            "issues": [
                {"line": 5, "issue": "缺少边界条件检查", "severity": "warning"},
                {"line": 10, "issue": "变量命名不规范", "severity": "info"}
            ],
            "suggestions": [
                "建议添加输入验证",
                "考虑添加异常处理"
            ]
        }

    async def _generate_annotations(
        self,
        content: str,
        analysis: Dict
    ) -> List[Dict]:
        """
        生成批注

        模拟教师批注体验
        """
        annotations = []

        # 根据分析结果生成批注
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # 检查是否有明显错误（模拟）
            if "TODO" in line:
                annotations.append({
                    "position": {"line": i, "column": 1, "length": len(line)},
                    "type": "warning",
                    "content": "此处有未完成的任务",
                    "suggestion": "请补充完整实现"
                })

        # 添加整体评价批注
        if analysis.get("code_analysis"):
            for issue in analysis["code_analysis"].get("issues", []):
                annotations.append({
                    "position": {"line": issue["line"], "column": 1, "length": 20},
                    "type": issue["severity"],
                    "content": issue["issue"],
                    "suggestion": None
                })

        return annotations

    async def _calculate_score(
        self,
        analysis: Dict,
        template: Dict
    ) -> float:
        """
        计算分数
        """
        base_score = 100.0

        # 根据分析结果扣分
        errors = analysis.get("errors", [])
        for error in errors:
            if "过短" in error:
                base_score -= 10
            elif "错误" in error:
                base_score -= 5

        # 代码分析扣分
        code_analysis = analysis.get("code_analysis", {})
        if code_analysis:
            for issue in code_analysis.get("issues", []):
                if issue["severity"] == "error":
                    base_score -= 10
                elif issue["severity"] == "warning":
                    base_score -= 5

        return max(0, min(100, base_score))

    async def _generate_feedback(
        self,
        annotations: List[Dict],
        analysis: Dict
    ) -> str:
        """
        生成反馈意见
        """
        feedback_parts = []

        # 整体评价
        if analysis.get("word_count", 0) >= 100:
            feedback_parts.append("作业内容完整，结构清晰。")
        else:
            feedback_parts.append("建议增加内容深度，详细阐述关键观点。")

        # 代码相关反馈
        if analysis.get("has_code"):
            code_analysis = analysis.get("code_analysis", {})
            if code_analysis.get("has_errors"):
                feedback_parts.append("代码部分存在一些问题，请参考批注进行修改。")
            else:
                feedback_parts.append("代码实现基本正确，思路清晰。")

        # 批注总结
        if annotations:
            feedback_parts.append(f"共有{len(annotations)}处需要注意，请查看详细批注。")

        return " ".join(feedback_parts)

    async def _identify_knowledge_gaps(
        self,
        analysis: Dict
    ) -> List[str]:
        """
        识别知识薄弱点
        """
        gaps = []

        # 根据分析结果识别薄弱点
        for error in analysis.get("errors", []):
            if "边界条件" in error:
                gaps.append("边界条件处理")
            elif "异常处理" in error:
                gaps.append("异常处理机制")

        code_analysis = analysis.get("code_analysis", {})
        for issue in code_analysis.get("issues", []):
            if "命名" in issue.get("issue", ""):
                gaps.append("编码规范")
            if "边界" in issue.get("issue", ""):
                gaps.append("边界条件处理")

        return list(set(gaps))  # 去重

    async def _parse_file(
        self,
        content: bytes,
        filename: str
    ) -> str:
        """
        解析文件内容

        生产环境应使用相应的文件解析库
        """
        if filename.endswith(".txt"):
            return content.decode("utf-8")
        elif filename.endswith(".pdf"):
            # TODO: 使用pdf解析库
            return "[PDF内容解析结果]"
        elif filename.endswith((".doc", ".docx")):
            # TODO: 使用docx解析库
            return "[Word内容解析结果]"
        else:
            return f"[文件内容: {filename}]"


def get_grading_engine() -> GradingEngine:
    """获取GradingEngine实例"""
    return GradingEngine()
