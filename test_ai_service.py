"""
纯AI服务测试脚本（异步版）
"""

import asyncio
from typing import Dict, Any, List

import httpx

BASE_URL = "http://localhost:8000/api/v1/ai"
DEFAULT_HEADERS = {"Content-Type": "application/json"}


def print_result(title: str, result: Dict[str, Any]) -> None:
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")
    if result.get("success"):
        print(" 成功!")
        payload = result.get("result") or result.get("content")
        if payload:
            snippet = payload[:500]
            suffix = "..." if len(payload) > 500 else ""
            print(f"响应内容: {snippet}{suffix}")
        if result.get("model"):
            print(f"使用模型: {result['model']}")
        if result.get("usage"):
            print(f"Token使用: {result['usage']}")
    else:
        print(f" 失败: {result.get('error', 'Unknown error')}")
        if result.get("details"):
            print(f"详情: {result['details']}")


async def test_list_models(client: httpx.AsyncClient) -> bool:
    print("\n 测试获取可用模型列表...")
    response = await client.get("/models")
    if response.status_code == 200:
        data = response.json()
        print(f" 发现 {len(data['models'])} 个可用模型")
        print(f"默认模型: {data['default_model']}")
        print("\n推荐模型:")
        for use_case, model in data["recommended"].items():
            print(f"  - {use_case}: {model}")
        return True
    else:
        print(f" 获取模型列表失败: {response.status_code}")
        return False


async def test_text_analysis(client: httpx.AsyncClient) -> None:
    test_cases: List[Dict[str, Any]] = [
        {
            "title": "文本总结",
            "data": {
                "text": "人工智能（AI）是计算机科学的一个分支，它致力于创建能够模拟人类智能的系统。AI技术包括机器学习、深度学习、自然语言处理等。近年来，AI在医疗诊断、自动驾驶、语音识别等领域取得了重大突破。大型语言模型如GPT、BERT等展示了强大的文本理解和生成能力。",
                "task": "summarize",
            },
        },
        {
            "title": "情感分析",
            "data": {
                "text": "这个产品真的太棒了！界面设计非常人性化，功能强大且易于使用。客服响应也很及时，解决了我所有的问题。强烈推荐给大家！",
                "task": "sentiment",
            },
        },
        {
            "title": "关键词提取",
            "data": {
                "text": "区块链是一种分布式账本技术，通过密码学方法确保数据的安全性和不可篡改性。比特币是第一个成功应用区块链技术的加密货币。智能合约允许在区块链上执行自动化的协议。",
                "task": "keywords",
            },
        },
    ]

    for case in test_cases:
        response = await client.post("/text/analyze", json=case["data"])
        if response.status_code == 200:
            print_result(f"文本分析 - {case['title']}", response.json())
        else:
            print(f" {case['title']}失败: {response.status_code}")


async def test_code_assist(client: httpx.AsyncClient) -> None:
    test_cases: List[Dict[str, Any]] = [
        {
            "title": "代码生成",
            "data": {
                "task": "generate",
                "language": "Python",
                "requirements": "实现一个二分查找算法",
            },
        },
        {
            "title": "代码审查",
            "data": {
                "code": """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total
                """,
                "task": "review",
                "language": "Python",
            },
        },
        {
            "title": "代码优化",
            "data": {
                "code": """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates
                """,
                "task": "optimize",
                "language": "Python",
            },
        },
    ]

    for case in test_cases:
        response = await client.post("/code", json=case["data"])
        if response.status_code == 200:
            print_result(f"代码辅助 - {case['title']}", response.json())
        else:
            print(f" {case['title']}失败: {response.status_code}")


async def test_chat(client: httpx.AsyncClient) -> None:
    print("\n 测试对话功能...")
    data = {
        "messages": [
            {"role": "user", "content": "什么是量子计算？"},
            {"role": "assistant", "content": "量子计算是一种基于量子力学原理的计算方式。"},
            {"role": "user", "content": "它与传统计算有什么区别？"},
        ],
        "system_prompt": "你是一个专业的科技顾问，用简单易懂的语言解释复杂概念。",
    }

    response = await client.post("/chat", json=data)
    if response.status_code == 200:
        print_result("多轮对话", response.json())
    else:
        print(f" 对话失败: {response.status_code}")


async def test_quick_ai(client: httpx.AsyncClient) -> None:
    print("\n 测试快速AI调用...")
    data = {
        "prompt": "用三句话介绍Python编程语言的特点",
    }

    response = await client.post("/quick", json=data)
    if response.status_code == 200:
        print_result("快速AI调用", response.json())
    else:
        print(f" 快速调用失败: {response.status_code}")


async def test_batch_process(client: httpx.AsyncClient) -> None:
    print("\n 测试批量处理...")
    tasks = [
        {
            "id": "task1",
            "type": "text",
            "text": "机器学习是人工智能的一个重要分支。",
            "task": "translate",
        },
        {
            "id": "task2",
            "type": "code",
            "code": "print('Hello World')",
            "task": "explain",
            "language": "Python",
        },
        {
            "id": "task3",
            "type": "text",
            "text": "今天天气真好，适合出去散步。",
            "task": "sentiment",
        },
    ]

    response = await client.post("/batch", json={"tasks": tasks})
    if response.status_code == 200:
        results = response.json()
        print(f" 批量处理完成，共处理 {len(results['results'])} 个任务")
        for result in results["results"]:
            success = result.get("result", {}).get("success")
            print(f"  - 任务 {result['task_id']}: {'成功' if success else '失败'}")
    else:
        print(f" 批量处理失败: {response.status_code}")


async def test_health_check(client: httpx.AsyncClient) -> bool:
    print("\n 测试健康检查...")
    response = await client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print(f" 服务状态: {data['status']}")
        print(f"服务名称: {data['service']}")
        print(f"模型可用: {data['models_available']}")
        return True
    else:
        print(f" 健康检查失败: {response.status_code}")
        return False


async def main() -> None:
    print(" 开始测试纯AI服务")
    print("=" * 60)
    print(f"服务地址: {BASE_URL}")
    print("=" * 60)

    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(base_url=BASE_URL, headers=DEFAULT_HEADERS, timeout=timeout) as client:
        if not await test_health_check(client):
            print("\n 服务可能未启动，请先启动服务：")
            print("python main.py 或 uvicorn main:app --reload")
            return

        await test_list_models(client)
        await test_text_analysis(client)
        await test_code_assist(client)
        await test_chat(client)
        await test_quick_ai(client)
        await test_batch_process(client)

    print("\n" + "=" * 60)
    print(" 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
