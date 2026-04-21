"""
Routing_Restriction Infra 整合測試 — 共用 fixture。

與 ops 測試相同：DDL 後釋放 engine pool，避免連線快取影響後續查詢。
"""

from __future__ import annotations

import pytest

from shared.core.db.connection import get_engine

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _dispose_engine_after_ddl():
    yield
    get_engine().dispose()
