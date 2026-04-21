"""
example_api_wrapper_usage.py — API Wrapper 使用範例（不依賴已移除之舊 user context）。

舊版 `/users/*` 已由 IAM（`/api/v1/auth/*`）取代；此檔僅示範 `api_response` 包裝成功／錯誤資料。
"""

from __future__ import annotations

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def example_controller_usage() -> None:
    print("=== API Wrapper 使用範例 ===")
    os.environ.setdefault("JWT_SECRET", "test-secret-key-for-Truck_Permit_System")

    from shared.api.api_wrapper import api_response
    from shared.errors.domain_error.validation_error import ValidationError

    ok, code = api_response({"user_id": "demo", "status": "ok"})
    print("成功:", ok, "HTTP", code)

    err, code2 = api_response(ValidationError("示範驗證失敗"))
    print("錯誤:", err, "HTTP", code2)


if __name__ == "__main__":
    example_controller_usage()
