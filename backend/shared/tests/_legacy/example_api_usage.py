"""
example_api_usage.py - API 使用範例
展示如何使用 Truck_Permit_System API
"""

import requests
import json
import time

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """測試所有 API 端點"""
    print("=== Truck_Permit_System API 使用範例 ===")
    print(f"API 基礎 URL: {BASE_URL}")
    
    try:
        # 1. 健康檢查
        print("\n1. 健康檢查...")
        response = requests.get(f"{BASE_URL}/health")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        # 2. 註冊使用者
        print("\n2. 註冊使用者...")
        timestamp = int(time.time())
        register_data = {
            "username": f"tps_demo{timestamp}",
            "password": "password123",
            "email": f"tps_demo{timestamp}@truckpermitsystem.local"
        }
        
        response = requests.post(f"{BASE_URL}/users/register", json=register_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            user_data = response.json()["data"]
            user_id = user_data["id"]
            print(f"✅ 使用者註冊成功，ID: {user_id}")
        else:
            print("❌ 使用者註冊失敗")
            return
        
        # 3. 登入使用者
        print("\n3. 登入使用者...")
        login_data = {
            "username": f"tps_demo{timestamp}",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            login_data = response.json()["data"]
            access_token = login_data["access_token"]
            print(f"✅ 使用者登入成功，Token: {access_token[:20]}...")
        else:
            print("❌ 使用者登入失敗")
            return
        
        # 4. 查詢使用者資訊
        print("\n4. 查詢使用者資訊...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 查詢使用者資訊成功")
        else:
            print("❌ 查詢使用者資訊失敗")
        
        # 5. 修改密碼
        print("\n5. 修改密碼...")
        change_password_data = {
            "old_password": "password123",
            "new_password": "newpassword456"
        }
        
        response = requests.put(f"{BASE_URL}/users/{user_id}/password", json=change_password_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 密碼修改成功")
        else:
            print("❌ 密碼修改失敗")
        
        # 6. 用新密碼登入
        print("\n6. 用新密碼登入...")
        new_login_data = {
            "username": f"tps_demo{timestamp}",
            "password": "newpassword456"
        }
        
        response = requests.post(f"{BASE_URL}/users/login", json=new_login_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 新密碼登入成功")
        else:
            print("❌ 新密碼登入失敗")
        
        # 7. 修改 Email
        print("\n7. 修改 Email...")
        change_email_data = {
            "new_email": f"newemail{timestamp}@truckpermitsystem.local"
        }
        
        response = requests.put(f"{BASE_URL}/users/{user_id}/email", json=change_email_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Email 修改成功")
        else:
            print("❌ Email 修改失敗")
        
        # 8. 測試錯誤案例
        print("\n8. 測試錯誤案例...")
        
        # 重複註冊
        print("\n8.1 重複註冊...")
        duplicate_register_data = {
            "username": f"tps_demo{timestamp}",
            "password": "password123",
            "email": "different@truckpermitsystem.local"
        }
        
        response = requests.post(f"{BASE_URL}/users/register", json=duplicate_register_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 409:
            print("✅ 重複註冊錯誤處理正確")
        else:
            print("❌ 重複註冊錯誤處理失敗")
        
        # 錯誤密碼登入
        print("\n8.2 錯誤密碼登入...")
        wrong_login_data = {
            "username": f"tps_demo{timestamp}",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/users/login", json=wrong_login_data)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 401:
            print("✅ 錯誤密碼登入錯誤處理正確")
        else:
            print("❌ 錯誤密碼登入錯誤處理失敗")
        
        # 查詢不存在使用者
        print("\n8.3 查詢不存在使用者...")
        response = requests.get(f"{BASE_URL}/users/99999")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
        
        if response.status_code == 404:
            print("✅ 查詢不存在使用者錯誤處理正確")
        else:
            print("❌ 查詢不存在使用者錯誤處理失敗")
        
        print("\n=== API 使用範例完成 ===")
        print("🎉 所有 API 端點測試完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 API 伺服器")
        print("請確保 API 伺服器正在運行：python main.py")
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")


def show_api_documentation():
    """顯示 API 文件資訊"""
    print("\n=== API 文件資訊 ===")
    print("📖 Swagger UI: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("❤️  健康檢查: http://localhost:8000/health")
    print("\n📋 可用的 API 端點：")
    print("POST /users/register - 註冊使用者")
    print("POST /users/login - 登入使用者")
    print("GET /users/{id} - 查詢使用者資訊")
    print("PUT /users/{id}/password - 修改密碼")
    print("PUT /users/{id}/email - 修改 Email")
    print("GET /users/me - 查詢當前登入者")


if __name__ == "__main__":
    print("Truck_Permit_System API 使用範例")
    print("請確保 API 伺服器正在運行：python main.py")
    
    # 顯示 API 文件資訊
    show_api_documentation()
    
    # 測試 API 端點
    test_api_endpoints()
