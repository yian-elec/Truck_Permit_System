"""
Permit_Document Infra 整合測試 — 共用 fixture。

隔離策略：僅操作 **permit** schema；使用 `permit_infra_bootstrap`（Infra 層）重建表與 seed，
不依賴其他 context 的測試資料（seed JSON 內 application_id 僅為字串，無 DB FK）。
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine

pytestmark = pytest.mark.integration


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("permit_document infra integration tests require PostgreSQL")


@pytest.fixture
def permit_postgres_env() -> None:
    """
    每個測試前：DROP+CREATE `permit` schema、建三表、載入 seed。

    真實 I/O；不使用 mock。
    """
    _require_postgresql()
    from src.contexts.permit_document.infra.permit_infra_bootstrap import (
        rebuild_permit_schema_tables_and_seed,
    )

    rebuild_permit_schema_tables_and_seed()
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_permit_integration() -> None:
    yield
    get_engine().dispose()
