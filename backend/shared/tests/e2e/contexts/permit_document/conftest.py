"""
Permit_Document — API E2E 共用 fixture。

- 僅重建 **permit** schema 與 seed（`permit_infra_bootstrap`），不操作其他 context 之業務路由。
- 真實 `main:app` + `TestClient` + `AuthMiddleware`；JWT 由 **JWTHandler** 產生（不呼叫 User 登入 API）。
- 與 infra seed 對齊之 UUID 常數供斷言與路徑替換。
"""

from __future__ import annotations

from uuid import UUID

import pytest

from shared.core.db.connection import get_engine


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Permit_Document API E2E requires PostgreSQL")


# 與 `src/contexts/permit_document/infra/seed/data/*.json` 一致
SEED_APPLICATION_ID = UUID("11111111-1111-4111-8111-111111111101")
SEED_PERMIT_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01")
SEED_DOCUMENT_ID = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddd01")


@pytest.fixture
def permit_document_e2e_db_ready() -> None:
    """DROP+CREATE **permit** schema、建表並載入 seed；可重現、與他測試分離。"""
    _require_postgresql()
    from src.contexts.permit_document.infra.permit_infra_bootstrap import (
        rebuild_permit_schema_tables_and_seed,
    )

    rebuild_permit_schema_tables_and_seed()
    yield
    get_engine().dispose()


@pytest.fixture
def e2e_client(permit_document_e2e_db_ready):
    """真實 FastAPI `main:app`（含 Permit 路由器與認證中介軟體）。"""
    from fastapi.testclient import TestClient

    from main import app
    from src.contexts.permit_document.infra.permit_infra_bootstrap import (
        rebuild_permit_schema_tables_and_seed,
    )

    with TestClient(app) as client:
        # lifespan 內會跑全庫 init_db；與 permit 專用 seed 的順序／略過邏輯可能不一致，
        # 故在 app 啟動後再重建 permit schema + seed，確保 E2E 斷言與 JSON seed 一致。
        rebuild_permit_schema_tables_and_seed()
        yield client


@pytest.fixture(scope="module")
def applicant_auth_headers() -> dict[str, str]:
    """合法 Bearer JWT（`sub` 為 UUID 字串，與 `get_applicant_user_id` 解析一致）。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    token = JWTHandler().encode(str(UUID("22222222-2222-4222-8222-222222222202")), roles=["user"])
    return {"Authorization": f"Bearer {token}"}
