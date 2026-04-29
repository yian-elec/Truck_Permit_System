"""
UC-ROUTE-03：路線規劃讀取模型組裝。

責任：依 application_id 取最新 RoutePlan，轉為 DTO；不含業務狀態變更。
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from src.contexts.routing_restriction.app.dtos.route_plan_dtos import (
    GeoPointDTO,
    NoRouteExplanationDTO,
    OfficerOverrideSummaryDTO,
    RouteCandidateDTO,
    RoutePlanDetailDTO,
    RouteRuleHitDTO,
    RouteRuleHitQueryDTO,
    RouteSegmentDTO,
)
from src.contexts.routing_restriction.domain.entities.route_plan import RoutePlan
from src.contexts.routing_restriction.infra.repositories.officer_route_override_repository import (
    OfficerRouteOverrideRepository,
)
from src.contexts.routing_restriction.infra.repositories.route_plan_repository import (
    RoutePlanRepository,
)
from src.contexts.routing_restriction.infra.repositories.route_request_repository import (
    RouteRequestRepository,
)


class RoutePlanQueryApplicationService:
    """路線規劃查詢服務。"""

    def __init__(
        self,
        *,
        route_plans: RoutePlanRepository | None = None,
        officer_overrides: OfficerRouteOverrideRepository | None = None,
        route_requests: RouteRequestRepository | None = None,
    ) -> None:
        self._plans = route_plans or RoutePlanRepository()
        self._overrides = officer_overrides or OfficerRouteOverrideRepository()
        self._requests = route_requests or RouteRequestRepository()

    def get_latest_route_plan(self, application_id: UUID) -> RoutePlanDetailDTO | None:
        """最新一筆規劃；無則 None。"""
        plan = self._plans.find_latest_by_application_id(application_id)
        if plan is None:
            return None
        dto = _plan_to_detail_dto(plan)
        req = self._requests.get_by_id(plan.route_request_id)
        if req is not None:
            og: GeoPointDTO | None = None
            dg: GeoPointDTO | None = None
            if req.origin_point is not None:
                og = GeoPointDTO(
                    latitude=req.origin_point.latitude,
                    longitude=req.origin_point.longitude,
                )
            if req.destination_point is not None:
                dg = GeoPointDTO(
                    latitude=req.destination_point.latitude,
                    longitude=req.destination_point.longitude,
                )
            dto = dto.model_copy(
                update={
                    "origin_text": req.origin_text,
                    "destination_text": req.destination_text,
                    "origin_geo": og,
                    "destination_geo": dg,
                }
            )
        ov_rows = self._overrides.list_by_application_id(application_id)
        summaries = [
            OfficerOverrideSummaryDTO(
                override_id=r.override_id,
                base_candidate_id=r.base_candidate_id,
                override_reason=(r.override_reason or "").strip(),
                created_at=r.created_at,
            )
            for r in ov_rows
        ]
        return dto.model_copy(update={"officer_overrides": summaries})

    def list_rule_hits_for_latest_plan(self, application_id: UUID) -> RouteRuleHitQueryDTO | None:
        """彙整最新計畫下所有候選之規則命中（供承辦檢視）。"""
        plan = self._plans.find_latest_by_application_id(application_id)
        if plan is None:
            return None
        hits: list[RouteRuleHitDTO] = []
        for c in plan.candidates:
            for h in c.rule_hits:
                seg_id = None
                if h.segment_index is not None and 0 <= h.segment_index < len(c.segments):
                    seg_id = c.segments[h.segment_index].segment_id
                hits.append(
                    RouteRuleHitDTO(
                        rule_id=h.rule_id,
                        rule_type=h.rule_type.value,
                        hit_type=h.severity.value,
                        segment_id=seg_id,
                        detail_text=h.detail_text,
                    )
                )
        return RouteRuleHitQueryDTO(route_plan_id=plan.route_plan_id, hits=hits)


def _plan_to_detail_dto(plan: RoutePlan) -> RoutePlanDetailDTO:
    cands: list[RouteCandidateDTO] = []
    for c in plan.candidates:
        score_val = c.score.value if c.score is not None else Decimal(0)
        segs = [
            RouteSegmentDTO(
                segment_id=s.segment_id,
                seq_no=s.seq_no,
                road_name=s.road_name,
                distance_m=s.distance_m,
                duration_s=s.duration_s,
                instruction_text=s.instruction_text,
                is_exception_road=s.is_exception_road,
            )
            for s in c.segments
        ]
        hits = [
            RouteRuleHitDTO(
                rule_id=h.rule_id,
                rule_type=h.rule_type.value,
                hit_type=h.severity.value,
                segment_id=(
                    c.segments[h.segment_index].segment_id
                    if h.segment_index is not None
                    and 0 <= h.segment_index < len(c.segments)
                    else None
                ),
                detail_text=h.detail_text,
            )
            for h in c.rule_hits
        ]
        cands.append(
            RouteCandidateDTO(
                candidate_id=c.candidate_id,
                candidate_rank=c.candidate_rank,
                distance_m=c.distance_m,
                duration_s=c.duration_s,
                score=score_val,
                summary_text=c.summary_text,
                area_road_sequence=c.area_road_sequence,
                segments=segs,
                rule_hits=hits,
            )
        )
    no = None
    if plan.no_route_explanation is not None:
        no = NoRouteExplanationDTO(
            code=plan.no_route_explanation.code.value,
            message=plan.no_route_explanation.message,
        )
    return RoutePlanDetailDTO(
        route_plan_id=plan.route_plan_id,
        application_id=plan.application_id,
        route_request_id=plan.route_request_id,
        status=plan.status.value,
        planning_version=plan.planning_version,
        map_version=plan.map_version,
        selected_candidate_id=plan.selected_candidate_id,
        candidates=cands,
        no_route=no,
    )
