"""
users_repository — iam.users 存取。

僅使用 `shared.core.db.connection.get_session`，不自建 engine／Session。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.iam.infra.repositories._orm_detach import detach_optional
from src.contexts.iam.infra.schema.users import Users


class UsersRepository:
    """IAM 使用者主表讀寫。"""

    def get_by_user_id(self, user_id: UUID) -> Optional[Users]:
        with get_session() as session:
            row = session.get(Users, user_id)
            return detach_optional(session, row)

    def get_by_username(self, username: str) -> Optional[Users]:
        with get_session() as session:
            rows = list(
                session.scalars(select(Users).where(Users.username == username).limit(1)).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def get_by_email(self, email: str) -> Optional[Users]:
        """Email 比對採小寫正規化（避免大小寫重複註冊）。"""
        em = (email or "").strip().lower()
        if not em:
            return None
        with get_session() as session:
            rows = list(
                session.scalars(select(Users).where(Users.email == em).limit(1)).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def get_by_mobile(self, mobile: str) -> Optional[Users]:
        m = (mobile or "").strip()
        if not m:
            return None
        with get_session() as session:
            rows = list(
                session.scalars(select(Users).where(Users.mobile == m).limit(1)).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def add(self, row: Users) -> Users:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
