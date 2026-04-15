"""
API Gateway - 统一入口网关
将前端请求路由到各个后端微服务
"""

import sys
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="EduAgent API Gateway",
    description="统一API网关 - 路由请求到各个微服务",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 微服务地址配置
SERVICES = {
    "/api/v1/agents": "http://localhost:8001",
    "/api/v1/knowledge": "http://localhost:8002",
    "/api/v1/adapters": "http://localhost:8003",
    "/api/v1/webhooks": "http://localhost:8003",
    "/api/v1/qa": "http://localhost:8005",
    "/api/v1/grading": "http://localhost:8005",
    "/api/v1/warning": "http://localhost:8005",
    "/api/v1/exercise": "http://localhost:8005",
}

# HTTP客户端
client = httpx.AsyncClient(timeout=30.0, trust_env=False)


def get_service_url(path: str) -> str:
    """根据路径获取目标服务URL"""
    for prefix, url in SERVICES.items():
        if path.startswith(prefix):
            return url + path
    return None


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """代理所有请求到对应的微服务"""

    # 构建完整路径
    full_path = f"/{path}"

    # 获取目标服务URL
    target_url = get_service_url(full_path)

    if not target_url:
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": f"No service found for path: {full_path}"}
        )

    try:
        # 获取请求体
        body = await request.body()

        # 构建请求头
        headers = dict(request.headers)
        headers.pop("host", None)  # 移除host头

        # 转发请求
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params)
        )

        # 返回响应
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        )

    except httpx.ConnectError:
        logger.error(f"Failed to connect to service: {target_url}")
        return JSONResponse(
            status_code=503,
            content={"code": 503, "message": f"Service unavailable: {target_url}"}
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": str(e)}
        )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/")
async def root():
    """根路由"""
    return {
        "service": "EduAgent API Gateway",
        "version": "0.1.0",
        "docs": "/docs",
        "services": list(SERVICES.keys())
    }


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    await client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
