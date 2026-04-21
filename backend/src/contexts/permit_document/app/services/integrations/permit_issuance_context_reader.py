"""
UC-PERMIT-01 前置資料讀取：申請核准狀態、核准期間、最終路線候選。

責任：
- 讀取 **Application** 與 **RoutePlan**（跨 context Infra），組合成領域建立許可所需之輸入；
- 不寫入資料庫；錯誤轉為 **PermitValidationAppError**／**PermitNotFoundAppError**。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.contexts.application.domain.value_objects import ApplicationStatusPhase
from src.contexts.application.infra.repositories.application_repository_impl import (
    ApplicationRepositoryImpl,
)
from src.contexts.permit_document.app.errors import PermitNotFoundAppError, PermitValidationAppError
from src.contexts.review_decision.domain.value_objects.decision_type import DecisionType
from src.contexts.review_decision.infra.repositories.decisions_repository import DecisionsRepository
from src.contexts.routing_restriction.infra.repositories.route_plan_repository import (
    RoutePlanRepository,
)


@dataclass(frozen=True)
class PermitIssuanceSnapshot:
    """
    建立許可當下之唯讀快照（非 DTO 傳輸邊界，僅服務內部傳遞）。

    責任：承載 `application_approved`、通行期間（此處取自申請之 **requested_period**）、
    路線候選與覆寫 id（覆寫初版固定為 None，可日後接 officer override 讀取器）。
    """

    application_id: UUID
    application_approved: bool
    approved_start_at: datetime
    approved_end_at: datetime
    selected_candidate_id: UUID | None
    override_id: UUID | None
    application_no: str


class PermitIssuanceContextReader:
    """
    具體讀取器：ApplicationRepositoryImpl + RoutePlanRepository。

    責任：將跨 context 讀取集中於單一類別，利於測試替換與錯誤訊息一致化。
    """

    def __init__(
        self,
        *,
        applications: ApplicationRepositoryImpl | None = None,
        route_plans: RoutePlanRepository | None = None,
        decisions: DecisionsRepository | None = None,
    ) -> None:
        self._apps = applications or ApplicationRepositoryImpl()
        self._plans = route_plans or RoutePlanRepository()
        self._decisions = decisions or DecisionsRepository()

    def load(self, application_id: UUID) -> PermitIssuanceSnapshot:
        app = self._apps.get_by_id(application_id)
        if app is None:
            raise PermitNotFoundAppError("申請案件不存在", {"application_id": str(application_id)})

        approved = app.status.value == ApplicationStatusPhase.APPROVED.value
        start_at = app.requested_period.start_at
        end_at = app.requested_period.end_at

        plan = self._plans.find_latest_by_application_id(application_id)
        selected: UUID | None = None
        if plan is not None:
            selected = plan.selected_candidate_id

        override: UUID | None = None
        last_approve = self._last_approve_decision(application_id)
        if last_approve is not None:
            if selected is None:
                selected = last_approve.selected_candidate_id
            override = last_approve.override_id

        return PermitIssuanceSnapshot(
            application_id=application_id,
            application_approved=approved,
            approved_start_at=start_at,
            approved_end_at=end_at,
            selected_candidate_id=selected,
            override_id=override,
            application_no=app.application_no,
        )

    def _last_approve_decision(self, application_id: UUID):
        rows = self._decisions.list_by_application_id(application_id)
        last = None
        for row in rows:
            if row.decision_type == DecisionType.APPROVE.value:
                last = row
        return last


def _is_legacy_english_route_summary_placeholder(text: str) -> bool:
    """
    舊版曾將英文佔位寫入 **route_candidates.summary_text**／同步至 **permit.route_summary_text**；
    若仍優先採用該欄，PDF 會印出整句英文。偵測後改走路段名或中文後備句。
    """
    t = (text or "").strip()
    if not t:
        return False
    if "official route bound to selected_candidate_id" in t:
        return True
    if "Application " in t and "selected_candidate_id=" in t:
        return True
    return False


def build_route_summary_text_for_plan(
    application_id: UUID,
    selected_candidate_id: UUID | None,
    *,
    override_id: UUID | None = None,
) -> str:
    """
    將路線選定結果摘成可列印文字。

    優先 **routing.route_candidates.summary_text**；否則串接候選之路段 **road_name**；
    再退回候選識別說明。調線覆寫時僅能標示覆寫 id（初版）。
    """
    from sqlalchemy import select

    from shared.core.db.connection import get_session

    from src.contexts.routing_restriction.infra.schema.route_candidates import RouteCandidates
    from src.contexts.routing_restriction.infra.schema.route_segments import RouteSegments

    if selected_candidate_id is not None:
        with get_session() as session:
            cand = session.get(RouteCandidates, selected_candidate_id)
            if cand is not None:
                st = cand.summary_text
                if st is not None and str(st).strip():
                    raw = str(st).strip()
                    if not _is_legacy_english_route_summary_placeholder(raw):
                        return raw
                seg_rows = list(
                    session.scalars(
                        select(RouteSegments)
                        .where(RouteSegments.candidate_id == selected_candidate_id)
                        .order_by(RouteSegments.seq_no)
                    ).all()
                )
                names: list[str] = []
                for sr in seg_rows:
                    rn = sr.road_name
                    if rn is not None and str(rn).strip():
                        names.append(str(rn).strip())
                if names:
                    return " → ".join(names)
        return f"已選定核准路線（候選編號 {selected_candidate_id}）"

    if override_id is not None:
        return f"已採調線覆寫（編號 {override_id}）"

    raise PermitValidationAppError(
        "尚未選定路線候選或調線覆寫，無法建立許可證",
        {"application_id": str(application_id)},
    )


def build_permit_no_from_application(application_no: str) -> str:
    """
    產生許可字號（初版：與申請編號連動並加前綴）。

    責任：確保總長度 ≤ 30（**PermitNo** 上限）；若過長則截斷尾段。
    """
    raw = f"P-{application_no}".strip()
    return raw[:30]
