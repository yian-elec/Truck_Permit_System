"""
DocumentJobsRepository — permit.document_jobs 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.permit_document.infra.repositories._orm_detach import detach_all, detach_optional
from src.contexts.permit_document.infra.schema.document_jobs import DocumentJobs


class DocumentJobsRepository:
    """文件產製工作單存取。"""

    def get_by_id(self, job_id: UUID) -> DocumentJobs | None:
        with get_session() as session:
            row = session.get(DocumentJobs, job_id)
            return detach_optional(session, row)

    def list_pending(self, *, limit: int = 50) -> List[DocumentJobs]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(DocumentJobs)
                    .where(DocumentJobs.status == "pending")
                    .order_by(DocumentJobs.created_at)
                    .limit(limit)
                ).all()
            )
            return detach_all(session, rows)

    def list_by_permit_id(self, permit_id: UUID) -> List[DocumentJobs]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(DocumentJobs).where(DocumentJobs.permit_id == permit_id)
                ).all()
            )
            return detach_all(session, rows)

    def list_by_application_id(self, application_id: UUID) -> List[DocumentJobs]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(DocumentJobs).where(DocumentJobs.application_id == application_id)
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: DocumentJobs) -> DocumentJobs:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def merge_update(self, row: DocumentJobs) -> DocumentJobs | None:
        with get_session() as session:
            existing = session.get(DocumentJobs, row.job_id)
            if existing is None:
                return None
            existing.application_id = row.application_id
            existing.permit_id = row.permit_id
            existing.job_type = row.job_type
            existing.status = row.status
            existing.error_message = row.error_message
            existing.triggered_by = row.triggered_by
            existing.trigger_source = row.trigger_source
            existing.retry_count = row.retry_count
            existing.payload_json = row.payload_json
            if row.started_at is not None:
                existing.started_at = row.started_at
            if row.finished_at is not None:
                existing.finished_at = row.finished_at
            existing.updated_at = row.updated_at
            session.flush()
            session.refresh(existing)
            return detach_optional(session, existing)
