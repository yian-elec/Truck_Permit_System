"""
conftest.py - 測試配置和共用函數
提供測試環境的統一配置和共用函數
"""

import os
import sys
from typing import Dict, Any

# 專案根目錄（backend/）：conftest 位於 shared/tests/
_backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _backend_root)


def setup_test_environment() -> Dict[str, str]:
    """
    設定測試環境變數

    Returns:
        設定的環境變數字典
    """
    test_env_vars = {
        'JWT_SECRET': 'test-secret-key-for-testing',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'postgres',
        'DB_NAME': 'language_path_test',
        'TEST_API_HOST': 'localhost',
        'TEST_API_PORT': '8000',
        'TEST_USERNAME_PREFIX': 'testuser',
        'TEST_PASSWORD': 'password123',
        'TEST_EMAIL_DOMAIN': 'truckpermitsystem.local'
    }

    for key, value in test_env_vars.items():
        os.environ.setdefault(key, value)

    return test_env_vars


def get_test_user_data(prefix: str = "testuser") -> Dict[str, str]:
    """
    取得測試使用者資料

    Args:
        prefix: 使用者名稱前綴

    Returns:
        測試使用者資料字典
    """
    import time
    timestamp = int(time.time())

    return {
        "username": f"{prefix}{timestamp}",
        "password": os.environ.get('TEST_PASSWORD', 'password123'),
        "email": f"{prefix}{timestamp}@{os.environ.get('TEST_EMAIL_DOMAIN', 'truckpermitsystem.local')}"
    }


def get_test_base_url() -> str:
    """
    取得測試 API 基礎 URL

    Returns:
        測試 API 基礎 URL
    """
    host = os.environ.get('TEST_API_HOST', 'localhost')
    port = os.environ.get('TEST_API_PORT', '8000')
    return f"http://{host}:{port}"


setup_test_environment()
