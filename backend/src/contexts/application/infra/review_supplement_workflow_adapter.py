"""
審查 context 補件資料之 Application 埠實作。

責任：讀取 review.supplement_requests／supplement_items，組成申請人端補件通知 DTO。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.contexts.application.app.dtos import SupplementRequestItemDTO
from src.contexts.application.app.errors import ApplicationValidationAppError
from src.contexts.application.app.services.ports.outbound import SupplementWorkflowPort
from src.contexts.review_decision.infra.repositories import SupplementRequestsRepository


class ReviewSupplementWorkflowAdapter(SupplementWorkflowPort):
    """以 review schema 實作補件協作埠。"""

    def __init__(self) -> None:
        self._supplements = SupplementRequestsRepository()

    def assert_may_finalize_supplement_response(self, application_id: UUID) -> None:
        _ = application_id

    def record_applicant_supplement_reply(
        self,
        application_id: UUID,
        supplement_request_id: UUID,
        *,
        applicant_note: str | None,
        now: datetime,
    ) -> None:
        n = self._supplements.fulfill_specific_supplement_if_open(
            application_id,
            supplement_request_id,
            applicant_note=applicant_note,
            now=now,
        )
        if n == 0:
            raise ApplicationValidationAppError(
                "找不到可回覆的待補件紀錄，請重新整理後再試，或確認已選擇尚未完成的補件項目。",
                details={
                    "application_id": str(application_id),
                    "supplement_request_id": str(supplement_request_id),
                },
            )

    def count_open_supplement_requests(self, application_id: UUID) -> int:
        return self._supplements.count_open_requests_for_application(application_id)

    def list_supplement_notifications(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestItemDTO]:
        rows = self._supplements.list_requests_by_application_id(application_id)
        rows_sorted = sorted(rows, key=lambda r: r.created_at, reverse=True)
        out: list[SupplementRequestItemDTO] = []
        for r in rows_sorted:
            msg = (r.message or "").strip()
            raw_title = (getattr(r, "title", None) or "").strip()
            title = raw_title or _fallback_title(r.created_at)
            out.append(
                SupplementRequestItemDTO(
                    request_id=r.supplement_request_id,
                    title=title,
                    description=msg or None,
                    status=r.status,
                    created_at=r.created_at,
                )
            )
        return out


def _fallback_title(created_at) -> str:
    return f"補件通知 · {created_at.strftime('%Y-%m-%d %H:%M')}"
