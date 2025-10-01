import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import app_logger
from app.api.ai_endpoints import router as ai_router
from app.api.auth_endpoints import router as auth_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="纯AI服务API - 所有功能通过大模型API实现",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务（前端构建后的文件）
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    # 为前端路由提供fallback
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

# 健康检查端点（必须在其他路由之前注册，避免被认证拦截）
@app.get("/api/v1/ai/health")
async def health_check():
    """
    公开的健康检查接口（不需要认证）
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# 注册认证路由（无需权限）
app.include_router(auth_router, prefix="/api/v1")

# 注册AI路由（需要权限）
app.include_router(ai_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    app_logger.info(f"{settings.app_name} v{settings.app_version} 启动成功")
    app_logger.info(f"服务运行在: http://{settings.host}:{settings.port}")

@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info(f"{settings.app_name} 服务关闭")

@app.get("/")
async def root():
    return {
        "message": f"欢迎使用 {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )