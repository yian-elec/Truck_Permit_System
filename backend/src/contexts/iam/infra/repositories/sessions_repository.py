"""
sessions_repository — iam.sessions 存取。

僅使用 `shared.core.db.connection.get_session`。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.iam.infra.repositories._orm_detach import detach_optional
from src.contexts.iam.infra.schema.sessions import Sessions


class SessionsRepository:
    """登入工作階段讀寫。"""

    def get_by_session_id(self, session_id: UUID) -> Optional[Sessions]:
        with get_session() as session:
            row = session.get(Sessions, session_id)
            return detach_optional(session, row)

    def get_by_access_jti(self, jti: str) -> Optional[Sessions]:
        with get_session() as session:
            rows = list(
                session.scalars(select(Sessions).where(Sessions.access_token_jti == jti).limit(1)).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def add(self, row: Sessions) -> Sessions:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
