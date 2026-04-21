"""
run_e2e_test.py - E2E 測試啟動腳本
自動啟動 API 伺服器並執行 E2E 測試
"""

import subprocess
import time
import requests
import sys
import os
from threading import Thread

def check_server_health(base_url: str = "http://localhost:8000", max_retries: int = 30) -> bool:
    """檢查伺服器是否健康"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"等待伺服器啟動... ({i+1}/{max_retries})")
        time.sleep(1)
    
    return False

def start_api_server():
    """啟動 API 伺服器"""
    print("🚀 啟動 API 伺服器...")
    
    # 設定環境變數
    env = os.environ.copy()
    env.update({
        'JWT_SECRET': 'test-secret-key-for-e2e-testing',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'postgres',
        'DB_NAME': 'language_path_test'
    })
    
    try:
        # 啟動伺服器
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待伺服器啟動
        if check_server_health():
            print("✅ API 伺服器啟動成功")
            return process
        else:
            print("❌ API 伺服器啟動失敗")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ 啟動 API 伺服器時發生錯誤: {e}")
        return None

def run_e2e_tests():
    """執行 E2E 測試"""
    print("\n🧪 開始執行 E2E 測試...")
    
    try:
        # 執行 E2E 測試
        result = subprocess.run(
            [sys.executable, "test_user_e2e.py"],
            capture_output=True,
            text=True
        )
        
        # 輸出測試結果
        print(result.stdout)
        if result.stderr:
            print("錯誤輸出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 執行 E2E 測試時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    print("=== User Context E2E 測試啟動腳本 ===")
    print("此腳本會自動啟動 API 伺服器並執行 E2E 測試")
    
    server_process = None
    
    try:
        # 啟動 API 伺服器
        server_process = start_api_server()
        if not server_process:
            print("❌ 無法啟動 API 伺服器，測試終止")
            return False
        
        # 執行 E2E 測試
        test_success = run_e2e_tests()
        
        if test_success:
            print("\n🎉 E2E 測試完成！所有測試通過")
            return True
        else:
            print("\n⚠️  E2E 測試失敗")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  測試被使用者中斷")
        return False
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        return False
        
    finally:
        # 清理：停止伺服器
        if server_process:
            print("\n🛑 停止 API 伺服器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ API 伺服器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  強制終止 API 伺服器")
                server_process.kill()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
