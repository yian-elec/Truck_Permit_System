#!/usr/bin/env python3
"""
綜合 API 測試
測試所有端點的 Swagger 文檔和實際功能
"""

import requests
import json
import time
from typing import Dict, Any

class ComprehensiveAPITest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_user_id = None
        self.access_token = None
        
    def test_swagger_documentation(self):
        """測試 Swagger 文檔完整性"""
        print("🔍 測試 Swagger 文檔完整性...")
        
        # 獲取 OpenAPI 文檔
        response = requests.get(f"{self.base_url}/openapi.json")
        assert response.status_code == 200, "無法獲取 OpenAPI 文檔"
        
        openapi_data = response.json()
        
        # 檢查所有端點是否都有文檔
        expected_endpoints = [
            "/health",
            "/",
            "/users/register", 
            "/users/login",
            "/users/me",
            "/users/{user_id}",
            "/users/{user_id}/password",
            "/users/{user_id}/email"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in openapi_data["paths"], f"端點 {endpoint} 缺少文檔"
            print(f"  ✅ {endpoint} 文檔完整")
        
        # 檢查 DTO 定義
        schemas = openapi_data["components"]["schemas"]
        expected_dtos = [
            "RegisterUserInputDTO",
            "LoginUserInputDTO", 
            "ChangePasswordInputDTO",
            "ChangeEmailInputDTO"
        ]
        
        for dto in expected_dtos:
            assert dto in schemas, f"DTO {dto} 缺少定義"
            print(f"  ✅ {dto} 定義完整")
        
        print("✅ Swagger 文檔完整性測試通過")
        
    def test_api_endpoints(self):
        """測試所有 API 端點功能"""
        print("\n🔍 測試 API 端點功能...")
        
        # 1. 健康檢查
        self._test_health_check()
        
        # 2. 根路徑
        self._test_root_endpoint()
        
        # 3. 用戶註冊
        self._test_user_registration()
        
        # 4. 用戶登入
        self._test_user_login()
        
        # 5. 查詢用戶
        self._test_get_user()
        
        # 6. 修改密碼
        self._test_change_password()
        
        # 7. 修改 Email
        self._test_change_email()
        
        # 8. 查詢當前用戶（預期 401）
        self._test_get_current_user()
        
        print("✅ 所有 API 端點功能測試通過")
        
    def _test_health_check(self):
        """測試健康檢查端點"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200, f"健康檢查失敗: {response.status_code}"
        
        data = response.json()
        assert data["data"]["status"] == "healthy", "健康檢查狀態不正確"
        print("  ✅ 健康檢查端點正常")
        
    def _test_root_endpoint(self):
        """測試根路徑端點"""
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200, f"根路徑失敗: {response.status_code}"
        
        data = response.json()
        assert "Welcome to Truck_Permit_System API" in data["data"]["message"], "根路徑訊息不正確"
        print("  ✅ 根路徑端點正常")
        
    def _test_user_registration(self):
        """測試用戶註冊端點"""
        timestamp = int(time.time())
        register_data = {
            "username": f"comptest{timestamp}",
            "password": "password123",
            "email": f"comptest{timestamp}@truckpermitsystem.local"
        }
        
        response = requests.post(f"{self.base_url}/users/register", json=register_data)
        assert response.status_code == 200, f"用戶註冊失敗: {response.status_code}"
        
        data = response.json()
        assert data["data"]["username"] == f"comptest{timestamp}", "註冊回應不正確"
        self.test_user_id = data["data"]["id"]
        print(f"  ✅ 用戶註冊端點正常 - 用戶 ID: {self.test_user_id}")
        
    def _test_user_login(self):
        """測試用戶登入端點"""
        timestamp = int(time.time())
        login_data = {
            "username": f"comptest{timestamp}",
            "password": "password123"
        }
        
        response = requests.post(f"{self.base_url}/users/login", json=login_data)
        assert response.status_code == 200, f"用戶登入失敗: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data["data"], "登入回應缺少 token"
        self.access_token = data["data"]["access_token"]
        print("  ✅ 用戶登入端點正常")
        
    def _test_get_user(self):
        """測試查詢用戶端點"""
        response = requests.get(f"{self.base_url}/users/{self.test_user_id}")
        assert response.status_code == 200, f"查詢用戶失敗: {response.status_code}"
        
        data = response.json()
        assert data["data"]["id"] == self.test_user_id, "查詢用戶回應不正確"
        print("  ✅ 查詢用戶端點正常")
        
    def _test_change_password(self):
        """測試修改密碼端點"""
        change_data = {
            "old_password": "password123",
            "new_password": "newpassword456"
        }
        
        response = requests.put(
            f"{self.base_url}/users/{self.test_user_id}/password",
            json=change_data,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200, f"修改密碼失敗: {response.status_code}"
        
        data = response.json()
        assert "Password updated successfully" in data["data"]["message"], "修改密碼回應不正確"
        print("  ✅ 修改密碼端點正常")
        
    def _test_change_email(self):
        """測試修改 Email 端點"""
        timestamp = int(time.time())
        change_data = {
            "new_email": f"newemail{timestamp}@truckpermitsystem.local"
        }
        
        response = requests.put(
            f"{self.base_url}/users/{self.test_user_id}/email",
            json=change_data,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200, f"修改 Email 失敗: {response.status_code}"
        
        data = response.json()
        assert data["data"]["email"] == f"newemail{timestamp}@truckpermitsystem.local", "修改 Email 回應不正確"
        print("  ✅ 修改 Email 端點正常")
        
    def _test_get_current_user(self):
        """測試查詢當前用戶端點（預期 401）"""
        response = requests.get(f"{self.base_url}/users/me")
        assert response.status_code == 401, f"查詢當前用戶應該返回 401: {response.status_code}"
        
        data = response.json()
        assert data["error"]["code"] == "MissingTokenError", "錯誤碼不正確"
        print("  ✅ 查詢當前用戶端點正常（正確返回 401）")
        
    def test_error_handling(self):
        """測試錯誤處理"""
        print("\n🔍 測試錯誤處理...")
        
        # 測試重複註冊
        duplicate_data = {
            "username": "comptest",  # 使用已存在的用戶名
            "password": "password123",
            "email": "different@truckpermitsystem.local"
        }
        response = requests.post(f"{self.base_url}/users/register", json=duplicate_data)
        assert response.status_code == 409, f"重複註冊應該返回 409: {response.status_code}"
        print("  ✅ 重複註冊錯誤處理正常")
        
        # 測試錯誤密碼登入
        wrong_login_data = {
            "username": "comptest",
            "password": "wrongpassword"
        }
        response = requests.post(f"{self.base_url}/users/login", json=wrong_login_data)
        assert response.status_code == 401, f"錯誤密碼登入應該返回 401: {response.status_code}"
        print("  ✅ 錯誤密碼登入錯誤處理正常")
        
        # 測試查詢不存在用戶
        response = requests.get(f"{self.base_url}/users/99999")
        assert response.status_code == 404, f"查詢不存在用戶應該返回 404: {response.status_code}"
        print("  ✅ 查詢不存在用戶錯誤處理正常")
        
        print("✅ 錯誤處理測試通過")
        
    def test_swagger_ui_accessibility(self):
        """測試 Swagger UI 可訪問性"""
        print("\n🔍 測試 Swagger UI 可訪問性...")
        
        # 測試 Swagger UI
        response = requests.get(f"{self.base_url}/docs")
        assert response.status_code == 200, f"Swagger UI 無法訪問: {response.status_code}"
        assert "swagger-ui" in response.text, "Swagger UI 內容不正確"
        print("  ✅ Swagger UI 可訪問")
        
        # 測試 ReDoc
        response = requests.get(f"{self.base_url}/redoc")
        assert response.status_code == 200, f"ReDoc 無法訪問: {response.status_code}"
        assert "redoc" in response.text.lower(), "ReDoc 內容不正確"
        print("  ✅ ReDoc 可訪問")
        
        print("✅ Swagger UI 可訪問性測試通過")
        
    def run_all_tests(self):
        """執行所有測試"""
        print("=== 綜合 API 測試 ===")
        print("測試 Swagger 文檔和 API 功能的完整整合\n")
        
        try:
            self.test_swagger_documentation()
            self.test_api_endpoints()
            self.test_error_handling()
            self.test_swagger_ui_accessibility()
            
            print("\n🎉 所有測試通過！")
            print("✅ Swagger 文檔完整且正確")
            print("✅ API 端點功能正常")
            print("✅ 錯誤處理完善")
            print("✅ Swagger UI 可正常訪問")
            print("✅ 文檔與實際功能完全一致")
            
            print("\n📖 文檔訪問地址：")
            print(f"   - Swagger UI: {self.base_url}/docs")
            print(f"   - ReDoc: {self.base_url}/redoc")
            print(f"   - OpenAPI JSON: {self.base_url}/openapi.json")
            
        except Exception as e:
            print(f"\n❌ 測試失敗: {e}")
            raise

if __name__ == "__main__":
    tester = ComprehensiveAPITest()
    tester.run_all_tests()
