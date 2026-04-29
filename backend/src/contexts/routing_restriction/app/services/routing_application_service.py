"""
Routing_Restriction 應用層用例外觀（Facade）。

責任：對 API 或上層模組提供單一進入點，內部委派至依 UC 劃分之專責服務；
共用同一組 RoutePlanRepository 實例，避免快取不一致。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.routing_restriction.app.dtos import (
    CreateRestrictionRuleInputDTO,
    CreateRouteRequestInputDTO,
    MapImportJobStatusDTO,
    MapLayerListItemDTO,
    OfficerOverrideInputDTO,
    PatchRestrictionRuleInputDTO,
    PatchSelectedItineraryInputDTO,
    RequestKmlImportInputDTO,
    RestrictionRuleDetailDTO,
    RestrictionRuleListItemDTO,
    RoutePlanDetailDTO,
    RouteRequestStatusDTO,
    RouteRuleHitQueryDTO,
    SelectCandidateInputDTO,
)
from src.contexts.routing_restriction.app.services.map_import_application_service import (
    MapImportApplicationService,
)
from src.contexts.routing_restriction.app.services.restriction_admin_application_service import (
    RestrictionAdminApplicationService,
)
from src.contexts.routing_restriction.app.services.route_plan_query_application_service import (
    RoutePlanQueryApplicationService,
)
from src.contexts.routing_restriction.app.services.route_plan_review_application_service import (
    RoutePlanReviewApplicationService,
)
from src.contexts.routing_restriction.app.services.route_planning_application_service import (
    RoutePlanningApplicationService,
)
from src.contexts.routing_restriction.app.services.route_request_application_service import (
    RouteRequestApplicationService,
)
from src.contexts.routing_restriction.infra.repositories.route_plan_repository import (
    RoutePlanRepository,
)
from src.contexts.routing_restriction.infra.geocoding.geocoding_factory import (
    build_geocoding_port_from_settings,
)
from src.contexts.routing_restriction.infra.routing.routing_provider_factory import (
    build_routing_provider_from_settings,
)
from src.contexts.routing_restriction.infra.spatial.postgis_spatial_rule_hit_port import (
    PostgisSpatialRuleHitPort,
)


class RoutingApplicationService:
    """路線與限制情境之應用服務總入口。"""

    def __init__(self) -> None:
        self._route_plans = RoutePlanRepository()
        self.route_requests = RouteRequestApplicationService(
            geocoding=build_geocoding_port_from_settings(),
        )
        self.planning = RoutePlanningApplicationService(
            route_plans=self._route_plans,
            spatial_hits=PostgisSpatialRuleHitPort(),
            routing_provider=build_routing_provider_from_settings(),
        )
        self.plan_queries = RoutePlanQueryApplicationService(route_plans=self._route_plans)
        self.review = RoutePlanReviewApplicationService(
            route_plans=self._route_plans,
            planning=self.planning,
        )
        self.admin = RestrictionAdminApplicationService()
        self.map_import = MapImportApplicationService()

    # --- Applicant / 路線申請 ---
    def create_route_request(
        self,
        application_id: UUID,
        dto: CreateRouteRequestInputDTO,
        *,
        requested_by: UUID | None,
    ) -> RouteRequestStatusDTO:
        # UC-ROUTE-02 由審查端「重新規劃」或背景 worker 觸發；申請人僅送出路線需求（planning_queued）。
        return self.route_requests.create_route_request(
            application_id,
            dto,
            requested_by=requested_by,
        )

    def replan_route_request(
        self,
        application_id: UUID,
        dto: CreateRouteRequestInputDTO,
        *,
        requested_by: UUID | None,
    ) -> RouteRequestStatusDTO:
        return self.route_requests.replan_route_request(
            application_id,
            dto,
            requested_by=requested_by,
        )

    def get_route_preview_request_status(
        self,
        application_id: UUID,
    ) -> RouteRequestStatusDTO | None:
        return self.route_requests.get_route_request_status(application_id)

    # --- 規劃 ---
    def run_auto_planning(self, application_id: UUID) -> UUID:
        return self.planning.run_auto_planning_for_application(application_id)

    def get_route_plan(self, application_id: UUID) -> RoutePlanDetailDTO | None:
        return self.plan_queries.get_latest_route_plan(application_id)

    def get_route_plan_rule_hits(self, application_id: UUID) -> RouteRuleHitQueryDTO | None:
        return self.plan_queries.list_rule_hits_for_latest_plan(application_id)

    # --- Review ---
    def select_route_candidate(
        self,
        application_id: UUID,
        dto: SelectCandidateInputDTO,
    ) -> RoutePlanDetailDTO:
        return self.review.select_candidate(application_id, dto)

    def officer_override_route(
        self,
        application_id: UUID,
        dto: OfficerOverrideInputDTO,
        *,
        officer_user_id: UUID,
    ) -> RoutePlanDetailDTO:
        return self.review.officer_override_route(
            application_id,
            dto,
            officer_user_id=officer_user_id,
        )

    def patch_selected_itinerary(
        self,
        application_id: UUID,
        dto: PatchSelectedItineraryInputDTO,
    ) -> RoutePlanDetailDTO:
        return self.review.patch_selected_itinerary(application_id, dto)

    def review_replan(self, application_id: UUID) -> UUID:
        return self.review.replan(application_id)

    # --- Admin ---
    def admin_list_rules(
        self,
        *,
        layer_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[RestrictionRuleListItemDTO]:
        return self.admin.list_rules(layer_id=layer_id, is_active=is_active)

    def admin_get_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        return self.admin.get_rule(rule_id)

    def admin_create_rule(self, dto: CreateRestrictionRuleInputDTO) -> RestrictionRuleDetailDTO:
        return self.admin.create_rule(dto)

    def admin_patch_rule(
        self,
        rule_id: UUID,
        dto: PatchRestrictionRuleInputDTO,
    ) -> RestrictionRuleDetailDTO | None:
        return self.admin.patch_rule(rule_id, dto)

    def admin_activate_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        return self.admin.activate_rule(rule_id)

    def admin_deactivate_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        return self.admin.deactivate_rule(rule_id)

    def admin_list_map_layers(self) -> list[MapLayerListItemDTO]:
        return self.admin.list_map_layers()

    def admin_publish_map_layer(self, layer_id: UUID) -> MapLayerListItemDTO | None:
        return self.admin.publish_map_layer(layer_id)

    def admin_request_kml_import(self, dto: RequestKmlImportInputDTO) -> MapImportJobStatusDTO:
        return self.map_import.request_kml_import(dto)

    def admin_get_map_import_job(self, import_job_id: str) -> MapImportJobStatusDTO | None:
        return self.map_import.get_import_job_status(import_job_id)
