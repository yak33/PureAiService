#!/usr/bin/env python3
"""
直接测试修改后的call_ai方法
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pure_ai_service import PureAIService
from app.core.logger import app_logger

async def test_call_ai():
    """测试call_ai方法"""
    
    print("开始测试call_ai方法...")
    
    service = PureAIService()
    
    messages = [
        {
            "role": "user",
            "content": "你好，这是一个测试"
        }
    ]
    
    try:
        result = await service.call_ai(messages, model="zai-org/GLM-4.5")
        # 处理编码问题
        if result.get("success"):
            content = result.get("content", "")
            # 移除或替换可能的emoji字符
            safe_content = content.encode('gbk', errors='ignore').decode('gbk')
            print(f"调用成功!")
            print(f"模型: {result.get('model')}")
            print(f"内容: {safe_content}")
            print(f"使用情况: {result.get('usage')}")
        else:
            print(f"调用失败: {result}")
    except Exception as e:
        print(f"调用异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_call_ai())