"""
ApplicationReadModelQuery 之 SQLAlchemy／預設實作。

責任：列表與附件摘要等唯讀查詢；送件條件不再依 routing.route_requests（路線需求由申請人儲存、
自動規劃由審查端執行，與 UC-APP-06 送件閘道分離）。
"""

from __future__ import annotations

from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.application.domain.read_models import AttachmentSummaryView
from src.contexts.application.domain.repositories import ApplicationReadModelQuery
from src.contexts.application.infra.schema import Applications, Attachments


class ApplicationReadModelQueryImpl(ApplicationReadModelQuery):
    """
    申請案件讀模型查詢實作。

    責任：將「列表、附件摘要」等跨表查詢封裝於此；與寫入聚合之 Repository 分離。
    """

    def list_application_ids_for_applicant(
        self, applicant_user_id: UUID, *, limit: int = 100
    ) -> list[UUID]:
        with get_session() as session:
            q = (
                session.query(Applications.application_id)
                .filter(Applications.applicant_user_id == applicant_user_id)
                .order_by(Applications.created_at.desc())
                .limit(limit)
            )
            return [row[0] for row in q.all()]

    def list_attachment_summaries(self, application_id: UUID) -> list[AttachmentSummaryView]:
        with get_session() as session:
            rows = (
                session.query(Attachments)
                .filter_by(application_id=application_id)
                .order_by(Attachments.uploaded_at.asc())
                .all()
            )
            return [
                AttachmentSummaryView(
                    attachment_id=r.attachment_id,
                    attachment_type=r.attachment_type,
                    file_id=r.file_id,
                    original_filename=r.original_filename,
                    mime_type=r.mime_type,
                    size_bytes=int(r.size_bytes),
                    status=r.status,
                    ocr_status=r.ocr_status,
                    uploaded_by=r.uploaded_by,
                    uploaded_at=r.uploaded_at,
                )
                for r in rows
            ]
