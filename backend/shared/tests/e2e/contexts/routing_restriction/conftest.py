"""
Routing_Restriction — API E2E 共用 fixture。

- 僅重建 `routing` schema 後執行 `init_db()`，與其他 context 之 E2E 並行時較不易互相覆寫；
  仍須 PostgreSQL + PostGIS（與專案 routing.* 幾何表一致）。
- JWT 透過 `JWTHandler` 產生，不經 User context 登入 API。
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
            pytest.skip("Routing_Restriction API E2E requires PostgreSQL")


def _require_postgis() -> None:
    eng = get_engine()
    try:
        with eng.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    except Exception as exc:
        pytest.skip(f"PostGIS not available: {exc}")


@pytest.fixture(scope="module")
def routing_e2e_app_client():
    """
    僅載入 `main:app` 之 TestClient，**不**重建資料庫。

    適用：OpenAPI／Swagger、AuthMiddleware 攔截、FastAPI 路徑／Body 驗證（未到達會觸發
    PostGIS 之 repository）。
    """
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def routing_e2e_db_ready() -> None:
    """清空 routing schema 並重建表＋ seed，確保本模組測試可重現。"""
    _require_postgresql()
    _require_postgis()
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS routing CASCADE"))
    eng.dispose()
    assert init_db() is True
    yield
    get_engine().dispose()


@pytest.fixture(scope="module")
def e2e_client(routing_e2e_db_ready):
    """真實 FastAPI `main:app`（含 AuthMiddleware 與 Routing 三組路由器）。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def routing_auth_headers() -> dict[str, str]:
    """合法 Bearer JWT；`sub` 為 UUID 字串（與申請人端解析一致，審查／管理端僅需已登入）。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    sub = str(uuid.uuid4())
    token = JWTHandler().encode(sub, roles=["user"])
    return {"Authorization": f"Bearer {token}"}
