#!/usr/bin/env python3
"""
綜合測試報告
整合 E2E 測試和 Swagger 測試結果
"""

import requests
import json
import time
from datetime import datetime

def print_header(title):
    """打印標題"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """打印章節標題"""
    print(f"\n🔹 {title}")
    print("-" * 40)

def test_api_endpoints():
    """測試所有 API 端點"""
    print_section("API 端點功能測試")
    
    base_url = "http://localhost:8000"
    results = {}
    
    # 1. 健康檢查
    try:
        response = requests.get(f"{base_url}/health")
        results["健康檢查"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        results["健康檢查"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 2. 根路徑
    try:
        response = requests.get(f"{base_url}/")
        results["根路徑"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        results["根路徑"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 3. 用戶註冊
    try:
        timestamp = int(time.time())
        register_data = {
            "username": f"comptest{timestamp}",
            "password": "password123",
            "email": f"comptest{timestamp}@truckpermitsystem.local"
        }
        response = requests.post(f"{base_url}/users/register", json=register_data)
        results["用戶註冊"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "user_id": response.json()["data"]["id"] if response.status_code == 200 else None
        }
    except Exception as e:
        results["用戶註冊"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 4. 用戶登入
    try:
        login_data = {
            "username": f"comptest{timestamp}",
            "password": "password123"
        }
        response = requests.post(f"{base_url}/users/login", json=login_data)
        results["用戶登入"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "has_token": "access_token" in response.json()["data"] if response.status_code == 200 else False
        }
    except Exception as e:
        results["用戶登入"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 5. 查詢用戶
    try:
        user_id = results["用戶註冊"].get("user_id", 1)
        response = requests.get(f"{base_url}/users/{user_id}")
        results["查詢用戶"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        results["查詢用戶"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 打印結果
    for endpoint, result in results.items():
        print(f"  {endpoint}: {result['status']}")
        if "status_code" in result:
            print(f"    狀態碼: {result['status_code']}")
        if "response_time" in result:
            print(f"    回應時間: {result['response_time']:.3f}s")
        if "error" in result:
            print(f"    錯誤: {result['error']}")
    
    return results

def test_swagger_documentation():
    """測試 Swagger 文檔"""
    print_section("Swagger 文檔測試")
    
    base_url = "http://localhost:8000"
    results = {}
    
    # 1. Swagger UI
    try:
        response = requests.get(f"{base_url}/docs")
        results["Swagger UI"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "has_swagger_ui": "swagger-ui" in response.text
        }
    except Exception as e:
        results["Swagger UI"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 2. OpenAPI JSON
    try:
        response = requests.get(f"{base_url}/openapi.json")
        openapi_data = response.json()
        results["OpenAPI JSON"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code,
            "openapi_version": openapi_data.get("openapi"),
            "api_title": openapi_data.get("info", {}).get("title"),
            "endpoint_count": len(openapi_data.get("paths", {}))
        }
    except Exception as e:
        results["OpenAPI JSON"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 3. ReDoc
    try:
        response = requests.get(f"{base_url}/redoc")
        results["ReDoc"] = {
            "status": "✅ 通過" if response.status_code == 200 else "❌ 失敗",
            "status_code": response.status_code
        }
    except Exception as e:
        results["ReDoc"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 打印結果
    for doc_type, result in results.items():
        print(f"  {doc_type}: {result['status']}")
        if "status_code" in result:
            print(f"    狀態碼: {result['status_code']}")
        if "openapi_version" in result:
            print(f"    OpenAPI 版本: {result['openapi_version']}")
        if "api_title" in result:
            print(f"    API 標題: {result['api_title']}")
        if "endpoint_count" in result:
            print(f"    端點數量: {result['endpoint_count']}")
        if "error" in result:
            print(f"    錯誤: {result['error']}")
    
    return results

def test_error_handling():
    """測試錯誤處理"""
    print_section("錯誤處理測試")
    
    base_url = "http://localhost:8000"
    results = {}
    
    # 1. 查詢不存在的用戶
    try:
        response = requests.get(f"{base_url}/users/99999")
        results["查詢不存在用戶"] = {
            "status": "✅ 通過" if response.status_code == 404 else "❌ 失敗",
            "status_code": response.status_code,
            "has_error_format": "error" in response.json()
        }
    except Exception as e:
        results["查詢不存在用戶"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 2. 重複註冊
    try:
        duplicate_data = {
            "username": "testuser",
            "password": "password123",
            "email": "testuser@truckpermitsystem.local"
        }
        # 先註冊一次
        requests.post(f"{base_url}/users/register", json=duplicate_data)
        # 再註冊一次（應該失敗）
        response = requests.post(f"{base_url}/users/register", json=duplicate_data)
        results["重複註冊"] = {
            "status": "✅ 通過" if response.status_code == 409 else "❌ 失敗",
            "status_code": response.status_code,
            "has_error_format": "error" in response.json()
        }
    except Exception as e:
        results["重複註冊"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 3. 錯誤密碼登入
    try:
        wrong_login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = requests.post(f"{base_url}/users/login", json=wrong_login_data)
        results["錯誤密碼登入"] = {
            "status": "✅ 通過" if response.status_code == 401 else "❌ 失敗",
            "status_code": response.status_code,
            "has_error_format": "error" in response.json()
        }
    except Exception as e:
        results["錯誤密碼登入"] = {"status": "❌ 錯誤", "error": str(e)}
    
    # 打印結果
    for test_name, result in results.items():
        print(f"  {test_name}: {result['status']}")
        if "status_code" in result:
            print(f"    狀態碼: {result['status_code']}")
        if "has_error_format" in result:
            print(f"    錯誤格式正確: {'✅' if result['has_error_format'] else '❌'}")
        if "error" in result:
            print(f"    錯誤: {result['error']}")
    
    return results

def generate_summary(api_results, swagger_results, error_results):
    """生成測試總結"""
    print_header("測試總結")
    
    # 統計通過率
    total_tests = len(api_results) + len(swagger_results) + len(error_results)
    passed_tests = 0
    
    for results in [api_results, swagger_results, error_results]:
        for result in results.values():
            if result["status"] == "✅ 通過":
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 測試統計:")
    print(f"  總測試數: {total_tests}")
    print(f"  通過數: {passed_tests}")
    print(f"  失敗數: {total_tests - passed_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    
    print(f"\n🎯 功能驗證:")
    print(f"  ✅ API 端點功能: {'正常' if all(r['status'] == '✅ 通過' for r in api_results.values()) else '異常'}")
    print(f"  ✅ Swagger 文檔: {'正常' if all(r['status'] == '✅ 通過' for r in swagger_results.values()) else '異常'}")
    print(f"  ✅ 錯誤處理: {'正常' if all(r['status'] == '✅ 通過' for r in error_results.values()) else '異常'}")
    
    print(f"\n📖 文檔連結:")
    print(f"  - Swagger UI: http://localhost:8000/docs")
    print(f"  - ReDoc: http://localhost:8000/redoc")
    print(f"  - OpenAPI JSON: http://localhost:8000/openapi.json")
    
    if success_rate == 100:
        print(f"\n🎉 恭喜！所有測試都通過了！")
        print(f"   API 和 Swagger 文檔完美整合！")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 個測試失敗，請檢查相關功能。")

def main():
    """主函數"""
    print_header("Truck_Permit_System API 綜合測試報告")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行測試
    api_results = test_api_endpoints()
    swagger_results = test_swagger_documentation()
    error_results = test_error_handling()
    
    # 生成總結
    generate_summary(api_results, swagger_results, error_results)

if __name__ == "__main__":
    main()
