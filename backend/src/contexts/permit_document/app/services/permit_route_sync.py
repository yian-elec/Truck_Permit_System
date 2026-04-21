"""
許可證 **route_summary_text**／候選參照與 **routing.route_plans** 最新選線對齊。

責任：使用者於選路後更新計畫時，既有 **permit.permits** 列不會自動寫回；
在產檔／下載前呼叫 **sync_permit_route_from_latest_plan**，使 PDF 與 API 摘要與當前計畫一致。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from src.contexts.permit_document.app.errors import (
    PermitNotFoundAppError,
    PermitValidationAppError,
)
from src.contexts.permit_document.app.services.integrations.permit_issuance_context_reader import (
    PermitIssuanceContextReader,
    build_route_summary_text_for_plan,
)
from src.contexts.permit_document.infra.repositories.permits_repository import PermitsRepository
from src.contexts.permit_document.infra.schema.permits import Permits


def sync_permit_route_from_latest_plan(permit_id: UUID) -> bool:
    """
    依 **PermitIssuanceContextReader.load** 之快照重算路線摘要並 merge 許可列。

    Returns:
        是否有寫入資料庫（內容或候選／覆寫參照有變更）。
    """
    repo = PermitsRepository()
    permit = repo.get_by_id(permit_id)
    if permit is None:
        return False

    issuance = PermitIssuanceContextReader()
    try:
        snap = issuance.load(permit.application_id)
    except PermitNotFoundAppError:
        return False
    sel, ovr = snap.selected_candidate_id, snap.override_id
    if sel is None and ovr is None:
        return False

    try:
        new_text = build_route_summary_text_for_plan(
            permit.application_id, sel, override_id=ovr
        )
    except PermitValidationAppError:
        return False

    now = datetime.now(timezone.utc)
    if (
        new_text == permit.route_summary_text
        and sel == permit.selected_candidate_id
        and ovr == permit.override_id
    ):
        return False

    repo.merge_update(
        Permits(
            permit_id=permit.permit_id,
            permit_no=permit.permit_no,
            application_id=permit.application_id,
            status=permit.status,
            approved_start_at=permit.approved_start_at,
            approved_end_at=permit.approved_end_at,
            selected_candidate_id=sel,
            override_id=ovr,
            route_summary_text=new_text,
            note=permit.note,
            issued_at=permit.issued_at,
            issued_by=permit.issued_by,
            revoked_at=permit.revoked_at,
            revoked_by=permit.revoked_by,
            revoked_reason=permit.revoked_reason,
            created_at=permit.created_at,
            updated_at=now,
        )
    )
    return True
