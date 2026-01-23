# test_unified_api.py
import requests
import json
import time


def test_unified_apis():
    base_url = "http://localhost:8080"

    print("=== 测试统一 API 接口 ===")

    # 测试健康检查
    print("\n1. 测试健康检查:")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试系统状态
    print("\n2. 测试系统状态:")
    try:
        response = requests.get(f"{base_url}/api/system/status")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试预警数据
    print("\n3. 测试预警数据:")
    try:
        response = requests.get(f"{base_url}/api/alert/data")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试提示词
    print("\n4. 测试提示词:")
    try:
        response = requests.get(f"{base_url}/api/alert/prompts")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"提示词数量: {len(data)}")
        for i, prompt in enumerate(data[:2]):  # 只显示前2条
            print(f"提示词 {i + 1}: {prompt['level']} - {prompt['content']}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试时间天气
    print("\n5. 测试时间天气:")
    try:
        response = requests.get(f"{base_url}/api/system/time_weather")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试启动系统
    print("\n6. 测试启动安全系统:")
    try:
        response = requests.post(f"{base_url}/api/system/start")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试预警规则
    print("\n7. 测试预警规则:")
    try:
        response = requests.get(f"{base_url}/api/config/rules")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print("预警规则类别:", list(data.keys()))
    except Exception as e:
        print(f"错误: {e}")

    print("\n=== 统一 API 测试完成 ===")


if __name__ == "__main__":
    test_unified_apis()