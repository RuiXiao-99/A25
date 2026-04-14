"""
知识存储服务
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import csv
import io

from shared.models import KnowledgePoint, PaginatedResponse
from shared.utils import generate_uuid
from shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """
    知识存储服务

    提供:
    - 知识点的CRUD操作
    - 向量检索（模拟）
    - 知识图谱管理
    - 知识迁移
    """

    def __init__(self):
        # 内存存储（生产环境应使用数据库+向量数据库）
        self._knowledge: Dict[str, KnowledgePoint] = {}
        self._course_knowledge: Dict[str, List[str]] = {}  # course_id -> [knowledge_ids]
        self._knowledge_tree: Dict[str, List[str]] = {}  # parent_id -> [child_ids]

    async def create_knowledge(
        self,
        name: str,
        course_id: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> KnowledgePoint:
        """
        创建知识点
        """
        knowledge_id = generate_uuid()

        knowledge = KnowledgePoint(
            id=knowledge_id,
            name=name,
            description=description,
            parent_id=parent_id,
            course_id=course_id,
            tags=tags or []
        )

        # 存储
        self._knowledge[knowledge_id] = knowledge

        # 更新课程索引
        if course_id not in self._course_knowledge:
            self._course_knowledge[course_id] = []
        self._course_knowledge[course_id].append(knowledge_id)

        # 更新树结构
        if parent_id:
            if parent_id not in self._knowledge_tree:
                self._knowledge_tree[parent_id] = []
            self._knowledge_tree[parent_id].append(knowledge_id)

        # 如果有内容，生成向量嵌入（模拟）
        if content:
            await self._embed_knowledge(knowledge_id, content)

        logger.info(f"Created knowledge: {knowledge_id} - {name}")
        return knowledge

    async def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgePoint]:
        """获取知识点"""
        return self._knowledge.get(knowledge_id)

    async def list_knowledge(
        self,
        course_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginatedResponse[KnowledgePoint]:
        """
        列出知识点
        """
        items = list(self._knowledge.values())

        # 筛选
        if course_id:
            items = [k for k in items if k.course_id == course_id]
        if parent_id is not None:
            items = [k for k in items if k.parent_id == parent_id]
        if tags:
            items = [k for k in items if any(t in k.tags for t in tags)]

        # 分页
        total = len(items)
        start = (page - 1) * size
        end = start + size
        items = items[start:end]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )

    async def update_knowledge(
        self,
        knowledge_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> KnowledgePoint:
        """更新知识点"""
        knowledge = self._knowledge.get(knowledge_id)
        if not knowledge:
            raise ValidationException(f"Knowledge not found: {knowledge_id}")

        if name:
            knowledge.name = name
        if description is not None:
            knowledge.description = description
        if tags is not None:
            knowledge.tags = tags

        # 如果有新内容，更新向量嵌入
        if content:
            await self._embed_knowledge(knowledge_id, content)

        self._knowledge[knowledge_id] = knowledge
        return knowledge

    async def delete_knowledge(self, knowledge_id: str) -> None:
        """删除知识点"""
        knowledge = self._knowledge.get(knowledge_id)
        if not knowledge:
            return

        # 删除子知识点
        children = self._knowledge_tree.get(knowledge_id, [])
        for child_id in children:
            await self.delete_knowledge(child_id)

        # 从索引中移除
        if knowledge.course_id in self._course_knowledge:
            self._course_knowledge[knowledge.course_id].remove(knowledge_id)
        if knowledge.parent_id and knowledge.parent_id in self._knowledge_tree:
            if knowledge_id in self._knowledge_tree[knowledge.parent_id]:
                self._knowledge_tree[knowledge.parent_id].remove(knowledge_id)

        # 删除知识点
        del self._knowledge[knowledge_id]
        if knowledge_id in self._knowledge_tree:
            del self._knowledge_tree[knowledge_id]

        logger.info(f"Deleted knowledge: {knowledge_id}")

    async def search(
        self,
        query: str,
        course_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        语义搜索

        生产环境应使用向量数据库进行检索
        """
        results = []
        query_lower = query.lower()

        for kp in self._knowledge.values():
            # 简单的关键词匹配（模拟）
            if course_id and kp.course_id != course_id:
                continue

            score = 0
            if query_lower in kp.name.lower():
                score = 0.9
            elif kp.description and query_lower in kp.description.lower():
                score = 0.7
            elif query_lower in " ".join(kp.tags).lower():
                score = 0.5

            if score > 0:
                results.append({
                    "knowledge": kp.model_dump(),
                    "score": score
                })

        # 排序并返回top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def import_knowledge(
        self,
        course_id: str,
        content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """
        批量导入知识点
        """
        imported_count = 0
        errors = []

        try:
            if filename.endswith(".json"):
                data = json.loads(content.decode("utf-8"))
                for item in data:
                    try:
                        await self.create_knowledge(
                            name=item["name"],
                            course_id=course_id,
                            description=item.get("description"),
                            parent_id=item.get("parent_id"),
                            tags=item.get("tags", [])
                        )
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Failed to import: {item.get('name', 'unknown')} - {e}")

            elif filename.endswith(".csv"):
                reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
                for row in reader:
                    try:
                        await self.create_knowledge(
                            name=row["name"],
                            course_id=course_id,
                            description=row.get("description"),
                            tags=row.get("tags", "").split(",") if row.get("tags") else []
                        )
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Failed to import row: {e}")

            else:
                raise ValidationException(f"Unsupported file format: {filename}")

        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise

        return {
            "imported_count": imported_count,
            "error_count": len(errors),
            "errors": errors[:10]  # 只返回前10个错误
        }

    async def migrate_knowledge(
        self,
        source_course_id: str,
        target_course_id: str,
        knowledge_ids: List[str]
    ) -> Dict[str, Any]:
        """
        知识迁移
        """
        migrated = []

        for kid in knowledge_ids:
            knowledge = self._knowledge.get(kid)
            if not knowledge:
                continue

            # 创建新知识点（复制）
            new_knowledge = await self.create_knowledge(
                name=knowledge.name,
                course_id=target_course_id,
                description=knowledge.description,
                tags=knowledge.tags.copy()
            )
            migrated.append(new_knowledge.id)

        return {
            "source_course": source_course_id,
            "target_course": target_course_id,
            "migrated_count": len(migrated),
            "migrated_ids": migrated
        }

    async def get_children(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取子知识点"""
        child_ids = self._knowledge_tree.get(knowledge_id, [])
        return [self._knowledge[cid] for cid in child_ids if cid in self._knowledge]

    async def get_knowledge_path(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取知识点路径"""
        path = []
        current = self._knowledge.get(knowledge_id)

        while current:
            path.insert(0, current)
            if current.parent_id:
                current = self._knowledge.get(current.parent_id)
            else:
                break

        return path

    async def _embed_knowledge(self, knowledge_id: str, content: str) -> None:
        """
        生成知识向量嵌入

        生产环境应调用实际的向量嵌入服务
        """
        # 模拟嵌入过程
        logger.debug(f"Embedding knowledge: {knowledge_id}")
        # TODO: 调用嵌入模型生成向量


# FastAPI依赖注入
def get_knowledge_store() -> KnowledgeStore:
    """获取KnowledgeStore实例"""
    return KnowledgeStore()
