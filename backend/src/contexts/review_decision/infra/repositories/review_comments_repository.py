"""
ReviewCommentsRepository — review.review_comments 讀寫。

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
from src.contexts.review_decision.infra.schema.review_comments import ReviewComments


class ReviewCommentsRepository:
    """審查評論表存取。"""

    def get_by_id(self, comment_id: UUID) -> ReviewComments | None:
        with get_session() as session:
            row = session.get(ReviewComments, comment_id)
            return detach_optional(session, row)

    def list_by_application_id(self, application_id: UUID) -> List[ReviewComments]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(ReviewComments)
                    .where(ReviewComments.application_id == application_id)
                    .order_by(ReviewComments.created_at)
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: ReviewComments) -> ReviewComments:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
