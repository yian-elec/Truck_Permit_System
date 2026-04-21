"""
Application context — API E2E 共用 fixture。

- 需 PostgreSQL（與 Ops／整合測試相同之連線設定）。
- 模組級重建 `application` 與 `ops` schema 後執行 `init_db()`，確保 seed 與外鍵一致、可重現。
- JWT 僅透過 `JWTHandler` 產生，不呼叫 User context 登入 API。
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine
from shared.core.db.init_db import init_db


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Application API E2E requires PostgreSQL")


@pytest.fixture(scope="module")
def application_e2e_db_ready() -> None:
    """清空 application／ops schema 並重建，載入含 Application 在內之 seed。"""
    _require_postgresql()
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS application CASCADE"))
        conn.execute(text("DROP SCHEMA IF EXISTS ops CASCADE"))
    eng.dispose()
    assert init_db() is True
    yield
    get_engine().dispose()


@pytest.fixture(scope="module")
def e2e_client(application_e2e_db_ready):
    """真實 FastAPI `main:app`（含 AuthMiddleware、Application 路由器）。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def applicant_auth_headers() -> dict[str, str]:
    """合法 Bearer JWT；`sub` 為穩定測試用 UUID 字串。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    sub = str(uuid.uuid4())
    token = JWTHandler().encode(sub, roles=["user"])
    return {"Authorization": f"Bearer {token}"}