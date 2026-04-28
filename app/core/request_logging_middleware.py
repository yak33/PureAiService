"""
请求日志中间件
记录所有API请求和响应的详细信息

作者: ZHANGCHAO
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from app.core.logger import app_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志记录中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志"""
        # 记录请求开始时间
        start_time = time.time()
        
        # 生成请求ID
        request_id = f"{int(start_time * 1000)}"
        
        # 记录请求信息
        await self._log_request(request, request_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 读取并记录响应信息
        response = await self._log_response(response, request_id, process_time)
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    async def _log_request(self, request: Request, request_id: str):
        """记录请求详细信息"""
        try:
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client": f"{request.client.host}:{request.client.port}" if request.client else "unknown",
            }
            
            # 查询参数
            if request.query_params:
                log_data["query_params"] = dict(request.query_params)
            
            # 请求体
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    
                    # 重置请求体以便后续处理
                    async def receive():
                        return {"type": "http.request", "body": body}
                    request._receive = receive
                    
                    if body:
                        content_type = request.headers.get("content-type", "")
                        if "application/json" in content_type:
                            try:
                                log_data["body"] = json.loads(body.decode())
                            except Exception:
                                log_data["body"] = body.decode()[:500]
                        elif "multipart/form-data" in content_type:
                            log_data["body"] = "[FormData - 文件上传]"
                        else:
                            log_data["body"] = body.decode()[:500]
                except Exception:
                    log_data["body"] = "[无法读取请求体]"
            
            # 打印请求日志
            app_logger.info("=" * 80)
            app_logger.info(f"📥 请求 [{request_id}]")
            app_logger.info(f"  方法: {log_data['method']}")
            app_logger.info(f"  路径: {log_data['path']}")
            app_logger.info(f"  客户端: {log_data['client']}")
            
            if "query_params" in log_data:
                app_logger.info(f"  查询参数: {json.dumps(log_data['query_params'], ensure_ascii=False)}")
            
            if "body" in log_data:
                if isinstance(log_data['body'], dict):
                    app_logger.info(f"  请求体: {json.dumps(log_data['body'], ensure_ascii=False, indent=2)}")
                else:
                    app_logger.info(f"  请求体: {log_data['body']}")
                    
        except Exception as e:
            app_logger.error(f"记录请求日志失败: {e}")
    
    async def _log_response(self, response: Response, request_id: str, process_time: float):
        """记录响应信息"""
        try:
            # 流式响应不缓冲 body，避免破坏流式传输和 OOM 风险
            if isinstance(response, StreamingResponse):
                app_logger.info(f"📤 响应 [{request_id}]")
                app_logger.info(f"  状态码: {response.status_code}")
                app_logger.info(f"  处理时间: {process_time:.3f}秒")
                app_logger.info(f"  响应体: [StreamingResponse - 不记录]")
                app_logger.info("=" * 80)
                return response

            # 非流式响应正常读取 body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # 解析响应体
            response_data = None
            if response_body:
                try:
                    response_data = json.loads(response_body.decode())
                except Exception:
                    response_data = response_body.decode()[:500]

            # 打印响应日志
            app_logger.info(f"📤 响应 [{request_id}]")
            app_logger.info(f"  状态码: {response.status_code}")
            app_logger.info(f"  处理时间: {process_time:.3f}秒")

            if response_data:
                if isinstance(response_data, dict):
                    app_logger.info(f"  响应体: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                else:
                    app_logger.info(f"  响应体: {response_data}")

            app_logger.info("=" * 80)

            # 重新构造响应（因为body已经被读取）
            from starlette.responses import Response as StarletteResponse
            return StarletteResponse(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        except Exception as e:
            app_logger.error(f"记录响应日志失败: {e}")
            return response
