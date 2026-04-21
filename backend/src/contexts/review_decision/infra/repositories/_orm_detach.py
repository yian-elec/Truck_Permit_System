"""
ORM 實例自 Session 脫離，供 repository 在 `with get_session()` 結束後仍可讀取已載入屬性。

責任：避免 DetachedInstanceError（session 關閉後延遲載入失效）；不引入業務邏輯。
"""

from __future__ import annotations

from typing import List, Optional, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


def detach_optional(session: Session, row: Optional[T]) -> Optional[T]:
    if row is not None:
        session.expunge(row)
    return row


def detach_all(session: Session, rows: List[T]) -> List[T]:
    for r in rows:
        session.expunge(r)
    return rows
