"""
IAM API E2E — 共用 fixture。

- 需 PostgreSQL；模組級 `reset_iam_schema_for_recovery` 僅重建 `iam` schema，與其他 context 隔離。
- 提供 `TestClient(main:app)`、種子 system user 之管理用 JWT、以及將申請人標記為 active 之測試輔助函式。
"""

from __future__ import annotations

from uuid import UUID

import pytest

from shared.core.db.connection import get_engine


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("IAM API E2E requires PostgreSQL")


@pytest.fixture(scope="module")
def iam_e2e_db_ready() -> None:
    """模組級：乾淨 iam + seed（含 system user 與 admin 角色指派）。"""
    _require_postgresql()
    from src.contexts.iam.infra.iam_infra_bootstrap import reset_iam_schema_for_recovery

    reset_iam_schema_for_recovery()
    get_engine().dispose()
    yield
    get_engine().dispose()


@pytest.fixture(scope="module")
def e2e_client(iam_e2e_db_ready):
    """真實 FastAPI 應用（含 AuthMiddleware 與 IAM 路由）。"""
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(scope="module")
def iam_seed_system_user_id() -> UUID:
    """與 `iam/infra/seed/data/users.json` 一致之 system user。"""
    return UUID("00000000-0000-4000-8000-000000000001")


@pytest.fixture(scope="module")
def iam_admin_auth_headers(iam_seed_system_user_id: UUID) -> dict[str, str]:
    """具種子 admin 角色之使用者 JWT（sub 為 UUID 字串，供 IAM 路由解析）。"""
    from shared.core.security.jwt.jwt_handler import JWTHandler

    token = JWTHandler().encode(str(iam_seed_system_user_id), roles=["admin"])
    return {"Authorization": f"Bearer {token}"}


def activate_iam_user_status(user_id: UUID, status: str = "active") -> None:
    """測試輔助：更新 iam.users.status（不屬 API 層，僅供 E2E 打通登入成功路徑）。"""
    from shared.core.db.connection import get_session
    from src.contexts.iam.infra.schema.users import Users

    with get_session() as session:
        row = session.get(Users, user_id)
        assert row is not None
        row.status = status


def bind_iam_user_stub_external_identity(user_id: UUID, *, subject: str) -> None:
    """測試輔助：改為僅 stub 外部身分登入（password_hash 清空，external_* 設好）。"""
    from shared.core.db.connection import get_session
    from src.contexts.iam.infra.schema.users import Users

    with get_session() as session:
        row = session.get(Users, user_id)
        assert row is not None
        row.password_hash = None
        row.external_provider = "stub"
        row.external_subject = subject
