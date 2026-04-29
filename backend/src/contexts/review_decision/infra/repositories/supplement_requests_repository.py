"""
SupplementRequestsRepository — review.supplement_requests 與 review.supplement_items 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session。
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import func, select, update

from shared.core.db.connection import get_session

from src.contexts.review_decision.infra.repositories._orm_detach import (
    detach_all,
    detach_optional,
)
from src.contexts.review_decision.infra.schema.supplement_items import SupplementItems
from src.contexts.review_decision.infra.schema.supplement_requests import SupplementRequests


class SupplementRequestsRepository:
    """補件請求與細項表存取。"""

    def get_request_by_id(self, supplement_request_id: UUID) -> SupplementRequests | None:
        with get_session() as session:
            row = session.get(SupplementRequests, supplement_request_id)
            return detach_optional(session, row)

    def list_requests_by_application_id(self, application_id: UUID) -> List[SupplementRequests]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(SupplementRequests).where(
                        SupplementRequests.application_id == application_id
                    )
                ).all()
            )
            return detach_all(session, rows)

    def list_items_for_request(self, supplement_request_id: UUID) -> List[SupplementItems]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(SupplementItems).where(
                        SupplementItems.supplement_request_id == supplement_request_id
                    )
                ).all()
            )
            return detach_all(session, rows)

    def add_request(self, row: SupplementRequests) -> SupplementRequests:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def add_item(self, row: SupplementItems) -> SupplementItems:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def count_open_requests_for_application(self, application_id: UUID) -> int:
        with get_session() as session:
            n = session.scalar(
                select(func.count())
                .select_from(SupplementRequests)
                .where(
                    SupplementRequests.application_id == application_id,
                    SupplementRequests.status == "open",
                )
            )
            return int(n or 0)

    def fulfill_specific_supplement_if_open(
        self,
        application_id: UUID,
        supplement_request_id: UUID,
        *,
        applicant_note: str | None,
        now: datetime,
    ) -> int:
        """
        將指定補件單標記為 fulfilled（須為本案且為 open）。
        回傳更新列數（0 表示 ID 無效或已結案）。
        """
        note_val = (applicant_note or "").strip() or None
        with get_session() as session:
            stmt = (
                update(SupplementRequests)
                .where(
                    SupplementRequests.supplement_request_id == supplement_request_id,
                    SupplementRequests.application_id == application_id,
                    SupplementRequests.status == "open",
                )
                .values(
                    status="fulfilled",
                    updated_at=now,
                    applicant_response_note=note_val,
                    responded_at=now,
                )
            )
            res = session.execute(stmt)
            return int(res.rowcount or 0)
