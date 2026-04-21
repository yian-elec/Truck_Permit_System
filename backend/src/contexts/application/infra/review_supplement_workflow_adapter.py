"""
審查 context 補件資料之 Application 埠實作。

責任：讀取 review.supplement_requests／supplement_items，組成申請人端補件通知 DTO。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.application.app.dtos import SupplementRequestItemDTO
from src.contexts.application.app.services.ports.outbound import SupplementWorkflowPort
from src.contexts.review_decision.infra.repositories import SupplementRequestsRepository


class ReviewSupplementWorkflowAdapter(SupplementWorkflowPort):
    """以 review schema 實作補件協作埠。"""

    def __init__(self) -> None:
        self._supplements = SupplementRequestsRepository()

    def assert_may_finalize_supplement_response(self, application_id: UUID) -> None:
        _ = application_id

    def list_supplement_notifications(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestItemDTO]:
        rows = self._supplements.list_requests_by_application_id(application_id)
        rows_sorted = sorted(rows, key=lambda r: r.created_at, reverse=True)
        out: list[SupplementRequestItemDTO] = []
        for r in rows_sorted:
            item_rows = self._supplements.list_items_for_request(r.supplement_request_id)
            title = _title_for_request(r.created_at)
            description = _description_for_request(r.message, item_rows)
            out.append(
                SupplementRequestItemDTO(
                    request_id=r.supplement_request_id,
                    title=title,
                    description=description,
                    created_at=r.created_at,
                )
            )
        return out


def _title_for_request(created_at) -> str:
    return f"補件通知 · {created_at.strftime('%Y-%m-%d %H:%M')}"


def _description_for_request(message: str, item_rows) -> str | None:
    msg = (message or "").strip()
    parts: list[str] = []
    if msg:
        parts.append(msg)
    if item_rows:
        bullet_lines = []
        for it in item_rows:
            line = f"・{it.item_name}（{it.item_code}）"
            if it.note and str(it.note).strip():
                line += f" — {it.note.strip()}"
            bullet_lines.append(line)
        parts.append("須補交或處理項目：\n" + "\n".join(bullet_lines))
    if not parts:
        return None
    return "\n\n".join(parts)
