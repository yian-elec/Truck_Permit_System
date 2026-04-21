"""
PermitsRepository — permit.permits 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session，不自建 engine／session_factory。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.permit_document.infra.repositories._orm_detach import detach_all, detach_optional
from src.contexts.permit_document.infra.schema.permits import Permits


class PermitsRepository:
    """許可證主表存取。"""

    def get_by_id(self, permit_id: UUID) -> Permits | None:
        with get_session() as session:
            row = session.get(Permits, permit_id)
            return detach_optional(session, row)

    def get_by_application_id(self, application_id: UUID) -> Permits | None:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Permits).where(Permits.application_id == application_id).limit(1)
                ).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def get_by_permit_no(self, permit_no: str) -> Permits | None:
        with get_session() as session:
            rows = list(
                session.scalars(select(Permits).where(Permits.permit_no == permit_no).limit(1)).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def list_by_application_id(self, application_id: UUID) -> List[Permits]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(Permits).where(Permits.application_id == application_id)
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: Permits) -> Permits:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def merge_update(self, row: Permits) -> Permits | None:
        """依 permit_id 更新已存在列（欄位覆寫為 row 上之值）。"""
        with get_session() as session:
            existing = session.get(Permits, row.permit_id)
            if existing is None:
                return None
            existing.permit_no = row.permit_no
            existing.application_id = row.application_id
            existing.status = row.status
            existing.approved_start_at = row.approved_start_at
            existing.approved_end_at = row.approved_end_at
            existing.selected_candidate_id = row.selected_candidate_id
            existing.override_id = row.override_id
            existing.route_summary_text = row.route_summary_text
            existing.note = row.note
            existing.issued_at = row.issued_at
            existing.issued_by = row.issued_by
            existing.revoked_at = row.revoked_at
            existing.revoked_by = row.revoked_by
            existing.revoked_reason = row.revoked_reason
            existing.updated_at = row.updated_at
            session.flush()
            session.refresh(existing)
            return detach_optional(session, existing)
