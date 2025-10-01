"""
AI服务API端点
提供通用的AI调用接口，所有功能通过大模型实现
"""

import base64
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.pure_ai_service import PureAIService
from app.core.logger import app_logger
from app.core.config import settings
from app.core.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Services"], dependencies=[Depends(get_current_user)])

# 初始化AI服务
ai_service = PureAIService()


# 请求模型定义
class TextAnalysisRequest(BaseModel):
    text: str
    task: str = "analyze"
    custom_prompt: Optional[str] = None
    model: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False


class CodeRequest(BaseModel):
    code: Optional[str] = None
    task: str = "review"
    language: Optional[str] = None
    requirements: Optional[str] = None
    model: Optional[str] = None


class ImageDescriptionRequest(BaseModel):
    prompt: str
    model: str = "zai-org/GLM-4.5"  # 使用GLM模型生成文本描述
    style: str = "realistic"  # 风格：realistic, artistic, cartoon
    n: int = 1


@router.get("/models")
async def list_models():
    """
    获取所有可用的AI模型列表
    """
    try:
        return ai_service.list_available_models()
    except Exception as e:
        app_logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/analyze")
async def analyze_text(request: TextAnalysisRequest):
    """
    文本分析接口
    支持多种分析任务：analyze, summarize, extract, translate, sentiment, classify, keywords
    """
    app_logger.info(f"收到文本分析请求: task={request.task}, model={request.model}")
    app_logger.debug(f"文本分析内容: {request.text[:200]}...")  # 只记录前200个字符以防过长
    try:
        result = await ai_service.analyze_text(
            text=request.text,
            task=request.task,
            custom_prompt=request.custom_prompt,
            model=request.model
        )
        return result
    except Exception as e:
        app_logger.error(f"文本分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    通用对话接口
    支持多轮对话和自定义系统提示词
    """
    try:
        result = await ai_service.custom_chat(
            messages=request.messages,
            model=request.model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        return result
    except Exception as e:
        app_logger.error(f"对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code")
async def code_assist(request: CodeRequest):
    """
    代码辅助接口
    支持代码审查、优化、解释、调试、生成等任务
    """
    try:
        result = await ai_service.code_assist(
            code=request.code,
            task=request.task,
            language=request.language,
            requirements=request.requirements
        )
        return result
    except Exception as e:
        app_logger.error(f"代码辅助失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    detail_level: str = Form("medium")
):
    """
    OCR文字识别接口
    通过视觉语言模型识别图片中的文字
    
    注意：图片的高和宽都必须大于28像素
    """
    try:
        # 读取图片
        contents = await file.read()
        
        # 检查图片大小
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        # 检查文件大小限制
        max_size = settings.max_file_size
        if len(contents) > max_size:
            raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({max_size} 字节)")
        
        # 转换为base64
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        result = await ai_service.ocr_image(
            image_base64=image_base64,
            language=language,
            detail_level=detail_level
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"OCR识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/describe")
async def generate_image_description(request: ImageDescriptionRequest):
    """
    图像描述生成接口
    根据简单描述生成详细的图像描述（可用于其他图像生成服务）
    """
    try:
        result = await ai_service.generate_image_description(
            prompt=request.prompt,
            model=request.model,
            style=request.style,
            n=request.n
        )
        return result
    except Exception as e:
        app_logger.error(f"图像描述生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class QuickAIRequest(BaseModel):
    prompt: str
    model: Optional[str] = "moonshotai/Kimi-K2-Instruct-0905"
    stream: bool = False


@router.post("/quick")
async def quick_ai(request: QuickAIRequest):
    """
    快速AI调用接口
    直接输入提示词获取AI回复
    """
    try:
        messages = [
            {
                "role": "user",
                "content": request.prompt
            }
        ]
        # 如果没有指定模型，使用默认的 Kimi 模型
        model = request.model if request.model else "moonshotai/Kimi-K2-Instruct-0905"
        result = await ai_service.call_ai(messages, model=model, stream=request.stream)
        return result
    except Exception as e:
        app_logger.error(f"快速AI调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_process(
    tasks: List[Dict[str, Any]] = Body(...)
):
    """
    批量处理接口
    支持一次性处理多个AI任务
    """
    results = []
    for task in tasks:
        try:
            task_type = task.get("type", "text")
            
            if task_type == "text":
                result = await ai_service.analyze_text(
                    text=task.get("text", ""),
                    task=task.get("task", "analyze"),
                    custom_prompt=task.get("prompt"),
                    model=task.get("model")
                )
            elif task_type == "code":
                result = await ai_service.code_assist(
                    code=task.get("code"),
                    task=task.get("task", "review"),
                    language=task.get("language"),
                    requirements=task.get("requirements")
                )
            elif task_type == "chat":
                result = await ai_service.custom_chat(
                    messages=task.get("messages", []),
                    model=task.get("model"),
                    system_prompt=task.get("system_prompt")
                )
            else:
                result = {"success": False, "error": f"Unknown task type: {task_type}"}
            
            results.append({
                "task_id": task.get("id"),
                "result": result
            })
        except Exception as e:
            results.append({
                "task_id": task.get("id"),
                "error": str(e)
            })
    
    return {"results": results}


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "AI Service",
        "models_available": True
    }


@router.post("/image/edit")
async def edit_image(
    file: UploadFile = File(...),
    instruction: str = Form(...)
):
    """
    图片编辑接口
    使用 Qwen-Image-Edit-2509 模型根据指令编辑图片
    """
    try:
        # 读取图片
        contents = await file.read()
        
        # 检查图片大小
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        # 检查文件大小限制
        max_size = settings.max_file_size
        if len(contents) > max_size:
            raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({max_size} 字节)")
        
        # 转换为base64
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        result = await ai_service.edit_image(
            image_base64=image_base64,
            instruction=instruction
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"图片编辑失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/config")
async def debug_config():
    """
    调试配置信息（临时）
    """
    app_logger.debug("收到调试配置请求")
    return {
        "api_key_length": len(ai_service.api_key) if ai_service.api_key else 0,
        "api_key_prefix": ai_service.api_key[:10] if ai_service.api_key else None,
        "base_url": ai_service.base_url,
        "default_model": ai_service.default_model
    }