"""
纯AI服务模块
完全基于大模型API调用实现各种功能，不依赖第三方处理库
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List

import httpx
from httpx import RequestError, ResponseNotRead
from app.core.config import settings
from app.core.logger import app_logger
from app.core.siliconflow_models import SILICONFLOW_MODELS, DEFAULT_MODEL, RECOMMENDED_MODELS


class PureAIService:
    """纯AI服务类，所有功能通过大模型API实现"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")
        self.timeout = settings.api_timeout
        # 硅基流动可能需要特定的请求头格式
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.default_model = settings.default_model or DEFAULT_MODEL
        self._timeout = httpx.Timeout(self.timeout)
        
    async def call_ai(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> Dict[str, Any]:
        """
        调用AI模型的通用接口
        
        Args:
            messages: 消息列表
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
        """
        try:
            model = model or self.default_model

            # 移除敏感信息，只记录部分内容
            log_messages = json.dumps(messages, ensure_ascii=False)

            # 调试信息：检查API配置
            app_logger.info(f"API配置检查 - base_url: {self.base_url}")
            app_logger.info(f"API配置检查 - api_key前8位: {self.api_key[:8]}...")
            app_logger.debug(f"API配置检查 - headers: {self._redact_headers(self.headers)}")

            app_logger.info(
                "开始调用AI模型: model=%s, temperature=%s, max_tokens=%s, stream=%s",
                model,
                temperature,
                max_tokens,
                stream,
            )
            app_logger.debug(f"AI请求内容: {log_messages}")

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self._timeout,
            ) as client:
                endpoint = "/chat/completions"
                app_logger.info(f"完整请求路径: {endpoint}")
                app_logger.debug(f"请求payload: {payload}")

                if stream:
                    async with client.stream("POST", endpoint, json=payload) as response:
                        app_logger.info(f"响应状态码: {response.status_code}")
                        app_logger.info(f"响应头: {dict(response.headers)}")

                        if not response.is_success:
                            return await self._build_error_response(response)

                        return await self._consume_stream_response(response)

                response = await client.post(endpoint, json=payload)
                app_logger.info(f"响应状态码: {response.status_code}")
                app_logger.info(f"响应头: {dict(response.headers)}")

                if not response.is_success:
                    return await self._build_error_response(response)

                try:
                    result = response.json()
                except json.JSONDecodeError as exc:
                    app_logger.error(f"解析响应JSON失败: {exc}")
                    return {
                        "success": False,
                        "error": f"解析响应JSON失败: {exc}",
                        "status_code": response.status_code,
                        "details": response.text,
                    }

                usage = result.get("usage", {})
                finish_reason = result.get("choices", [{}])[0].get("finish_reason")

                app_logger.info(
                    "AI模型调用成功: model=%s, finish_reason=%s",
                    result.get("model"),
                    finish_reason,
                )
                app_logger.debug(f"AI响应 usage: {usage}")

                return {
                    "success": True,
                    "content": result.get("choices", [{}])[0].get("message", {}).get("content"),
                    "model": result.get("model"),
                    "usage": usage,
                    "finish_reason": finish_reason,
                }

        except RequestError as exc:
            app_logger.error(f"HTTP请求异常: {exc}")
            return {
                "success": False,
                "error": f"HTTP请求异常: {exc}",
            }
        except Exception as e:
            app_logger.exception("AI API调用异常")
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
            }

    async def _consume_stream_response(self, response: httpx.Response) -> Dict[str, Any]:
        content_parts: List[str] = []
        model_name: Optional[str] = None
        usage_info: Dict[str, Any] = {}
        finish_reason: Optional[str] = None

        try:
            async for line in response.aiter_lines():
                if not line:
                    continue
                if not line.startswith("data:"):
                    continue

                data_str = line[5:].strip()
                if not data_str:
                    continue
                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if "choices" in data and data["choices"]:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        content_parts.append(delta["content"])
                    finish_reason = data["choices"][0].get("finish_reason") or finish_reason
                if "model" in data:
                    model_name = data["model"]
                if "usage" in data:
                    usage_info = data["usage"]

            full_content = "".join(content_parts)
            app_logger.info(
                "AI模型流式调用成功: model=%s, finish_reason=%s",
                model_name,
                finish_reason,
            )
            app_logger.debug(f"AI响应 usage: {usage_info}")

            return {
                "success": True,
                "content": full_content,
                "model": model_name,
                "usage": usage_info,
                "finish_reason": finish_reason,
            }
        except Exception as exc:
            app_logger.error(f"解析流式响应失败: {exc}")
            return {
                "success": False,
                "error": f"解析流式响应失败: {exc}",
            }

    async def _build_error_response(self, response: httpx.Response) -> Dict[str, Any]:
        raw_text = await self._read_response_text(response)
        parsed_payload: Optional[Dict[str, Any]] = None
        if raw_text:
            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    parsed_payload = parsed
            except json.JSONDecodeError:
                parsed_payload = None

        message = self._extract_error_message(parsed_payload) if parsed_payload else None
        message = message or raw_text or f"HTTP {response.status_code}"

        app_logger.error(
            "AI API调用失败: status=%s, message=%s",
            response.status_code,
            message,
        )

        return {
            "success": False,
            "error": message,
            "status_code": response.status_code,
            "details": parsed_payload or raw_text,
        }

    async def _read_response_text(self, response: httpx.Response) -> str:
        try:
            content = await response.aread()
        except ResponseNotRead:
            content = response.content

        if not content:
            return ""
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return str(content)

    def _extract_error_message(self, payload: Dict[str, Any]) -> Optional[str]:
        for key in ("error", "message", "detail"):
            if key not in payload:
                continue
            value = payload[key]
            if isinstance(value, dict):
                for sub_key in ("message", "detail", "error"):
                    if sub_key in value and value[sub_key]:
                        return str(value[sub_key])
            elif value:
                return str(value)
        return None

    @staticmethod
    def _redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
        redacted: Dict[str, str] = {}
        for key, value in headers.items():
            if key.lower() == "authorization" and value.startswith("Bearer "):
                redacted[key] = "Bearer ****" + value[-4:]
            else:
                redacted[key] = value
        return redacted
    
    async def analyze_text(
        self,
        text: str,
        task: str = "analyze",
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本分析通用接口
        
        Args:
            text: 要分析的文本
            task: 任务类型 (analyze, summarize, extract, translate, etc.)
            custom_prompt: 自定义提示词
            model: 使用的模型
        """
        # 根据任务类型选择合适的提示词
        task_prompts = {
            "analyze": "请详细分析以下文本的内容，提取关键信息，分析主题和要点。",
            "summarize": "请简明扼要地总结以下文本的主要内容，保留核心信息。",
            "extract": "请从以下文本中提取所有重要的实体、数字、日期和关键信息。",
            "translate": "请将以下文本翻译成中文（如果是中文则翻译成英文）。",
            "sentiment": "请分析以下文本的情感倾向（正面/负面/中性）和情感强度。",
            "classify": "请对以下文本进行分类，并说明分类依据。",
            "keywords": "请提取以下文本的关键词和主题词，按重要性排序。",
            "qa": "请基于以下文本回答用户的问题。"
        }
        
        prompt = custom_prompt or task_prompts.get(task, task_prompts["analyze"])
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的文本分析助手，能够准确理解和分析各种类型的文本内容。请用中文回答。"
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n文本内容：\n{text}"
            }
        ]
        
        result = await self.call_ai(messages, model=model)
        
        if result["success"]:
            return {
                "success": True,
                "task": task,
                "result": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        else:
            return result
    
    async def ocr_image(
        self,
        image_base64: str,
        language: str = "auto",
        detail_level: str = "high"
    ) -> Dict[str, Any]:
        """
        通过视觉语言模型进行OCR识别
        
        Args:
            image_base64: Base64编码的图片
            language: 识别语言
            detail_level: 识别精度 (high/medium/low)
        """
        # 使用支持视觉的模型
        vision_model = RECOMMENDED_MODELS.get("vision", "zai-org/GLM-4.5V")
        
        language_prompts = {
            "auto": "自动识别图片中的文字语言",
            "zh": "识别中文文字",
            "en": "识别英文文字",
            "mix": "识别中英文混合文字"
        }
        
        detail_prompts = {
            "high": "请尽可能详细地识别图片中的所有文字，包括小字、水印等",
            "medium": "请识别图片中的主要文字内容",
            "low": "请快速识别图片中的关键文字"
        }
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的OCR文字识别助手，能够准确识别图片中的文字内容。"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""请识别这张图片中的所有文字。
要求：
1. {language_prompts.get(language, language_prompts["auto"])}
2. {detail_prompts.get(detail_level, detail_prompts["medium"])}
3. 保持原始格式和布局
4. 如果有表格，请用markdown格式展示
5. 标注不确定的文字"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        result = await self.call_ai(messages, model=vision_model, temperature=0.1)
        
        if result["success"]:
            return {
                "success": True,
                "text": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        else:
            # 如果视觉模型失败，回退到普通模型
            app_logger.warning("视觉模型OCR失败，尝试其他方法")
            return {
                "success": False,
                "error": "OCR识别失败",
                "details": result.get("details")
            }
    
    async def analyze_document(
        self,
        content: str,
        doc_type: str = "auto",
        task: str = "analyze",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文档分析（通过大模型理解文档内容）
        
        Args:
            content: 文档内容（文本形式）
            doc_type: 文档类型 (pdf, word, excel, ppt, etc.)
            task: 任务类型
            custom_prompt: 自定义提示词
        """
        doc_prompts = {
            "pdf": "这是一个PDF文档的文本内容",
            "word": "这是一个Word文档的内容",
            "excel": "这是一个Excel表格的数据",
            "ppt": "这是一个PPT演示文稿的内容",
            "code": "这是源代码文件",
            "auto": "请自动识别文档类型"
        }
        
        task_prompts = {
            "analyze": "请分析这个文档的结构、主要内容和关键信息。",
            "summarize": "请为这个文档生成执行摘要。",
            "outline": "请提取这个文档的大纲结构。",
            "extract_data": "请提取文档中的所有数据、表格和数字信息。",
            "review": "请对这个文档进行专业审阅，指出优缺点。"
        }
        
        doc_context = doc_prompts.get(doc_type, doc_prompts["auto"])
        task_prompt = custom_prompt or task_prompts.get(task, task_prompts["analyze"])
        
        messages = [
            {
                "role": "system",
                "content": f"你是一个专业的文档分析专家。{doc_context}"
            },
            {
                "role": "user",
                "content": f"{task_prompt}\n\n文档内容：\n{content[:8000]}"  # 限制长度
            }
        ]
        
        # 对于长文档，使用默认模型
        model = None
        if len(content) > 4000:
            model = "zai-org/GLM-4.5"  # 使用默认模型处理长文档
        
        result = await self.call_ai(messages, model=model, max_tokens=3000)
        
        if result["success"]:
            return {
                "success": True,
                "doc_type": doc_type,
                "task": task,
                "analysis": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        else:
            return result
    
    async def code_assist(
        self,
        code: Optional[str] = None,
        task: str = "review",
        language: Optional[str] = None,
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码辅助功能
        
        Args:
            code: 源代码
            task: 任务类型 (review, optimize, explain, debug, generate)
            language: 编程语言
            requirements: 具体要求
        """
        # 使用默认模型处理代码
        code_model = RECOMMENDED_MODELS.get("chat", "zai-org/GLM-4.5")
        
        task_prompts = {
            "review": "请对以下代码进行代码审查，指出潜在问题和改进建议。",
            "optimize": "请优化以下代码，提高性能和可读性。",
            "explain": "请详细解释以下代码的功能和实现逻辑。",
            "debug": "请帮助调试以下代码，找出并修复错误。",
            "generate": "请根据需求生成代码。",
            "convert": f"请将以下代码转换为{language or 'Python'}。",
            "test": "请为以下代码编写单元测试。",
            "document": "请为以下代码生成详细的文档注释。"
        }
        
        prompt = task_prompts.get(task, task_prompts["review"])
        if requirements:
            prompt = f"{prompt}\n具体要求：{requirements}"
        
        content = f"{prompt}\n\n"
        if code:
            content += f"代码：\n```{language or ''}\n{code}\n```"
        else:
            content += f"需求：{requirements or '请生成一个示例代码'}"
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的编程助手，精通各种编程语言和最佳实践。"
            },
            {
                "role": "user",
                "content": content
            }
        ]
        
        result = await self.call_ai(
            messages, 
            model=code_model,
            temperature=0.3,  # 代码生成使用较低的温度
            max_tokens=3000
        )
        
        if result["success"]:
            return {
                "success": True,
                "task": task,
                "language": language,
                "result": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        else:
            return result
    
    async def custom_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        自定义对话接口
        
        Args:
            messages: 对话消息列表
            model: 使用的模型
            system_prompt: 系统提示词
            **kwargs: 其他参数
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        return await self.call_ai(messages, model=model, **kwargs)
    
    def list_available_models(self) -> Dict[str, Any]:
        """列出所有可用的模型"""
        available_models = []
        
        for category, models in SILICONFLOW_MODELS.items():
            for model_id, info in models.items():
                available_models.append({
                    "id": model_id,
                    "name": info["name"],
                    "category": category,
                    "description": info["description"],
                    "max_tokens": info.get("max_tokens", "N/A"),
                    "price": {
                        "input": info.get("input_price", 0),
                        "output": info.get("output_price", 0)
                    } if category != "image" else {
                        "per_image": info.get("price", 0)
                    }
                })
        
        return {
            "models": available_models,
            "default_model": self.default_model,
            "recommended": RECOMMENDED_MODELS
        }
    
    async def generate_image_description(
        self,
        prompt: str,
        model: str = "zai-org/GLM-4.5",
        style: str = "realistic",
        n: int = 1
    ) -> Dict[str, Any]:
        """
        生成详细的图像描述（可用于其他图像生成服务）
        
        Args:
            prompt: 基础描述
            model: 使用的模型
            style: 风格（realistic, artistic, cartoon等）
            n: 生成数量
        """
        style_prompts = {
            "realistic": "请生成一个超现实、高清、细节丰富的图像描述",
            "artistic": "请生成一个艺术风格、富有创意的图像描述",
            "cartoon": "请生成一个卡通风格、生动有趣的图像描述"
        }
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的图像描述生成器，能够将简单的描述转换为详细、生动的图像描述。"
            },
            {
                "role": "user",
                "content": f"{style_prompts.get(style, style_prompts['realistic'])}。\n\n基础描述：{prompt}\n\n请生成一个详细的图像描述，包括：\n1. 主体物体的详细特征\n2. 背景和环境\n3. 光线和色彩\n4. 氛围和情绪\n5. 艺术风格"
            }
        ]
        
        descriptions = []
        for i in range(n):
            result = await self.call_ai(messages, model=model, temperature=0.8)
            if result["success"]:
                descriptions.append({
                    "description": result["content"],
                    "style": style
                })
        
        if descriptions:
            return {
                "success": True,
                "descriptions": descriptions,
                "model": model,
                "count": len(descriptions)
            }
        else:
            return {
                "success": False,
                "error": "生成图像描述失败"
            }
