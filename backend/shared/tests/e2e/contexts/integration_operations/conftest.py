"""
Integration_Operations API E2E — 共用 fixture。

- 需 PostgreSQL（與整合測試相同之 DB 設定）。
- `ops_e2e_db_ready`：DROP/重建 `ops` schema 並 `init_db()`，確保 seed 可重現。
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine
from shared.core.db.init_db import init_db


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Ops API E2E requires PostgreSQL")


@pytest.fixture(scope="module")
def ops_e2e_db_ready() -> None:
    """模組級隔離：清空並重建 ops schema，載入 seed。"""
    _require_postgresql()
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS ops CASCADE"))
    eng.dispose()
    assert init_db() is True
    yield
    get_engine().dispose()


@pytest.fixture(scope="module")
def e2e_client(ops_e2e_db_ready):
    """真實 FastAPI 應用（含中介軟體與 Ops 路由）。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def ops_auth_headers() -> dict[str, str]:
    """合法 JWT（不經 User login；僅使用 shared JWT 工具產生）。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    token = JWTHandler().encode("e2e-ops-subject", roles=["user"])
    return {"Authorization": f"Bearer {token}"}
