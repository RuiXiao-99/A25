"""
知识管理路由
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import List, Optional

from shared.models import BaseResponse, PaginatedResponse, KnowledgePoint
from shared.exceptions import ValidationException
from ..services.knowledge_store import KnowledgeStore, get_knowledge_store

router = APIRouter()


@router.post("", response_model=BaseResponse[KnowledgePoint])
async def create_knowledge(
    name: str,
    description: Optional[str] = None,
    course_id: str = None,
    parent_id: Optional[str] = None,
    content: Optional[str] = None,
    tags: List[str] = None,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """
    创建知识点

    - **name**: 知识点名称
    - **description**: 描述
    - **course_id**: 所属课程ID
    - **parent_id**: 父知识点ID
    - **content**: 知识内容
    - **tags**: 标签列表
    """
    if not name:
        raise ValidationException("Knowledge name is required", "name")
    if not course_id:
        raise ValidationException("Course ID is required", "course_id")

    knowledge = await store.create_knowledge(
        name=name,
        description=description,
        course_id=course_id,
        parent_id=parent_id,
        content=content,
        tags=tags or []
    )
    return BaseResponse(data=knowledge)


@router.get("", response_model=BaseResponse[PaginatedResponse[KnowledgePoint]])
async def list_knowledge(
    course_id: Optional[str] = Query(None, description="课程ID筛选"),
    parent_id: Optional[str] = Query(None, description="父知识点筛选"),
    tags: Optional[str] = Query(None, description="标签筛选"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """
    获取知识点列表
    """
    result = await store.list_knowledge(
        course_id=course_id,
        parent_id=parent_id,
        tags=tags.split(",") if tags else None,
        page=page,
        size=size
    )
    return BaseResponse(data=result)


@router.get("/{knowledge_id}", response_model=BaseResponse[KnowledgePoint])
async def get_knowledge(
    knowledge_id: str,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """获取知识点详情"""
    knowledge = await store.get_knowledge(knowledge_id)
    return BaseResponse(data=knowledge)


@router.put("/{knowledge_id}", response_model=BaseResponse[KnowledgePoint])
async def update_knowledge(
    knowledge_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """更新知识点"""
    knowledge = await store.update_knowledge(
        knowledge_id=knowledge_id,
        name=name,
        description=description,
        content=content,
        tags=tags
    )
    return BaseResponse(data=knowledge)


@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """删除知识点"""
    await store.delete_knowledge(knowledge_id)
    return BaseResponse(message=f"Knowledge {knowledge_id} deleted")


@router.post("/search")
async def search_knowledge(
    query: str,
    course_id: Optional[str] = None,
    top_k: int = 10,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """
    语义搜索知识点

    - **query**: 搜索查询
    - **course_id**: 限定课程范围
    - **top_k**: 返回结果数量
    """
    results = await store.search(
        query=query,
        course_id=course_id,
        top_k=top_k
    )
    return BaseResponse(data=results)


@router.post("/import")
async def import_knowledge(
    course_id: str,
    file: UploadFile = File(...),
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """
    批量导入知识点

    支持JSON、CSV格式
    """
    content = await file.read()
    result = await store.import_knowledge(
        course_id=course_id,
        content=content,
        filename=file.filename
    )
    return BaseResponse(data=result)


@router.post("/migrate")
async def migrate_knowledge(
    source_course_id: str,
    target_course_id: str,
    knowledge_ids: List[str],
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """
    知识迁移

    将知识点从一个课程迁移到另一个课程
    """
    result = await store.migrate_knowledge(
        source_course_id=source_course_id,
        target_course_id=target_course_id,
        knowledge_ids=knowledge_ids
    )
    return BaseResponse(data=result)


@router.get("/{knowledge_id}/children")
async def get_knowledge_children(
    knowledge_id: str,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """获取子知识点"""
    children = await store.get_children(knowledge_id)
    return BaseResponse(data=children)


@router.get("/{knowledge_id}/path")
async def get_knowledge_path(
    knowledge_id: str,
    store: KnowledgeStore = Depends(get_knowledge_store)
):
    """获取知识点路径（从根到此知识点）"""
    path = await store.get_knowledge_path(knowledge_id)
    return BaseResponse(data=path)
