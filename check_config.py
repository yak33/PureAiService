#!/usr/bin/env python3
"""
检查程序配置加载情况
"""

import os
from dotenv import load_dotenv
from app.core.config import settings

# 手动加载.env
load_dotenv(override=True)

print("=== 环境变量检查 ===")
print(f"直接从os.getenv获取的API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT_FOUND')[:8]}...")
print(f"直接从os.getenv获取的BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT_FOUND')}")

print("\n=== Settings对象检查 ===")
print(f"settings.openai_api_key: {settings.openai_api_key[:8]}...")
print(f"settings.openai_base_url: {settings.openai_base_url}")

print("\n=== 对比检查 ===")
env_key = os.getenv('OPENAI_API_KEY', '')
settings_key = settings.openai_api_key

if env_key == settings_key:
    print("OK: API Key配置一致")
else:
    print("ERROR: API Key配置不一致!")
    print(f"  环境变量: {env_key[:8]}...")
    print(f"  Settings: {settings_key[:8]}...")

# 测试PureAIService初始化
print("\n=== PureAIService初始化检查 ===")
from app.services.pure_ai_service import PureAIService

service = PureAIService()
print(f"Service API Key: {service.api_key[:8]}...")
print(f"Service Base URL: {service.base_url}")
print(f"Service Headers: {service.headers}")