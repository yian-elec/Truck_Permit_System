"""ORM 自 Session 脫離，避免 `get_session()` 結束後 DetachedInstanceError。"""

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
