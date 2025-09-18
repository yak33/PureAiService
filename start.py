#!/usr/bin/env python
"""
纯AI服务快速启动脚本
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 正在启动纯AI服务...")
    print("=" * 60)
    print("📌 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("📊 交互文档: http://localhost:8000/redoc")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
