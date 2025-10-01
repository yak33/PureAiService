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


class PureAIService:
    """纯AI服务类，所有功能通过大模型API实现"""
    
    def __init__(self):
        """初始化AI服务配置"""
        # 从配置中获取API密钥和基础URL
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url.rstrip("/")
        self.timeout = settings.api_timeout
        
        # 设置请求头，硅基流动平台需要特定的认证格式
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 设置默认模型和超时配置
        self.default_model = settings.default_model
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
            messages: 消息列表，包含角色和内容
            model: 使用的模型名称，如果未指定则使用默认模型
            temperature: 温度参数，控制生成文本的随机性(0-1)
            max_tokens: 最大token数，限制生成文本的长度
            stream: 是否使用流式输出，True为流式，False为一次性返回
            
        Returns:
            Dict[str, Any]: 包含调用结果的字典
                - success: 调用是否成功
                - content: AI生成的内容
                - model: 实际使用的模型名称
                - usage: token使用情况
                - finish_reason: 完成原因
                - error: 错误信息(如果失败)
        """
        try:
            # 检查是否提供了模型
            if not model:
                return {
                    "success": False,
                    "error": "未指定模型，请先在模型管理页面配置可用模型"
                }

            # 移除敏感信息，只记录部分内容用于日志
            log_messages = json.dumps(messages, ensure_ascii=False)

            # 记录API配置信息用于调试
            app_logger.info(f"API配置检查 - base_url: {self.base_url}")
            app_logger.info(f"API配置检查 - api_key前8位: {self.api_key[:8]}...")
            app_logger.debug(f"API配置检查 - headers: {self._redact_headers(self.headers)}")

            # 记录调用信息
            app_logger.info(
                "开始调用AI模型: model=%s, temperature=%s, max_tokens=%s, stream=%s",
                model,
                temperature,
                max_tokens,
                stream,
            )
            app_logger.debug(f"AI请求内容: {log_messages}")

            # 构造请求参数
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            # 创建异步HTTP客户端并发送请求
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self._timeout,
            ) as client:
                endpoint = "/chat/completions"
                app_logger.info(f"完整请求路径: {endpoint}")
                app_logger.debug(f"请求payload: {payload}")

                # 根据是否流式输出选择不同的处理方式
                if stream:
                    async with client.stream("POST", endpoint, json=payload) as response:
                        app_logger.info(f"响应状态码: {response.status_code}")
                        app_logger.info(f"响应头: {dict(response.headers)}")

                        # 处理错误响应
                        if not response.is_success:
                            return await self._build_error_response(response)

                        # 处理流式响应
                        return await self._consume_stream_response(response)

                # 非流式请求处理
                response = await client.post(endpoint, json=payload)
                app_logger.info(f"响应状态码: {response.status_code}")
                app_logger.info(f"响应头: {dict(response.headers)}")

                # 处理错误响应
                if not response.is_success:
                    return await self._build_error_response(response)

                # 解析JSON响应
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

                # 提取响应信息
                usage = result.get("usage", {})
                finish_reason = result.get("choices", [{}])[0].get("finish_reason")

                # 记录成功调用信息
                app_logger.info(
                    "AI模型调用成功: model=%s, finish_reason=%s",
                    result.get("model"),
                    finish_reason,
                )
                app_logger.debug(f"AI响应 usage: {usage}")

                # 返回成功结果
                return {
                    "success": True,
                    "content": result.get("choices", [{}])[0].get("message", {}).get("content"),
                    "model": result.get("model"),
                    "usage": usage,
                    "finish_reason": finish_reason,
                }

        except RequestError as exc:
            # 处理HTTP请求异常
            app_logger.error(f"HTTP请求异常: {exc}")
            return {
                "success": False,
                "error": f"HTTP请求异常: {exc}",
            }
        except Exception as e:
            # 处理其他异常
            app_logger.exception("AI API调用异常")
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
            }

    async def _consume_stream_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        处理流式响应数据
        
        Args:
            response: HTTP响应对象
            
        Returns:
            Dict[str, Any]: 解析后的响应数据
                - success: 是否成功
                - content: 响应内容
                - model: 模型名称
                - usage: 使用情况
                - finish_reason: 完成原因
        """
        # 存储响应内容的各个部分
        content_parts: List[str] = []
        model_name: Optional[str] = None
        usage_info: Dict[str, Any] = {}
        finish_reason: Optional[str] = None

        try:
            # 逐行读取流式响应
            async for line in response.aiter_lines():
                # 跳过空行
                if not line:
                    continue
                # 只处理以"data:"开头的行
                if not line.startswith("data:"):
                    continue

                # 提取数据部分并去除首尾空格
                data_str = line[5:].strip()
                if not data_str:
                    continue
                # 遇到结束标记则停止处理
                if data_str == "[DONE]":
                    break

                # 解析JSON数据
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    # JSON解析失败则跳过该行
                    continue

                # 提取响应内容
                if "choices" in data and data["choices"]:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        # 确保content不是None后再添加到列表中
                        if content is not None:
                            content_parts.append(content)
                    # 获取完成原因
                    finish_reason = data["choices"][0].get("finish_reason") or finish_reason
                # 提取模型名称
                if "model" in data:
                    model_name = data["model"]
                # 提取使用情况
                if "usage" in data:
                    usage_info = data["usage"]

            # 将所有内容片段合并成完整内容
            full_content = "".join(content_parts)
            
            # 记录成功日志
            app_logger.info(
                "AI模型流式调用成功: model=%s, finish_reason=%s",
                model_name,
                finish_reason,
            )
            app_logger.debug(f"AI响应 usage: {usage_info}")

            # 返回解析结果
            return {
                "success": True,
                "content": full_content,
                "model": model_name,
                "usage": usage_info,
                "finish_reason": finish_reason,
            }
        except Exception as exc:
            # 处理解析异常
            app_logger.error(f"解析流式响应失败: {exc}")
            return {
                "success": False,
                "error": f"解析流式响应失败: {exc}",
            }

    async def _build_error_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        构建错误响应
        
        Args:
            response: HTTP响应对象
            
        Returns:
            Dict[str, Any]: 错误响应数据
        """
        # 读取响应文本
        raw_text = await self._read_response_text(response)
        parsed_payload: Optional[Dict[str, Any]] = None
        
        # 尝试解析JSON格式的错误信息
        if raw_text:
            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    parsed_payload = parsed
            except json.JSONDecodeError:
                parsed_payload = None

        # 提取错误消息
        message = self._extract_error_message(parsed_payload) if parsed_payload else None
        message = message or raw_text or f"HTTP {response.status_code}"

        # 记录错误日志
        app_logger.error(
            "AI API调用失败: status=%s, message=%s",
            response.status_code,
            message,
        )

        # 返回错误响应
        return {
            "success": False,
            "error": message,
            "status_code": response.status_code,
            "details": parsed_payload or raw_text,
        }

    async def _read_response_text(self, response: httpx.Response) -> str:
        """
        读取响应文本内容
        
        Args:
            response: HTTP响应对象
            
        Returns:
            str: 响应文本内容
        """
        try:
            content = await response.aread()
        except ResponseNotRead:
            content = response.content

        # 处理空内容
        if not content:
            return ""
        # 处理字节内容
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return str(content)

    def _extract_error_message(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        从响应载荷中提取错误消息
        
        Args:
            payload: 响应载荷字典
            
        Returns:
            Optional[str]: 提取的错误消息，如果未找到则返回None
        """
        # 尝试从常见的错误字段中提取消息
        for key in ("error", "message", "detail"):
            if key not in payload:
                continue
            value = payload[key]
            if isinstance(value, dict):
                # 如果值是字典，继续深入查找
                for sub_key in ("message", "detail", "error"):
                    if sub_key in value and value[sub_key]:
                        return str(value[sub_key])
            elif value:
                return str(value)
        return None

    @staticmethod
    def _redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """
        对请求头中的敏感信息进行脱敏处理
        
        Args:
            headers: 原始请求头字典
            
        Returns:
            Dict[str, str]: 脱敏后的请求头字典
        """
        redacted: Dict[str, str] = {}
        for key, value in headers.items():
            # 对Authorization头进行脱敏处理，只显示前缀和后4位
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
            text: 要分析的文本内容
            task: 任务类型，支持 analyze(分析)、summarize(摘要)、extract(提取)、
                  translate(翻译)、sentiment(情感分析)、classify(分类)、keywords(关键词)等
            custom_prompt: 自定义提示词，如果提供则覆盖默认提示词
            model: 使用的模型名称，如果未指定则使用默认模型
            
        Returns:
            Dict[str, Any]: 文本分析结果
                - success: 是否成功
                - task: 任务类型
                - result: 分析结果内容
                - model: 实际使用的模型名称
                - usage: token使用情况
        """
        # 根据任务类型定义不同的提示词模板
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
        
        # 选择提示词：优先使用自定义提示词，其次根据任务类型选择，最后使用默认分析提示词
        prompt = custom_prompt or task_prompts.get(task, task_prompts["analyze"])
        
        # 构造对话消息
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
        
        # 调用AI模型进行文本分析
        result = await self.call_ai(messages, model=model)
        
        # 处理分析结果
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
            image_base64: Base64编码的图片数据
            language: 识别语言，支持 auto(自动)、zh(中文)、en(英文)、mix(中英文混合)
            detail_level: 识别精度，支持 high(高精度)、medium(标准精度)、low(快速识别)
            
        Returns:
            Dict[str, Any]: OCR识别结果
                - success: 是否成功
                - text: 识别出的文字内容
                - model: 实际使用的模型名称
                - usage: token使用情况
                - error: 错误信息(如果失败)
        """
        # 检查是否提供了模型
        if not model:
            return {
                "success": False,
                "error": "未指定模型，请先在模型管理页面配置可用的视觉模型"
            }
        
        vision_model = model
        
        # 定义不同语言的识别提示词
        language_prompts = {
            "auto": "自动识别图片中的文字语言",
            "zh": "识别中文文字",
            "en": "识别英文文字",
            "mix": "识别中英文混合文字"
        }
        
        # 定义不同精度级别的识别要求
        detail_prompts = {
            "high": "请尽可能详细地识别图片中的所有文字，包括小字、水印等",
            "medium": "请识别图片中的主要文字内容",
            "low": "请快速识别图片中的关键文字"
        }
        
        # 构造包含图片和指令的多模态消息
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
4. 如果有表格，请用代码格式展示
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
        
        # 调用视觉模型进行OCR识别，使用较低的温度参数以提高准确性
        result = await self.call_ai(messages, model=vision_model, temperature=0.1)
        
        # 处理识别结果
        if result["success"]:
            return {
                "success": True,
                "text": result["content"],
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        else:
            # 如果视觉模型识别失败，记录警告日志并返回错误信息
            app_logger.warning("视觉模型OCR失败，尝试其他方法")
            return {
                "success": False,
                "error": "OCR识别失败",
                "details": result.get("details")
            }
    
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
            code: 源代码内容，需要进行分析或处理的代码
            task: 任务类型，支持 review(代码审查)、optimize(优化)、explain(解释)、
                  debug(调试)、generate(生成)、convert(转换)、test(测试)、document(文档)等
            language: 编程语言类型，如 Python、JavaScript、Java 等
            requirements: 具体需求描述，用于代码生成或特定任务的详细要求
            
        Returns:
            Dict[str, Any]: 代码辅助结果
                - success: 是否成功
                - task: 任务类型
                - language: 编程语言
                - result: 处理结果内容
                - model: 实际使用的模型名称
                - usage: token使用情况
        """
        # 检查是否提供了模型
        if not model:
            return {
                "success": False,
                "error": "未指定模型，请先在模型管理页面配置可用的对话模型"
            }
        
        code_model = model
        
        # 定义不同代码任务的提示词模板
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
        
        # 选择任务提示词，并添加具体需求（如果提供）
        prompt = task_prompts.get(task, task_prompts["review"])
        if requirements:
            prompt = f"{prompt}\n具体要求：{requirements}"
        
        # 构造包含代码和指令的内容
        content = f"{prompt}\n\n"
        if code:
            # 如果提供了代码，则包含代码块
            content += f"代码：\n```{language or ''}\n{code}\n```"
        else:
            # 如果没有提供代码，则使用需求描述
            content += f"需求：{requirements or '请生成一个示例代码'}"
        
        # 构造对话消息
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
        
        # 调用AI模型进行代码辅助，使用较低的温度参数以提高代码准确性
        result = await self.call_ai(
            messages, 
            model=code_model,
            temperature=0.3,  # 代码生成使用较低的温度
            max_tokens=3000
        )
        
        # 处理结果
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
        自定义对话接口，允许用户构建自己的对话消息并调用AI模型
        
        Args:
            messages: 对话消息列表，每个消息包含role(角色)和content(内容)
            model: 使用的模型名称，如果未指定则使用默认模型
            system_prompt: 系统提示词，如果提供则会添加到消息列表开头
            **kwargs: 其他参数，如temperature、max_tokens、stream等
            
        Returns:
            Dict[str, Any]: 对话结果，格式与call_ai方法返回值相同
        """
        # 如果提供了系统提示词，则将其添加到消息列表开头
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # 调用通用AI接口
        return await self.call_ai(messages, model=model, **kwargs)
    
    def list_available_models(self) -> Dict[str, Any]:
        """
        列出所有可用的AI模型（从用户配置文件读取）
        
        Returns:
            Dict[str, Any]: 包含所有可用模型信息的字典
                - models: 模型列表
                - total: 模型总数
                - source: 数据来源（config/default）
        """
        from app.core.models_config_manager import models_config_manager
        
        # 从配置文件读取用户启用的模型
        enabled_models = models_config_manager.get_enabled_models()
        
        if enabled_models:
            # 如果有配置的模型，返回配置的模型列表
            return {
                "models": enabled_models,
                "total": len(enabled_models),
                "source": "config",
                "message": "使用用户配置的模型列表"
            }
        else:
            # 如果没有配置，返回默认提示
            return {
                "models": [],
                "total": 0,
                "source": "empty",
                "message": "请前往模型管理页面选择要使用的模型"
            }
    
    async def get_platform_models(
        self,
        model_type: Optional[str] = None,
        sub_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从硅基流动平台获取用户可用的模型列表
        
        Args:
            model_type: 模型类型，可选 text/image/audio/video
            sub_type: 模型子类型，如 chat/embedding/reranker/text-to-image等
            
        Returns:
            Dict[str, Any]: 平台返回的模型列表
                - success: 是否成功
                - data: 模型列表数据
                - error: 错误信息(如果失败)
        """
        try:
            # 构建查询参数
            params = {}
            if model_type:
                params['type'] = model_type
            if sub_type:
                params['sub_type'] = sub_type
            
            app_logger.info(f"获取平台模型列表: type={model_type}, sub_type={sub_type}")
            
            # 调用硅基流动API
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self._timeout
            ) as client:
                response = await client.get("/models", params=params)
                
                app_logger.info(f"平台模型列表响应状态码: {response.status_code}")
                
                if not response.is_success:
                    return await self._build_error_response(response)
                
                result = response.json()
                
                return {
                    "success": True,
                    "data": result
                }
                
        except Exception as e:
            app_logger.error(f"获取平台模型列表失败: {str(e)}")
            return {
                "success": False,
                "error": f"获取平台模型列表失败: {str(e)}"
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        获取用户账户信息，包括余额和状态
        
        Returns:
            Dict[str, Any]: 用户账户信息
                - success: 是否成功
                - data: 用户信息数据
                    - id: 用户ID
                    - name: 用户名
                    - email: 邮箱
                    - balance: 可用余额
                    - chargeBalance: 充值余额
                    - totalBalance: 总余额
                    - status: 账户状态
                - error: 错误信息(如果失败)
        """
        try:
            app_logger.info("获取用户账户信息")
            
            # 调用硅基流动API
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self._timeout
            ) as client:
                response = await client.get("/user/info")
                
                app_logger.info(f"用户信息响应状态码: {response.status_code}")
                
                if not response.is_success:
                    return await self._build_error_response(response)
                
                result = response.json()
                
                # 硅基流动返回格式: {"code": 20000, "status": true, "data": {...}}
                if result.get("code") == 20000 and result.get("status"):
                    return {
                        "success": True,
                        "data": result.get("data", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("message", "获取用户信息失败")
                    }
                
        except Exception as e:
            app_logger.error(f"获取用户信息失败: {str(e)}")
            return {
                "success": False,
                "error": f"获取用户信息失败: {str(e)}"
            }
    
    async def generate_image_description(
        self,
        prompt: str,
        model: Optional[str] = None,
        style: str = "realistic",
        n: int = 1
    ) -> Dict[str, Any]:
        """
        生成详细的图像描述（可用于其他图像生成服务）
        
        Args:
            prompt: 基础描述，用户提供的简单图像描述
            model: 使用的模型名称
            style: 图像风格，支持 realistic(写实)、artistic(艺术)、cartoon(卡通)等
            n: 生成数量，需要生成的图像描述数量
            
        Returns:
            Dict[str, Any]: 图像描述生成结果
                - success: 是否成功
                - descriptions: 生成的图像描述列表
                - model: 实际使用的模型名称
                - count: 实际生成的描述数量
                - error: 错误信息(如果失败)
        """
        # 检查是否提供了模型
        if not model:
            return {
                "success": False,
                "error": "未指定模型，请先在模型管理页面配置可用的对话模型"
            }
        # 定义不同风格的提示词模板
        style_prompts = {
            "realistic": "请生成一个超现实、高清、细节丰富的图像描述",
            "artistic": "请生成一个艺术风格、富有创意的图像描述",
            "cartoon": "请生成一个卡通风格、生动有趣的图像描述"
        }
        
        # 构造对话消息
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
        
        # 生成指定数量的图像描述
        descriptions = []
        for i in range(n):
            result = await self.call_ai(messages, model=model, temperature=0.8)
            if result["success"]:
                descriptions.append({
                    "description": result["content"],
                    "style": style
                })
        
        # 处理生成结果
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
    
    async def edit_image(
        self,
        image_base64: str,
        instruction: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        图片编辑功能 - 使用图像编辑模型
        
        Args:
            image_base64: Base64编码的原始图片数据
            instruction: 编辑指令，描述想要对图片进行的修改
            model: 使用的模型名称
            
        Returns:
            Dict[str, Any]: 图片编辑结果
                - success: 是否成功
                - edited_image: 编辑后的图片（base64格式）
                - model: 实际使用的模型名称
                - usage: token使用情况
                - error: 错误信息(如果失败)
        """
        # 检查是否提供了模型
        if not model:
            return {
                "success": False,
                "error": "未指定模型，请先在模型管理页面配置可用的图像编辑模型"
            }
        
        try:
            # 构造图片编辑请求 - 使用 images/generations 接口
            payload = {
                "model": model,
                "prompt": instruction,
                "image": f"data:image/jpeg;base64,{image_base64}",
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "batch_size": 1
            }
            
            app_logger.info(f"开始图片编辑: model={model}, instruction={instruction[:100]}...")
            
            # 发送请求到硅基流动平台
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=httpx.Timeout(120.0)
            ) as client:
                endpoint = "/images/generations"
                response = await client.post(endpoint, json=payload)
                
                app_logger.info(f"图片编辑响应状态码: {response.status_code}")
                
                if not response.is_success:
                    return await self._build_error_response(response)
                
                result = response.json()
                
                # 提取编辑后的图片 URL
                images = result.get("images", [])
                if not images:
                    app_logger.error("图片编辑返回结果中没有图片")
                    return {
                        "success": False,
                        "error": "图片编辑返回结果中没有图片"
                    }
                
                image_url = images[0].get("url", "")
                
                if not image_url:
                    app_logger.error("图片编辑返回的 URL 为空")
                    return {
                        "success": False,
                        "error": "图片编辑返回的 URL 为空"
                    }
                
                app_logger.info(f"图片编辑成功，URL: {image_url}")
                
                # 尝试下载图片并转换为 base64
                # 如果下载失败（403），前端可以直接使用 URL
                edited_image_base64 = None
                try:
                    app_logger.info(f"尝试下载编辑后的图片: {image_url}")
                    # 添加必要的 headers 模拟浏览器请求
                    download_headers = {
                        **self.headers,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Referer": "https://cloud.siliconflow.cn/"
                    }
                    image_response = await client.get(image_url, headers=download_headers, follow_redirects=True)
                    
                    if image_response.is_success:
                        # 将图片转换为 base64
                        edited_image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                        app_logger.info("图片下载并转换为 base64 成功")
                    else:
                        app_logger.warning(f"下载图片失败 ({image_response.status_code})，将返回 URL 供前端使用")
                except Exception as download_error:
                    app_logger.warning(f"下载图片异常: {download_error}，将返回 URL 供前端使用")
                
                return {
                    "success": True,
                    "edited_image": edited_image_base64,  # 可能为 None
                    "image_url": image_url,  # 始终返回 URL
                    "model": model,
                    "seed": result.get("seed"),
                    "timings": result.get("timings", {})
                }
                
        except Exception as e:
            app_logger.error(f"图片编辑失败: {str(e)}")
            return {
                "success": False,
                "error": f"图片编辑失败: {str(e)}"
            }
