"""
UC-ROUTE-04、UC-ROUTE-05、承辦 replan：選定候選、人工改線、觸發重新規劃。

責任：驗證 application 與計畫一致性、呼叫領域狀態轉移、協調 Infra 寫入；
人工改線後寫入 officer_route_overrides 並將計畫標為 officer_adjusted（完整重算可替換 SpatialRuleHitPort）。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.routing_restriction.app.dtos.route_plan_dtos import (
    OfficerOverrideInputDTO,
    RoutePlanDetailDTO,
    SelectCandidateInputDTO,
)
from src.contexts.routing_restriction.app.errors import RoutingConflictAppError, to_routing_app_error
from src.contexts.routing_restriction.app.services.route_plan_query_application_service import (
    _plan_to_detail_dto,
)
from src.contexts.routing_restriction.app.services.route_planning_application_service import (
    RoutePlanningApplicationService,
)
from src.contexts.routing_restriction.domain.entities.officer_route_override import (
    OfficerRouteOverride,
)
from src.contexts.routing_restriction.infra.repositories.officer_route_override_repository import (
    OfficerRouteOverrideRepository,
)
from src.contexts.routing_restriction.infra.repositories.route_plan_repository import (
    RoutePlanRepository,
)
from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
    parse_linestring_wkt,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoutePlanReviewApplicationService:
    """審查端路線規劃操作服務。"""

    def __init__(
        self,
        *,
        route_plans: RoutePlanRepository | None = None,
        overrides: OfficerRouteOverrideRepository | None = None,
        planning: RoutePlanningApplicationService | None = None,
    ) -> None:
        self._plans = route_plans or RoutePlanRepository()
        self._overrides = overrides or OfficerRouteOverrideRepository()
        self._planning = planning or RoutePlanningApplicationService(
            route_plans=self._plans,
        )

    def select_candidate(
        self,
        application_id: UUID,
        dto: SelectCandidateInputDTO,
    ) -> RoutePlanDetailDTO:
        """UC-ROUTE-04：選定候選並持久化。"""
        now = _utc_now()
        try:
            plan = self._plans.find_latest_by_application_id(application_id)
            if plan is None:
                raise LookupError("route_plan not found")
            if plan.application_id != application_id:
                raise RoutingConflictAppError("route_plan does not belong to application")
            plan.select_candidate(dto.candidate_id, now=now)
            self._plans.update_plan_header(plan)
            return _plan_to_detail_dto(plan)
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def officer_override_route(
        self,
        application_id: UUID,
        dto: OfficerOverrideInputDTO,
        *,
        officer_user_id: UUID,
    ) -> RoutePlanDetailDTO:
        """
        UC-ROUTE-05：寫入人工改線並更新計畫狀態。

        責任：幾何以 WKT 解析；**不**於此處重跑完整規劃管線（可後續接上）。
        """
        now = _utc_now()
        try:
            geom = parse_linestring_wkt(dto.override_line_wkt)
            override = OfficerRouteOverride(
                override_id=uuid4(),
                application_id=application_id,
                override_geom=geom,
                override_reason=dto.override_reason,
                created_by=officer_user_id,
                base_candidate_id=dto.base_candidate_id,
                created_at=now,
            )
            self._overrides.save(override)

            plan = self._plans.find_latest_by_application_id(application_id)
            if plan is None:
                raise LookupError("route_plan not found")
            plan.mark_officer_adjusted(now=now)
            self._plans.update_plan_header(plan)
            return _plan_to_detail_dto(plan)
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def replan(self, application_id: UUID) -> UUID:
        """
        承辦觸發重新自動規劃（再跑 UC-ROUTE-02）。

        責任：要求最新 RouteRequest 仍處於可規劃狀態；成功回傳新 route_plan_id。
        """
        try:
            return self._planning.run_auto_planning_for_application(application_id)
        except Exception as exc:
            raise to_routing_app_error(exc) from exc
