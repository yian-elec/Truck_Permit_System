"""
IAM infra / app 整合測試：需可連線之 PostgreSQL（與專案 .env 相同設定）。

隔離：僅透過 `reset_iam_schema_for_recovery` 重建 `iam` schema，不修改其他 context。
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import UUID

import bcrypt
import pytest

from shared.core.db.connection import get_engine, get_session

os.environ.setdefault("IAM_INFRA_INTEGRATION_TEST", "1")

# 應用層整合測試專用之操作者（具 admin 角色 → iam.assign_roles），與 seed 內 system user 分離。
IAM_APP_OPERATOR_USER_ID = UUID("20000000-0000-4000-8000-000000000011")
IAM_APP_OPERATOR_ASSIGNMENT_ID = UUID("20000000-0000-4000-8000-000000000012")
IAM_APP_OPERATOR_PASSWORD = "AdminPass123!"


def _require_postgresql() -> None:
    try:
        eng = get_engine()
        with eng.connect() as conn:
            if conn.dialect.name != "postgresql":
                pytest.skip("IAM infra integration tests require PostgreSQL")
    except Exception as exc:
        pytest.skip(f"PostgreSQL unavailable for IAM infra tests: {exc}")


@pytest.fixture
def iam_schema_reset_for_test() -> None:
    """每個測試前刪除並重建 iam schema + seed，確保隔離與可重現。"""
    _require_postgresql()
    from src.contexts.iam.infra.iam_infra_bootstrap import reset_iam_schema_for_recovery

    reset_iam_schema_for_recovery()
    get_engine().dispose()
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_iam_integration():
    yield
    get_engine().dispose()


def seed_iam_app_operator_user() -> UUID:
    """
    寫入可密碼登入之 admin 操作者（含 admin 角色指派），供 UC-IAM-04 等用例測試。

    須在 `iam_schema_reset_for_test` 之後呼叫；使用固定 UUID 以確保可重現。
    """
    now = datetime.now(timezone.utc)
    ph = bcrypt.hashpw(IAM_APP_OPERATOR_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
    from src.contexts.iam.infra.schema.users import Users

    with get_session() as session:
        session.add(
            Users(
                user_id=IAM_APP_OPERATOR_USER_ID,
                account_type="admin",
                status="active",
                username="iam_app_test_admin",
                password_hash=ph,
                display_name="IAM App 測試管理員",
                email="iam_app_operator@test.local",
                mobile=None,
                external_provider=None,
                external_subject=None,
                mfa_enabled=True,
                last_login_at=None,
                deleted_at=None,
                created_at=now,
                updated_at=now,
            )
        )
    with get_session() as session:
        session.add(
            RoleAssignments(
                assignment_id=IAM_APP_OPERATOR_ASSIGNMENT_ID,
                user_id=IAM_APP_OPERATOR_USER_ID,
                role_code="admin",
                scope_type=None,
                scope_id=None,
                created_at=now,
                updated_at=now,
            )
        )
    return IAM_APP_OPERATOR_USER_ID


@pytest.fixture
def iam_app_operator(iam_schema_reset_for_test) -> dict:
    """
    在乾淨 iam schema 上建立具 `iam.assign_roles` 之操作者。

    Returns:
        {"user_id": UUID, "password": str}
    """
    seed_iam_app_operator_user()
    get_engine().dispose()
    return {"user_id": IAM_APP_OPERATOR_USER_ID, "password": IAM_APP_OPERATOR_PASSWORD}
