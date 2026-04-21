"""
Review_Decision — 僅 **review.* schema** 的 DDL 與 seed 載入。

責任：
- 在 **未安裝 PostGIS** 的環境中，全專案 `init_db()` 會因 `routing.*` 之 geometry 型別而失敗；
  本模組僅對 `review` schema 執行 `CREATE SCHEMA` 與 `create_all`（指定表），不依賴 PostGIS。
- **apply_review_context_seed** 與 `init_db` 對 `review_decision` 之 seed 語意一致：依表順序載入 JSON、
  若表內已有資料則跳過（可重入）。

整合測試應優先使用本模組驗證 Review infra 之自我恢復；完整 `init_db()` 需 PostGIS 時另測。
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from shared.core.db.connection import Base, get_engine, get_session
from shared.utils.seed_loader import load_seed_data

from src.contexts.review_decision.infra.schema import (
    Decisions,
    ReviewComments,
    ReviewTasks,
    SupplementItems,
    SupplementRequests,
)

# create_all 時一併傳入；SQLAlchemy 會依 FK 排序
_REVIEW_TABLES: tuple = (
    ReviewTasks.__table__,
    SupplementRequests.__table__,
    SupplementItems.__table__,
    Decisions.__table__,
    ReviewComments.__table__,
)

_SEED_ORDER: tuple[str, ...] = (
    "review_tasks",
    "supplement_requests",
    "supplement_items",
    "decisions",
    "review_comments",
)

_SCHEMA_BY_TABLE: dict[str, type] = {
    "review_tasks": ReviewTasks,
    "supplement_requests": SupplementRequests,
    "supplement_items": SupplementItems,
    "decisions": Decisions,
    "review_comments": ReviewComments,
}


def ensure_review_schema_and_tables(engine=None) -> None:
    """
    建立 `review` schema（若無）並只建立本 context 之五張表。

    不觸及其他 schema，故無需 PostGIS。
    """
    eng = engine or get_engine()
    with eng.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS review"))
    Base.metadata.create_all(bind=eng, tables=list(_REVIEW_TABLES))


def _table_has_rows(session: Session, model: type) -> bool:
    return session.query(model).count() > 0


def apply_review_context_seed() -> None:
    """
    自 `infra/seed/data/*.json` 載入 seed；表內已有列則跳過（與 init_db 可重入行為一致）。
    """
    seed_dir = str(Path(__file__).resolve().parent / "seed" / "data")

    for table_name in _SEED_ORDER:
        model = _SCHEMA_BY_TABLE[table_name]
        seed_rows = load_seed_data(table_name, seed_dir)
        if not seed_rows:
            continue

        with get_session() as session:
            if _table_has_rows(session, model):
                continue
            objects = []
            for raw in seed_rows:
                row = dict(raw)
                if "id" in row and row["id"] is None:
                    row = {k: v for k, v in row.items() if k != "id"}
                objects.append(model(**row))
            session.add_all(objects)
