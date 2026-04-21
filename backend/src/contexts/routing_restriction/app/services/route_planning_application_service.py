"""
UC-ROUTE-02：自動規劃候選路線、規則檢核管線、寫入 route_plans 樹狀資料。

責任：
- 讀取已 `planning_queued` 之最新 RouteRequest。
- 決定 map_version（圖資 layer）與 planning_version 字串。
- 呼叫 RoutingProviderPort 取得候選 → SpatialRuleHitPort 附加命中 → RestrictionEvaluationService 計分與無路判定。
- 單一交易 `save_full_plan`；若全部不可行，領域會帶結構化 no_route 說明。
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from shared.core.logger.logger import logger

from src.contexts.routing_restriction.app.errors import to_routing_app_error
from src.contexts.routing_restriction.app.services.ports.outbound import (
    RoutingProviderPort,
    SpatialRuleHitPort,
)
from src.contexts.routing_restriction.domain.entities.route_plan import RoutePlan
from src.contexts.routing_restriction.domain.services.restriction_evaluation_service import (
    RestrictionEvaluationService,
)
from src.contexts.routing_restriction.infra.repositories.map_layers_repository import (
    MapLayersRepository,
)
from src.contexts.routing_restriction.infra.repositories.route_plan_repository import (
    RoutePlanRepository,
)
from src.contexts.routing_restriction.infra.repositories.route_request_repository import (
    RouteRequestRepository,
)
from src.contexts.routing_restriction.app.services.route_area_enrichment_service import (
    RouteAreaEnrichmentService,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoutePlanningApplicationService:
    """自動規劃用例服務。"""

    def __init__(
        self,
        *,
        route_requests: RouteRequestRepository | None = None,
        route_plans: RoutePlanRepository | None = None,
        map_layers: MapLayersRepository | None = None,
        routing_provider: RoutingProviderPort | None = None,
        spatial_hits: SpatialRuleHitPort | None = None,
    ) -> None:
        self._requests = route_requests or RouteRequestRepository()
        self._plans = route_plans or RoutePlanRepository()
        self._layers = map_layers or MapLayersRepository()
        if routing_provider is None or spatial_hits is None:
            from src.contexts.routing_restriction.app.services.ports.outbound import (
                NoopSpatialRuleHitPort,
                StubRoutingProviderPort,
            )

            self._provider = routing_provider or StubRoutingProviderPort()
            self._spatial = spatial_hits or NoopSpatialRuleHitPort()
        else:
            self._provider = routing_provider
            self._spatial = spatial_hits

    def run_auto_planning_for_application(self, application_id: UUID) -> UUID:
        """
        對指定案件執行一輪自動規劃並持久化。

        Returns:
            新建立之 route_plan_id

        Raises:
            LookupError: 無路線申請或狀態非 planning_queued
            RoutingAppError: 領域／驗證錯誤
        """
        from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
            RouteRequestStatus,
        )

        now = _utc_now()
        try:
            req = self._requests.find_latest_by_application_id(application_id)
            if req is None:
                raise LookupError("no route_request for application")
            if req.status != RouteRequestStatus.PLANNING_QUEUED:
                raise LookupError(
                    f"route_request not ready for planning: status={req.status.value}"
                )
            if req.origin_point is None or req.destination_point is None:
                raise LookupError("route_request missing geocoded points")

            o = req.origin_point
            d = req.destination_point
            logger.info(
                "UC-ROUTE-02 planning start",
                context="Routing",
                application_id=str(application_id),
                route_request_id=str(req.route_request_id),
                origin_lat=f"{o.latitude:.7f}",
                origin_lon=f"{o.longitude:.7f}",
                dest_lat=f"{d.latitude:.7f}",
                dest_lon=f"{d.longitude:.7f}",
            )

            map_ver = self._layers.resolve_map_version_for_planning()
            plan_ver = f"plan-{uuid4().hex[:12]}"
            plan_id = uuid4()
            plan = RoutePlan.start_planning(
                route_plan_id=plan_id,
                application_id=application_id,
                route_request_id=req.route_request_id,
                planning_version=plan_ver,
                map_version=map_ver,
                now=now,
            )

            raw_candidates = self._provider.fetch_candidates(
                req.origin_point,
                req.destination_point,
                vehicle=req.vehicle_profile,
                departure_at=req.requested_departure_at,
            )
            hint_getter = getattr(self._provider, "consume_routing_empty_hint", None)
            provider_empty_hint = (
                hint_getter() if callable(hint_getter) else None
            )
            logger.info(
                "UC-ROUTE-02 provider fetch_candidates done",
                context="Routing",
                application_id=str(application_id),
                raw_candidate_count=len(raw_candidates),
            )
            fixed: list = []
            for c in raw_candidates:
                fixed.append(replace(c, route_plan_id=plan.route_plan_id))
            with_hits = self._spatial.attach_rule_hits(
                fixed,
                vehicle=req.vehicle_profile,
                departure_at=req.requested_departure_at,
            )
            for c in with_hits:
                logger.info(
                    "UC-ROUTE-02 after attach_rule_hits",
                    context="Routing",
                    application_id=str(application_id),
                    candidate_rank=c.candidate_rank,
                    segments=len(c.segments),
                    rule_hits=len(c.rule_hits),
                )
            base_scores = [Decimal(1000 - i) for i in range(len(with_hits))]
            processed, no_route = RestrictionEvaluationService.evaluate_candidates_after_provider(
                with_hits,
                base_scores=base_scores,
                provider_empty_hint=provider_empty_hint if not with_hits else None,
            )
            if no_route is not None:
                logger.info(
                    "UC-ROUTE-02 evaluation: no feasible route",
                    context="Routing",
                    application_id=str(application_id),
                    no_route_code=no_route.code.value,
                    no_route_message=(no_route.message or "")[:800],
                )
            else:
                logger.info(
                    "UC-ROUTE-02 evaluation: feasible candidates exist",
                    context="Routing",
                    application_id=str(application_id),
                    processed_count=len(processed),
                )
                processed = RouteAreaEnrichmentService().enrich_candidates(processed)
            plan.set_candidates_after_planning(
                processed,
                now=now,
                no_route=no_route,
            )
            self._plans.save_full_plan(plan)
            logger.info(
                "UC-ROUTE-02 persisted route_plan",
                context="Routing",
                application_id=str(application_id),
                route_plan_id=str(plan.route_plan_id),
                status=plan.status.value,
                candidate_count=len(plan.candidates),
            )
            return plan.route_plan_id
        except Exception as exc:
            raise to_routing_app_error(exc) from exc
