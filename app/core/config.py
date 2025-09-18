import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    # 应用基本配置
    app_name: str = os.getenv("APP_NAME", "Pure AI Service")
    app_version: str = os.getenv("APP_VERSION", "2.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # AI服务配置（硅基流动平台）
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    
    # 默认模型配置
    default_model: str = os.getenv("DEFAULT_MODEL", "zai-org/GLM-4.5")
    default_temperature: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    default_max_tokens: int = int(os.getenv("DEFAULT_MAX_TOKENS", "2000"))
    
    # API超时设置
    api_timeout: int = int(os.getenv("API_TIMEOUT", "60"))
    
    # 文件处理（仅用于临时存储）
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    upload_dir: str = "temp_uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()

# 验证必要的配置
if not settings.openai_api_key:
    import sys
    print("错误: OPENAI_API_KEY 未配置！")
    print("请在 .env 文件中设置您的 API 密钥")
    print("您可以参考 .env.example 文件了解配置格式")
    sys.exit(1)
