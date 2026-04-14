"""
Knowledge Middleware Service - Main Entry
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from shared.config import get_settings
from shared.exceptions import EduAgentException
from shared.database import init_database, db_manager
from .routers import knowledge, health
from .services.knowledge_store_db import KnowledgeStore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"Starting {settings.APP_NAME} - Knowledge Middleware Service")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # 初始化数据库
    db_path = os.path.join(os.path.dirname(__file__), "../../../data/eduagent.db")
    await init_database(db_path)
    logger.info(f"Database initialized: {db_path}")

    # 初始化知识存储
    app.state.knowledge_store = KnowledgeStore()

    yield

    logger.info("Shutting down Knowledge Middleware Service")
    await db_manager.close()


# 创建FastAPI应用
app = FastAPI(
    title="Knowledge Middleware Service",
    description="知识中间件服务 - 提供知识的存储、检索、迁移等功能",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# 异常处理器
@app.exception_handler(EduAgentException)
async def eduagent_exception_handler(request: Request, exc: EduAgentException):
    """处理自定义异常"""
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
            "data": exc.data
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识管理"])


# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "service": "Knowledge Middleware",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }
