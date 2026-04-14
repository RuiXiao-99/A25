"""
共享配置模块
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "EduAgent Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/eduagent"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017/eduagent"
    MONGODB_DATABASE: str = "eduagent"

    # GLM AI配置
    GLM_API_KEY: str = ""
    GLM_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4"
    GLM_MODEL: str = "glm-4"
    GLM_MAX_TOKENS: int = 2048
    GLM_TEMPERATURE: float = 0.7

    # 安全配置
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    API_KEY_SALT: str = "your-api-key-salt"

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # 服务端口配置
    GATEWAY_PORT: int = 8000
    AGENT_FRAMEWORK_PORT: int = 8001
    KNOWLEDGE_MIDDLEWARE_PORT: int = 8002
    PLATFORM_ADAPTER_PORT: int = 8003
    DATA_FUSION_PORT: int = 8004
    INTELLIGENT_ENGINE_PORT: int = 8005

    # 限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # 缓存配置
    CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（缓存）"""
    return Settings()


# 服务发现配置
SERVICE_REGISTRY = {
    "agent-framework": {
        "host": "localhost",
        "port": 8001,
        "health_check": "/health"
    },
    "knowledge-middleware": {
        "host": "localhost",
        "port": 8002,
        "health_check": "/health"
    },
    "platform-adapter": {
        "host": "localhost",
        "port": 8003,
        "health_check": "/health"
    },
    "data-fusion": {
        "host": "localhost",
        "port": 8004,
        "health_check": "/health"
    },
    "intelligent-engine": {
        "host": "localhost",
        "port": 8005,
        "health_check": "/health"
    }
}


def get_service_url(service_name: str) -> str:
    """获取服务URL"""
    if service_name not in SERVICE_REGISTRY:
        raise ValueError(f"Unknown service: {service_name}")

    service = SERVICE_REGISTRY[service_name]
    return f"http://{service['host']}:{service['port']}"
