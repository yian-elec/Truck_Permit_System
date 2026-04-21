"""
iam_infra_bootstrap — 僅建立 `iam` schema、本 context 資料表並載入 seed。

責任：
- 與 `DatabaseInitializer` 對 iam 之 DDL／seed 語意對齊，但不觸及其他 context。
- 供整合測試與「刪除 iam 後自我恢復」；僅使用 `get_engine`／`get_session`。
- 建表與 seed 皆可安全重入（checkfirst、表非空則跳過該表 seed）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Type

from sqlalchemy import func, select, text

from shared.core.db.connection import get_engine, get_session
from shared.utils.seed_loader import load_seed_data

_SEED_DATA_DIR = str(Path(__file__).resolve().parent / "seed" / "data")

# 與 shared/core/db/init_db.py 中 iam 的 seed 順序一致（外鍵依賴）
_IAM_SEED_TABLE_ORDER: tuple[str, ...] = (
    "roles",
    "permissions",
    "role_permissions",
    "users",
    "role_assignments",
    "sessions",
    "mfa_challenges",
)


def _iam_orm_classes_in_create_order() -> List[Type[Any]]:
    from src.contexts.iam.infra.schema import (
        MfaChallenges,
        Permissions,
        RoleAssignments,
        RolePermissions,
        Roles,
        Sessions,
        Users,
    )

    return [
        Roles,
        Permissions,
        RolePermissions,
        Users,
        RoleAssignments,
        Sessions,
        MfaChallenges,
    ]


def _table_name_to_model() -> Dict[str, Type[Any]]:
    return {cls.__tablename__: cls for cls in _iam_orm_classes_in_create_order()}


def ensure_iam_schema_and_tables() -> None:
    """建立 `iam` schema（若無）並以 checkfirst 建立本 context 全部表（可重入）。"""
    engine = get_engine()
    with engine.begin() as conn:
        if conn.dialect.name != "postgresql":
            raise RuntimeError("IAM infra bootstrap requires PostgreSQL")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS iam"))

    for cls in _iam_orm_classes_in_create_order():
        cls.__table__.create(bind=engine, checkfirst=True)


def seed_iam_tables_if_empty() -> Dict[str, int]:
    """
    依固定順序載入 `seed/data/*.json`；該表已有列則跳過（與 init_db 行為一致）。

    Returns:
        各表名稱 -> 本次新增列數（跳過則為 0）。
    """
    ensure_iam_schema_and_tables()
    inserted: Dict[str, int] = {}
    name_to_cls = _table_name_to_model()

    for table_name in _IAM_SEED_TABLE_ORDER:
        cls = name_to_cls[table_name]
        seed_rows = load_seed_data(table_name, _SEED_DATA_DIR)
        if not seed_rows:
            inserted[table_name] = 0
            continue

        with get_session() as session:
            existing = session.scalar(select(func.count()).select_from(cls))
            if (existing or 0) > 0:
                inserted[table_name] = 0
                continue
            for data in seed_rows:
                if "id" in data and data["id"] is None:
                    data = {k: v for k, v in data.items() if k != "id"}
                session.add(cls(**data))
            inserted[table_name] = len(seed_rows)

    return inserted


def drop_iam_schema_cascade() -> None:
    """刪除整個 `iam` schema（僅本 context）。呼叫後建議 `get_engine().dispose()`。"""
    engine = get_engine()
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("DROP SCHEMA IF EXISTS iam CASCADE"))


def reset_iam_schema_for_recovery() -> None:
    """
    刪除 `iam` schema 後重建表並重新載入 seed（模擬災後／刪表後重啟之自我恢復）。

    責任：僅影響 iam；與全專案 init_db 分離，避免依賴 PostGIS 等他 context 前置。
    """
    drop_iam_schema_cascade()
    ensure_iam_schema_and_tables()
    seed_iam_tables_if_empty()
