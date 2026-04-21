"""
permit schema 之建立、刪除與 seed 載入（Infra 層）。

責任：
- 供整合測試或維運腳本 **僅針對 permit.*** 做 DDL 重置與 seed，不依賴完整 `init_db()`。
- 所有 DB 存取透過 `get_engine()` / `get_session()`（shared.core.db），不自建連線。
- seed 邏輯與全專案 `init_db._import_seed_data_from_directory` 對 **permit_document** 之語意一致：
  表內已有資料則 **跳過**（可重入）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from sqlalchemy import func, select, text

from shared.core.db.connection import Base, get_engine, get_session
from shared.utils.seed_loader import load_seed_data

PERMIT_SEED_TABLE_ORDER = ("permits", "documents", "document_jobs")


def drop_and_recreate_permit_schema(engine=None) -> None:
    """
    刪除並重建 PostgreSQL schema `permit`（僅 permit.*，不影響其他 schema）。

    責任：模擬「表刪除後」之乾淨 slate；後續須呼叫 `create_permit_tables`。
    """
    eng = engine or get_engine()
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS permit CASCADE"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS permit"))


def create_permit_tables(engine=None) -> None:
    """
    建立 permit.permits、permit.documents、permit.document_jobs（若尚未存在）。

    責任：僅註冊本 context 之 ORM 表並 `create_all(tables=...)`，不跑其他 context。
    """
    import src.contexts.permit_document.infra.schema  # noqa: F401 — 註冊 metadata

    from src.contexts.permit_document.infra.schema import (
        CertificateAccessLogs,
        DocumentJobs,
        Documents,
        Permits,
    )

    eng = engine or get_engine()
    Base.metadata.create_all(
        bind=eng,
        tables=[
            Permits.__table__,
            Documents.__table__,
            DocumentJobs.__table__,
            CertificateAccessLogs.__table__,
        ],
    )


def import_permit_seed_if_empty() -> Dict[str, int]:
    """
    依序載入 `infra/seed/data/{permits,documents,document_jobs}.json`；
    若該表已有列則跳過（**可重入**）。

    Returns:
        各表名稱 -> 本次新增筆數（跳過則為 0）。
    """
    from src.contexts.permit_document.infra.schema import DocumentJobs, Documents, Permits

    model_by_name = {
        "permits": Permits,
        "documents": Documents,
        "document_jobs": DocumentJobs,
    }
    seed_dir = str(Path(__file__).resolve().parent / "seed" / "data")
    inserted: Dict[str, int] = {}

    for name in PERMIT_SEED_TABLE_ORDER:
        model = model_by_name[name]
        seed_rows = load_seed_data(name, seed_dir)
        if not seed_rows:
            inserted[name] = 0
            continue

        with get_session() as session:
            existing = session.scalar(select(func.count()).select_from(model))
            if existing and existing > 0:
                inserted[name] = 0
                continue
            session.add_all([model(**row) for row in seed_rows])
        inserted[name] = len(seed_rows)

    return inserted


def rebuild_permit_schema_tables_and_seed(engine=None) -> Dict[str, int]:
    """
    一鍵：DROP+CREATE schema、建表、載入 seed（用於自我恢復驗證）。

    責任：組合 `drop_and_recreate_permit_schema` → `create_permit_tables` → `import_permit_seed_if_empty`。
    """
    eng = engine or get_engine()
    drop_and_recreate_permit_schema(eng)
    create_permit_tables(eng)
    return import_permit_seed_if_empty()
