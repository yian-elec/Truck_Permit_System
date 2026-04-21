"""
Application Infra 整合測試：backend 根路徑、PostgreSQL、init_db 隔離。

僅針對 `application` schema 提供 DROP CASCADE 後重建之 fixture；不修改其他 context 之資料表語意。
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from shared.core.db.connection import get_engine
from shared.core.db.init_db import init_db

os.environ.setdefault("APPLICATION_INTEGRATION_TEST", "1")


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Application infra integration tests require PostgreSQL")


@pytest.fixture
def reset_application_schema_isolated() -> None:
    """
    隔離：DROP SCHEMA application CASCADE 後執行 init_db()，驗證表與 seed 可自癒。

    不刪除 public／ops 等其他 schema（與 integration_operations 測試分區）。
    """
    _require_postgresql()
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS application CASCADE"))
    eng.dispose()
    assert init_db() is True
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_application_integration_test() -> None:
    yield
    get_engine().dispose()
