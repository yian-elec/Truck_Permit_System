"""
page_model_infra_bootstrap — 僅建立 `page_model` schema、本 context 資料表並載入 seed。

責任：
- 與 `init_db` 對本表之語意對齊（CREATE SCHEMA、`checkfirst` 建表、表非空則跳過 seed），
  但不依賴全專案 `create_all`（例如 routing 需 PostGIS 時，全專案 init 可能失敗）。
- 供整合測試與災後僅修復本 context 時使用；正式環境仍由 `DatabaseInitializer` 一併建立所有表。

僅使用 `shared.core.db.connection` 之 `get_engine`／`get_session`。
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select, text

from shared.core.db.connection import get_engine, get_session
from shared.utils.seed_loader import load_seed_data

_SEED_DATA_DIR = str(Path(__file__).resolve().parent / "seed" / "data")


def ensure_page_model_schema_and_tables() -> None:
    """
    建立 PostgreSQL schema `page_model`（若尚無），並以 checkfirst 建立 `page_model_snapshots`。

    責任：DDL 可安全重入；不刪除既有資料。
    """
    engine = get_engine()
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS page_model"))

    from src.contexts.page_model_query_aggregation.infra.schema.page_model_snapshots import (
        PageModelSnapshots,
    )

    PageModelSnapshots.__table__.create(bind=engine, checkfirst=True)


def seed_page_model_snapshots_if_empty() -> int:
    """
    若 `page_model_snapshots` 為空，則自 `seed/data/page_model_snapshots.json` 載入 seed。

    Returns:
        新增列數（表已有資料時為 0）。

    責任：與 `init_db` 之「有資料則跳過整表 seed」一致，確保可重入。
    """
    ensure_page_model_schema_and_tables()

    from src.contexts.page_model_query_aggregation.infra.schema.page_model_snapshots import (
        PageModelSnapshots,
    )

    seed_rows = load_seed_data("page_model_snapshots", _SEED_DATA_DIR)
    if not seed_rows:
        return 0

    with get_session() as session:
        existing = session.scalar(select(func.count()).select_from(PageModelSnapshots))
        if (existing or 0) > 0:
            return 0
        for data in seed_rows:
            if "id" in data and data["id"] is None:
                data = {k: v for k, v in data.items() if k != "id"}
            session.add(PageModelSnapshots(**data))
        return len(seed_rows)


def reset_page_model_schema_for_recovery() -> None:
    """
    刪除整個 `page_model` schema 後，重建表並重新載入 seed（自我恢復用）。

    責任：**僅**影響本 context。建議測試或呼叫端在 DDL 後執行 `get_engine().dispose()` 釋放連線池。
    """
    engine = get_engine()
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("DROP SCHEMA IF EXISTS page_model CASCADE"))
    ensure_page_model_schema_and_tables()
    seed_page_model_snapshots_if_empty()
