"""
Page_Model_Query_Aggregation 整合測試：backend 根目錄、PostgreSQL。

以本 context 之 `page_model_infra_bootstrap` 驗證隔離初始化（不依賴全專案 init_db 之前置如 PostGIS）。
"""

from __future__ import annotations

import os

import pytest

from shared.core.db.connection import get_engine

os.environ.setdefault("PAGE_MODEL_INTEGRATION_TEST", "1")


def _require_postgresql() -> None:
    from shared.core.db.connection import get_engine as _ge

    eng = _ge()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("Page_Model_Query_Aggregation infra tests require PostgreSQL")


@pytest.fixture
def reset_page_model_schema_isolated() -> None:
    """
    隔離：DROP `page_model` schema 後以 infra bootstrap 重建表並 seed。
    """
    _require_postgresql()
    from src.contexts.page_model_query_aggregation.infra.page_model_infra_bootstrap import (
        reset_page_model_schema_for_recovery,
    )

    reset_page_model_schema_for_recovery()
    get_engine().dispose()
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_page_model_integration_test():
    yield
    get_engine().dispose()
