"""
DecisionsRepository — review.decisions 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.review_decision.infra.repositories._orm_detach import (
    detach_all,
    detach_optional,
)
from src.contexts.review_decision.infra.schema.decisions import Decisions


class DecisionsRepository:
    """決策紀錄表存取。"""

    def get_by_id(self, decision_id: UUID) -> Decisions | None:
        with get_session() as session:
            row = session.get(Decisions, decision_id)
            return detach_optional(session, row)

    def list_by_application_id(self, application_id: UUID) -> List[Decisions]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Decisions)
                    .where(Decisions.application_id == application_id)
                    .order_by(Decisions.decided_at)
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: Decisions) -> Decisions:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
