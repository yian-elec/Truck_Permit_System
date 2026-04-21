"""
RoutePlan — 路線規劃聚合根。

責任：在單一路線請求之上維護規劃版本、圖資版本、候選路線集合、選定候選與無路說明；
實作選線、標記無路、承辦調線後狀態等不變條件。候選之產生與空間命中由 App 協調 Provider 與
RestrictionEvaluationService 後回填本聚合。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.contexts.routing_restriction.domain.errors import (
    CandidateNotInPlanError,
    InvalidRoutePlanStateError,
    RoutingInvalidValueError,
)
from src.contexts.routing_restriction.domain.value_objects.no_route_explanation import (
    NoRouteExplanation,
)
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    NoRouteReasonCode,
    RoutePlanStatus,
)

from .route_candidate import RouteCandidate


@dataclass
class RoutePlan:
    """
    路線規劃結果（對應 routing.route_plans + candidates）。

    責任：
    - **planning_version / map_version** 與規格一致，全程保留以利稽核與重播。
    - **candidates** 僅透過 `set_candidates_after_planning` 等方法整批置換，避免外部任意 append。
    - **no_route_explanation** 在狀態為 NO_ROUTE 時應已填寫。
    """

    route_plan_id: UUID
    application_id: UUID
    route_request_id: UUID
    status: RoutePlanStatus
    planning_version: str
    map_version: str
    candidates: List[RouteCandidate] = field(default_factory=list)
    selected_candidate_id: Optional[UUID] = None
    no_route_explanation: Optional[NoRouteExplanation] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._assert_versions()

    def _assert_versions(self) -> None:
        if not (self.planning_version or "").strip():
            raise RoutingInvalidValueError("planning_version must be non-empty")
        if not (self.map_version or "").strip():
            raise RoutingInvalidValueError("map_version must be non-empty")

    @classmethod
    def start_planning(
        cls,
        *,
        route_plan_id: UUID,
        application_id: UUID,
        route_request_id: UUID,
        planning_version: str,
        map_version: str,
        now: datetime,
    ) -> RoutePlan:
        """
        開始一輪自動規劃（UC-ROUTE-02 起始）。

        責任：狀態 PLANNING，候選為空直至規劃完成寫入。
        """
        return cls(
            route_plan_id=route_plan_id,
            application_id=application_id,
            route_request_id=route_request_id,
            status=RoutePlanStatus.PLANNING,
            planning_version=planning_version,
            map_version=map_version,
            candidates=[],
            selected_candidate_id=None,
            no_route_explanation=None,
            created_at=now,
            updated_at=now,
        )

    def set_candidates_after_planning(
        self,
        candidates: List[RouteCandidate],
        *,
        now: datetime,
        no_route: Optional[NoRouteExplanation] = None,
    ) -> None:
        """
        規劃與規則檢核完成後寫入候選集合。

        責任：
        - 若 **no_route** 提供，狀態轉為 NO_ROUTE 且須附原因（不可無訊息）。
        - 否則應有至少一筆候選且狀態為 CANDIDATES_READY；若候選皆不可行，呼叫端應先以
          RestrictionEvaluationService 判定並傳入適當之 no_route。
        """
        if self.status not in (RoutePlanStatus.PLANNING, RoutePlanStatus.CANDIDATES_READY):
            raise InvalidRoutePlanStateError(
                "Cannot attach candidates unless planning is in progress or refreshing",
                current_status=self.status.value,
            )
        if no_route is not None:
            if not (no_route.message or "").strip():
                raise RoutingInvalidValueError(
                    "no_route explanation must include a non-empty message"
                )
            self.candidates = []
            self.selected_candidate_id = None
            self.no_route_explanation = no_route
            self.status = RoutePlanStatus.NO_ROUTE
            self.updated_at = now
            return
        if not candidates:
            raise RoutingInvalidValueError(
                "When feasible, candidates must be non-empty; use no_route with explanation instead"
            )
        self.candidates = list(candidates)
        self.no_route_explanation = None
        self.status = RoutePlanStatus.CANDIDATES_READY
        self.updated_at = now

    def select_candidate(self, candidate_id: UUID, *, now: datetime) -> None:
        """
        承辦選定候選（UC-ROUTE-04 領域部分）。

        責任：驗證 candidate 屬於本計畫；不可在 NO_ROUTE 或 PLANNING 狀態選線。
        """
        if self.status not in (
            RoutePlanStatus.CANDIDATES_READY,
            RoutePlanStatus.OFFICER_ADJUSTED,
        ):
            raise InvalidRoutePlanStateError(
                "Candidate selection not allowed in current state",
                current_status=self.status.value,
            )
        ids = {c.candidate_id for c in self.candidates}
        if candidate_id not in ids:
            raise CandidateNotInPlanError(
                "Candidate does not belong to this route plan",
                candidate_id=candidate_id,
                route_plan_id=self.route_plan_id,
            )
        self.selected_candidate_id = candidate_id
        self.status = RoutePlanStatus.CANDIDATE_SELECTED
        self.updated_at = now

    def mark_officer_adjusted(self, *, now: datetime) -> None:
        """人工改線完成並通過檢核後之狀態（UC-ROUTE-05 後續寫入由 App 觸發）。"""
        self.status = RoutePlanStatus.OFFICER_ADJUSTED
        self.updated_at = now

    def mark_replanning(self, *, planning_version: str, now: datetime) -> None:
        """
        重新規劃：清空選取與舊候選語意由呼叫端置換；更新 planning_version。

        責任：保留 map_version 除非 App 一併呼叫更新；此處僅更新 planning 版本字串。
        """
        if not (planning_version or "").strip():
            raise RoutingInvalidValueError("planning_version must be non-empty")
        self.planning_version = planning_version
        self.status = RoutePlanStatus.PLANNING
        self.candidates = []
        self.selected_candidate_id = None
        self.no_route_explanation = None
        self.updated_at = now

    def update_map_version(self, map_version: str, now: datetime) -> None:
        """圖資版本變更（例如 layer publish）時更新，供與規則集對齊。"""
        if not (map_version or "").strip():
            raise RoutingInvalidValueError("map_version must be non-empty")
        self.map_version = map_version
        self.updated_at = now

    def build_no_route_all_forbidden(self, detail: str) -> NoRouteExplanation:
        """
        輔助建立「所有候選均觸犯禁止規則」之標準說明。

        責任：封裝原因碼與訊息組合，避免呼叫端硬編字串分散。
        """
        return NoRouteExplanation(
            code=NoRouteReasonCode.ALL_CANDIDATES_FORBIDDEN,
            message=detail or "All candidate routes violate active restriction rules.",
        )
