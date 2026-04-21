"""
Review_Decision 整合測試 — 共用 fixture。

隔離策略（**無需 PostGIS／完整 init_db**）：
- 僅建立 **application.***、**ops.stored_files**、**review.*** 之 DDL，與審查 App 真實呼叫所需之前置一致。
- 每測試 **DROP application schema 後重建**，確保申請案件資料可重現；**TRUNCATE review.*** 清空審查列。
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from shared.core.db.connection import Base, get_engine

pytestmark = pytest.mark.integration

os.environ.setdefault("APPLICATION_INTEGRATION_TEST", "1")


def _require_postgresql() -> None:
    eng = get_engine()
    with eng.connect() as conn:
        if conn.dialect.name != "postgresql":
            pytest.skip("review_decision integration tests require PostgreSQL")


def _bootstrap_application_ops_and_review_tables() -> None:
    """建立本測試套件所需之最小 DDL（不含 routing.* geometry）。"""
    import src.contexts.application.infra.schema  # noqa: F401 — 註冊 metadata

    from src.contexts.review_decision.infra.review_context_db_init import (
        ensure_review_schema_and_tables,
    )

    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS application CASCADE"))
    with eng.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS application"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ops"))

    app_and_ops_tables = [
        t
        for t in Base.metadata.sorted_tables
        if t.schema == "application"
        or (t.schema == "ops" and t.name == "stored_files")
    ]
    Base.metadata.create_all(bind=eng, tables=app_and_ops_tables)
    ensure_review_schema_and_tables(engine=eng)


def _truncate_review_tables() -> None:
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    review.review_comments,
                    review.decisions,
                    review.supplement_items,
                    review.supplement_requests,
                    review.review_tasks
                RESTART IDENTITY CASCADE
                """
            )
        )


@pytest.fixture
def review_app_integration_env() -> None:
    """
    可重現之乾淨環境：application 重建 + review 表清空。

    不依賴 `init_db()`，避免無 PostGIS 時 routing.geometry 導致初始化失敗。
    """
    _require_postgresql()
    _bootstrap_application_ops_and_review_tables()
    _truncate_review_tables()
    yield
    get_engine().dispose()


@pytest.fixture(autouse=True)
def _dispose_engine_after_review_integration_test() -> None:
    yield
    get_engine().dispose()
