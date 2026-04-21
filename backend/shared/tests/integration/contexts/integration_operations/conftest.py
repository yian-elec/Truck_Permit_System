"""
只為本目錄整合測試：確保從 backend 根目錄解析路徑與設定。

不修改其他 context；使用 .env / conftest 既有 DB_*（預設與 shared/tests/conftest 對齊）。
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine
from shared.core.db.init_db import init_db

# 與 shared/tests/conftest 一致：在收集測試前已 insert backend root
# 此檔可再保險設定整合測試專用 DB（若未設則沿用目前環境）
os.environ.setdefault("OPS_INTEGRATION_TEST", "1")


def _require_postgresql() -> None:
    from shared.core.db.connection import get_engine as _ge

    eng = _ge()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Integration_Operations tests require PostgreSQL")


@pytest.fixture
def reset_ops_schema_isolated() -> None:
    """
    隔離環境：DROP SCHEMA ops CASCADE 後重新 init_db()，確保表結構與 seed 可重現。

    僅影響 ops schema，不碰其他 context 之表。
    """
    _require_postgresql()
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS ops CASCADE"))
    eng.dispose()
    assert init_db() is True
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_integration_test():
    """每個測試結束釋放連線池，避免 DDL／交易狀態殘留影響下一測。"""
    yield
    get_engine().dispose()
