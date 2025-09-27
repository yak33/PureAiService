"""
��AI������Խű����첽�棩
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
        print(" �ɹ�!")
        payload = result.get("result") or result.get("content")
        if payload:
            snippet = payload[:500]
            suffix = "..." if len(payload) > 500 else ""
            print(f"��Ӧ����: {snippet}{suffix}")
        if result.get("model"):
            print(f"ʹ��ģ��: {result['model']}")
        if result.get("usage"):
            print(f"Tokenʹ��: {result['usage']}")
    else:
        print(f" ʧ��: {result.get('error', 'Unknown error')}")
        if result.get("details"):
            print(f"����: {result['details']}")


async def test_list_models(client: httpx.AsyncClient) -> bool:
    print("\n ���Ի�ȡ����ģ���б�...")
    response = await client.get("/models")
    if response.status_code == 200:
        data = response.json()
        print(f" ���� {len(data['models'])} ������ģ��")
        print(f"Ĭ��ģ��: {data['default_model']}")
        print("\n�Ƽ�ģ��:")
        for use_case, model in data["recommended"].items():
            print(f"  - {use_case}: {model}")
        return True
    else:
        print(f" ��ȡģ���б�ʧ��: {response.status_code}")
        return False


async def test_text_analysis(client: httpx.AsyncClient) -> None:
    test_cases: List[Dict[str, Any]] = [
        {
            "title": "�ı��ܽ�",
            "data": {
                "text": "�˹����ܣ�AI���Ǽ������ѧ��һ����֧���������ڴ����ܹ�ģ���������ܵ�ϵͳ��AI������������ѧϰ�����ѧϰ����Ȼ���Դ���ȡ���������AI��ҽ����ϡ��Զ���ʻ������ʶ�������ȡ�����ش�ͻ�ơ���������ģ����GPT��BERT��չʾ��ǿ����ı���������������",
                "task": "summarize",
            },
        },
        {
            "title": "��з���",
            "data": {
                "text": "�����Ʒ���̫���ˣ�������Ʒǳ����Ի�������ǿ��������ʹ�á��ͷ���ӦҲ�ܼ�ʱ������������е����⡣ǿ���Ƽ�����ң�",
                "task": "sentiment",
            },
        },
        {
            "title": "�ؼ�����ȡ",
            "data": {
                "text": "��������һ�ֲַ�ʽ�˱�������ͨ������ѧ����ȷ�����ݵİ�ȫ�ԺͲ��ɴ۸��ԡ����ر��ǵ�һ���ɹ�Ӧ�������������ļ��ܻ��ҡ����ܺ�Լ��������������ִ���Զ�����Э�顣",
                "task": "keywords",
            },
        },
    ]

    for case in test_cases:
        response = await client.post("/text/analyze", json=case["data"])
        if response.status_code == 200:
            print_result(f"�ı����� - {case['title']}", response.json())
        else:
            print(f" {case['title']}ʧ��: {response.status_code}")


async def test_code_assist(client: httpx.AsyncClient) -> None:
    test_cases: List[Dict[str, Any]] = [
        {
            "title": "��������",
            "data": {
                "task": "generate",
                "language": "Python",
                "requirements": "ʵ��һ�����ֲ����㷨",
            },
        },
        {
            "title": "�������",
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
            "title": "�����Ż�",
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
            print_result(f"���븨�� - {case['title']}", response.json())
        else:
            print(f" {case['title']}ʧ��: {response.status_code}")


async def test_chat(client: httpx.AsyncClient) -> None:
    print("\n ���ԶԻ�����...")
    data = {
        "messages": [
            {"role": "user", "content": "ʲô�����Ӽ��㣿"},
            {"role": "assistant", "content": "���Ӽ�����һ�ֻ���������ѧԭ��ļ��㷽ʽ��"},
            {"role": "user", "content": "���봫ͳ������ʲô����"},
        ],
        "system_prompt": "����һ��רҵ�ĿƼ����ʣ��ü��׶������Խ��͸��Ӹ��",
    }

    response = await client.post("/chat", json=data)
    if response.status_code == 200:
        print_result("���ֶԻ�", response.json())
    else:
        print(f" �Ի�ʧ��: {response.status_code}")


async def test_quick_ai(client: httpx.AsyncClient) -> None:
    print("\n ���Կ���AI����...")
    data = {
        "prompt": "�����仰����Python������Ե��ص�",
    }

    response = await client.post("/quick", json=data)
    if response.status_code == 200:
        print_result("����AI����", response.json())
    else:
        print(f" ���ٵ���ʧ��: {response.status_code}")


async def test_batch_process(client: httpx.AsyncClient) -> None:
    print("\n ������������...")
    tasks = [
        {
            "id": "task1",
            "type": "text",
            "text": "����ѧϰ���˹����ܵ�һ����Ҫ��֧��",
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
            "text": "����������ã��ʺϳ�ȥɢ����",
            "task": "sentiment",
        },
    ]

    response = await client.post("/batch", json={"tasks": tasks})
    if response.status_code == 200:
        results = response.json()
        print(f" ����������ɣ������� {len(results['results'])} ������")
        for result in results["results"]:
            success = result.get("result", {}).get("success")
            print(f"  - ���� {result['task_id']}: {'�ɹ�' if success else 'ʧ��'}")
    else:
        print(f" ��������ʧ��: {response.status_code}")


async def test_health_check(client: httpx.AsyncClient) -> bool:
    print("\n ���Խ������...")
    response = await client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print(f" ����״̬: {data['status']}")
        print(f"��������: {data['service']}")
        print(f"ģ�Ϳ���: {data['models_available']}")
        return True
    else:
        print(f" �������ʧ��: {response.status_code}")
        return False


async def main() -> None:
    print(" ��ʼ���Դ�AI����")
    print("=" * 60)
    print(f"�����ַ: {BASE_URL}")
    print("=" * 60)

    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(base_url=BASE_URL, headers=DEFAULT_HEADERS, timeout=timeout) as client:
        if not await test_health_check(client):
            print("\n �������δ������������������")
            print("python main.py �� uvicorn main:app --reload")
            return

        await test_list_models(client)
        await test_text_analysis(client)
        await test_code_assist(client)
        await test_chat(client)
        await test_quick_ai(client)
        await test_batch_process(client)

    print("\n" + "=" * 60)
    print(" ���в�����ɣ�")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
