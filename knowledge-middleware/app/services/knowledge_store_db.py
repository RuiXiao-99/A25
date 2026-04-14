"""
知识存储服务 - 数据库版本

使用SQLite持久化存储知识数据
"""

import json
import csv
import io
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from shared.models import KnowledgePoint, PaginatedResponse
from shared.utils import generate_uuid
from shared.exceptions import ValidationException
from shared.database import dao_factory, db_manager

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """
    知识存储服务 (数据库版本)

    提供:
    - 知识点的CRUD操作
    - 向量检索（模拟）
    - 知识图谱管理
    - 知识迁移
    """

    def __init__(self):
        self._dao = dao_factory.knowledge_point()

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
        now = datetime.utcnow()

        # 保存到数据库
        await self._dao.insert({
            "id": knowledge_id,
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "course_id": course_id,
            "tags": tags or [],
            "content": content,
            "created_at": now,
            "updated_at": now
        })

        # 如果有内容，生成向量嵌入（模拟）
        if content:
            await self._embed_knowledge(knowledge_id, content)

        logger.info(f"Created knowledge: {knowledge_id} - {name}")
        
        return KnowledgePoint(
            id=knowledge_id,
            name=name,
            description=description,
            parent_id=parent_id,
            course_id=course_id,
            tags=tags or []
        )

    async def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgePoint]:
        """获取知识点"""
        row = await self._dao.get_by_id(knowledge_id)
        if not row:
            return None
        return self._row_to_knowledge_point(row)

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
        # 构建查询条件
        conditions = []
        params = []
        
        if course_id:
            conditions.append("course_id = ?")
            params.append(course_id)
        if parent_id is not None:
            conditions.append("parent_id = ?" if parent_id else "parent_id IS NULL")
            if parent_id:
                params.append(parent_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as count FROM knowledge_points WHERE {where_clause}"
        async with db_manager.connection.execute(count_sql, params) as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0
        
        # 获取分页数据
        offset = (page - 1) * size
        sql = f"""
            SELECT * FROM knowledge_points 
            WHERE {where_clause} 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        
        rows = await db_manager.fetchall(sql, tuple(params))
        items = [self._row_to_knowledge_point(row) for row in rows]
        
        # 如果有标签筛选，在内存中过滤
        if tags:
            items = [k for k in items if any(t in k.tags for t in tags)]

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
        row = await self._dao.get_by_id(knowledge_id)
        if not row:
            raise ValidationException(f"Knowledge not found: {knowledge_id}")

        update_data = {}
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if tags is not None:
            update_data["tags"] = tags
        if content:
            update_data["content"] = content

        if update_data:
            await self._dao.update(knowledge_id, update_data)

        # 如果有新内容，更新向量嵌入
        if content:
            await self._embed_knowledge(knowledge_id, content)

        return await self.get_knowledge(knowledge_id)

    async def delete_knowledge(self, knowledge_id: str) -> None:
        """删除知识点"""
        # 递归删除子知识点
        children = await self.get_children(knowledge_id)
        for child in children:
            await self.delete_knowledge(child.id)

        # 从数据库删除
        await self._dao.delete(knowledge_id)
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
        
        # 构建查询
        if course_id:
            sql = "SELECT * FROM knowledge_points WHERE course_id = ?"
            rows = await db_manager.fetchall(sql, (course_id,))
        else:
            sql = "SELECT * FROM knowledge_points"
            rows = await db_manager.fetchall(sql)

        for row in rows:
            kp = self._row_to_knowledge_point(row)
            
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
            knowledge = await self.get_knowledge(kid)
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
        rows = await self._dao.list_by_parent(knowledge_id)
        return [self._row_to_knowledge_point(row) for row in rows]

    async def get_knowledge_path(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取知识点路径"""
        path = []
        current = await self.get_knowledge(knowledge_id)

        while current:
            path.insert(0, current)
            if current.parent_id:
                current = await self.get_knowledge(current.parent_id)
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

    def _row_to_knowledge_point(self, row: Dict[str, Any]) -> KnowledgePoint:
        """将数据库行转换为KnowledgePoint对象"""
        tags = row.get("tags")
        if isinstance(tags, str):
            tags = json.loads(tags)
        
        return KnowledgePoint(
            id=row["id"],
            name=row["name"],
            description=row.get("description"),
            parent_id=row.get("parent_id"),
            course_id=row["course_id"],
            tags=tags or []
        )


# FastAPI依赖注入
def get_knowledge_store() -> KnowledgeStore:
    """获取KnowledgeStore实例"""
    return KnowledgeStore()
