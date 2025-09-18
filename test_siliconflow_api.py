#!/usr/bin/env python3
"""
测试硅基流动API调用
用于对比直接调用和程序调用的差异
"""

import requests
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def test_direct_api_call():
    """直接测试API调用"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    print(f"API Key前8位: {api_key[:8]}...")
    print(f"Base URL: {base_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Test-Script/1.0"
    }
    
    payload = {
        "model": "zai-org/GLM-4.5",
        "messages": [
            {
                "role": "user", 
                "content": "你好，请回复一句话测试"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    url = f"{base_url}/chat/completions"
    
    print(f"请求URL: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功! 回复内容: {result['choices'][0]['message']['content']}")
        else:
            print(f"失败! 状态码: {response.status_code}")
            
    except Exception as e:
        print(f"异常: {str(e)}")

if __name__ == "__main__":
    test_direct_api_call()