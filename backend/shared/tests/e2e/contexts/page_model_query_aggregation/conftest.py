"""
Page_Model_Query_Aggregation — API E2E 共用 fixture。

- 不重建資料庫：Page Model 讀取路徑預設僅組 Domain／App 聚合，不依賴本 context 之 ORM seed。
- 真實 `main:app` + `TestClient` + `AuthMiddleware`；JWT 由 **JWTHandler** 產生（不呼叫登入 API）。
"""

from __future__ import annotations

from uuid import UUID

import pytest


@pytest.fixture(scope="module")
def page_model_e2e_client():
    """真實 FastAPI `main:app`（含 Page Model 路由器與認證中介軟體）。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def page_model_auth_headers() -> dict[str, str]:
    """合法 Bearer JWT（`sub` 為 UUID 字串，與申請人／承辦解析一致）。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    token = JWTHandler().encode(str(UUID("22222222-2222-4222-8222-222222222202")), roles=["user"])
    return {"Authorization": f"Bearer {token}"}
