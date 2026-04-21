"""
申請案件唯讀查詢（對應 5.4 GET 系列）。

責任：明細、列表、編輯模型、時間軸；不修改聚合狀態。
"""

from __future__ import annotations

from uuid import UUID

from ..dtos import (
    ApplicationDetailDTO,
    ApplicationEditModelDTO,
    ApplicationSummaryDTO,
    StatusHistoryEntryDTO,
)
from .application_mappers import application_to_detail_dto, application_to_summary_dto
from .application_service_context import ApplicationServiceContext


class ApplicationQueryService:
    """讀取專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def get_application(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        views = self._c.read.list_attachment_summaries(application_id)
        return application_to_detail_dto(app, attachment_views=views)

    def list_applications_for_applicant(
        self,
        applicant_user_id: UUID,
        *,
        limit: int = 100,
    ) -> list[ApplicationSummaryDTO]:
        ids = self._c.read.list_application_ids_for_applicant(
            applicant_user_id,
            limit=limit,
        )
        out: list[ApplicationSummaryDTO] = []
        for aid in ids:
            app = self._c.repo.get_by_id(aid)
            if app is not None:
                out.append(application_to_summary_dto(app))
        return out

    def get_edit_model(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationEditModelDTO:
        detail = self.get_application(application_id, applicant_user_id=applicant_user_id)
        return ApplicationEditModelDTO(detail=detail)

    def get_timeline(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[StatusHistoryEntryDTO]:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        return [
            StatusHistoryEntryDTO(
                history_id=h.history_id,
                from_status=h.from_status,
                to_status=h.to_status,
                changed_by=h.changed_by,
                reason=h.reason,
                created_at=h.created_at,
            )
            for h in app.status_histories
        ]
