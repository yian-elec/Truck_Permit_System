"""
Routing_Restriction — HTTP 路由（規格 6.4）。

審查要點：
- **shared.api**：OpenAPI 範例僅用 `success_response`／`error_response`／`combine_responses`；
  實際回應經 `routing_api_response` → `api_response_with_logging`。
- **shared.decorators.error_handler**：同步用例本體置於 `@handle_api_errors` 之 `_core_*`，非 `BaseError`
  轉為 `SystemError` 後仍由包裝器輸出信封。
- **應用層 DTO**：請求／回應型別**僅**來自 `routing_restriction.app.dtos`，本檔不另定義業務結構。
- **路徑**：URL 採 kebab-case 段落；Python 路徑參數為 snake_case，並於 `Path(description=…)` 標註規格名稱。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, Request

from src.contexts.application.api.dependencies import get_applicant_user_id
from src.contexts.routing_restriction.api.dependencies import get_routing_application_service
from src.contexts.routing_restriction.api.response_utils import routing_api_response
from src.contexts.routing_restriction.app.dtos import (
    CreateRestrictionRuleInputDTO,
    CreateRouteRequestInputDTO,
    MapImportJobStatusDTO,
    MapLayerListItemDTO,
    OfficerOverrideInputDTO,
    PatchRestrictionRuleInputDTO,
    RequestKmlImportInputDTO,
    RestrictionRuleDetailDTO,
    RestrictionRuleListItemDTO,
    RoutePlanCreatedOutputDTO,
    RoutePlanDetailDTO,
    RouteRequestStatusDTO,
    RouteRuleHitQueryDTO,
    SelectCandidateInputDTO,
)
from src.contexts.routing_restriction.app.errors import RoutingNotFoundAppError
from src.contexts.routing_restriction.app.services.routing_application_service import (
    RoutingApplicationService,
)
from shared.api import combine_responses, error_response, success_response
from shared.core.logger.logger import logger
from shared.decorators import handle_api_errors

# ---------------------------------------------------------------------------
# 同步核心（@handle_api_errors）：與 decorators/error_handler 規範一致
# ---------------------------------------------------------------------------


@handle_api_errors
def _core_create_route_request(
    svc: RoutingApplicationService,
    application_id: UUID,
    body: CreateRouteRequestInputDTO,
    requested_by: UUID | None,
) -> RouteRequestStatusDTO:
    return svc.create_route_request(application_id, body, requested_by=requested_by)


@handle_api_errors
def _core_replan_route_request(
    svc: RoutingApplicationService,
    application_id: UUID,
    body: CreateRouteRequestInputDTO,
    requested_by: UUID | None,
) -> RouteRequestStatusDTO:
    return svc.replan_route_request(application_id, body, requested_by=requested_by)


@handle_api_errors
def _core_get_route_preview(
    svc: RoutingApplicationService,
    application_id: UUID,
) -> RouteRequestStatusDTO | None:
    return svc.get_route_preview_request_status(application_id)


@handle_api_errors
def _core_get_route_plan(
    svc: RoutingApplicationService,
    application_id: UUID,
) -> RoutePlanDetailDTO | None:
    return svc.get_route_plan(application_id)


@handle_api_errors
def _core_select_candidate(
    svc: RoutingApplicationService,
    application_id: UUID,
    body: SelectCandidateInputDTO,
) -> RoutePlanDetailDTO:
    return svc.select_route_candidate(application_id, body)


@handle_api_errors
def _core_officer_override(
    svc: RoutingApplicationService,
    application_id: UUID,
    body: OfficerOverrideInputDTO,
    officer_user_id: UUID,
) -> RoutePlanDetailDTO:
    return svc.officer_override_route(application_id, body, officer_user_id=officer_user_id)


@handle_api_errors
def _core_review_replan(svc: RoutingApplicationService, application_id: UUID) -> UUID:
    return svc.review_replan(application_id)


@handle_api_errors
def _core_rule_hits(
    svc: RoutingApplicationService,
    application_id: UUID,
) -> RouteRuleHitQueryDTO | None:
    return svc.get_route_plan_rule_hits(application_id)


@handle_api_errors
def _core_admin_list_rules(
    svc: RoutingApplicationService,
    layer_id: UUID | None,
    is_active: bool | None,
) -> list[RestrictionRuleListItemDTO]:
    return svc.admin_list_rules(layer_id=layer_id, is_active=is_active)


@handle_api_errors
def _core_admin_get_rule(svc: RoutingApplicationService, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
    return svc.admin_get_rule(rule_id)


@handle_api_errors
def _core_admin_create_rule(
    svc: RoutingApplicationService,
    body: CreateRestrictionRuleInputDTO,
) -> RestrictionRuleDetailDTO:
    return svc.admin_create_rule(body)


@handle_api_errors
def _core_admin_patch_rule(
    svc: RoutingApplicationService,
    rule_id: UUID,
    body: PatchRestrictionRuleInputDTO,
) -> RestrictionRuleDetailDTO | None:
    return svc.admin_patch_rule(rule_id, body)


@handle_api_errors
def _core_admin_activate_rule(
    svc: RoutingApplicationService,
    rule_id: UUID,
) -> RestrictionRuleDetailDTO | None:
    return svc.admin_activate_rule(rule_id)


@handle_api_errors
def _core_admin_deactivate_rule(
    svc: RoutingApplicationService,
    rule_id: UUID,
) -> RestrictionRuleDetailDTO | None:
    return svc.admin_deactivate_rule(rule_id)


@handle_api_errors
def _core_admin_list_layers(svc: RoutingApplicationService) -> list[MapLayerListItemDTO]:
    return svc.admin_list_map_layers()


@handle_api_errors
def _core_admin_request_kml(svc: RoutingApplicationService, body: RequestKmlImportInputDTO) -> Any:
    return svc.admin_request_kml_import(body)


@handle_api_errors
def _core_admin_get_import_job(svc: RoutingApplicationService, import_job_id: UUID) -> Any:
    return svc.admin_get_map_import_job(str(import_job_id))


@handle_api_errors
def _core_admin_publish_layer(
    svc: RoutingApplicationService,
    layer_id: UUID,
) -> MapLayerListItemDTO | None:
    return svc.admin_publish_map_layer(layer_id)


_EX_APP = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
_EX_RR = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
_EX_RP = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
_EX_CAND = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
_EX_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
_EX_TS2 = datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 申請人端（6.4 Applicant）— 與既有 prefix 銜接
# ---------------------------------------------------------------------------

routing_applicant_router = APIRouter(
    prefix="/api/v1/applicant/applications",
    tags=["路線與限制（申請人）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@routing_applicant_router.post(
    "/{application_id}/route-request",
    summary="建立路線申請",
    description="UC-ROUTE-01：寫入路線申請、地理編碼、回傳請求狀態。",
    responses=combine_responses(
        success_response(
            RouteRequestStatusDTO(
                route_request_id=_EX_RR,
                application_id=_EX_APP,
                status="planning_queued",
                origin_text="範例起點",
                destination_text="範例終點",
                geocode_failure_reason=None,
                requested_departure_at=None,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(400, "RoutingValidationAppError", "Invalid input", "輸入驗證失敗"),
        error_response(422, "RoutingAppError", "Unprocessable", "業務規則錯誤"),
    ),
)
async def post_route_request(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: CreateRouteRequestInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
    requested_by: UUID = Depends(get_applicant_user_id),
):
    """POST …/route-request"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_create_route_request(svc, application_id, body, requested_by)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_applicant_router.post(
    "/{application_id}/route-request/replan",
    summary="重新申請路線",
    description="以新路線條件建立申請（新 route_request 列）。",
    responses=combine_responses(
        success_response(
            RouteRequestStatusDTO(
                route_request_id=_EX_RR,
                application_id=_EX_APP,
                status="planning_queued",
                origin_text="範例",
                destination_text="範例",
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(422, "RoutingAppError", "Unprocessable", "業務規則錯誤"),
    ),
)
async def post_route_request_replan(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: CreateRouteRequestInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
    requested_by: UUID = Depends(get_applicant_user_id),
):
    """POST …/route-request/replan"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_replan_route_request(svc, application_id, body, requested_by)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_applicant_router.get(
    "/{application_id}/route-preview",
    summary="路線申請預覽狀態",
    description="回傳最新路線申請狀態；尚無申請時回 200 且 data 為 null（避免客戶端將空狀態當成 HTTP 錯誤）。",
    responses=combine_responses(
        success_response(
            RouteRequestStatusDTO(
                route_request_id=_EX_RR,
                application_id=_EX_APP,
                status="planning_queued",
                origin_text="範例起點",
                destination_text="範例終點",
            ).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_route_preview(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    """GET …/route-preview"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_get_route_preview(svc, application_id)
        if out is None:
            return routing_api_response(None, request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


# ---------------------------------------------------------------------------
# 審查端（6.4 Review）
# ---------------------------------------------------------------------------

routing_review_router = APIRouter(
    prefix="/api/v1/review/applications",
    tags=["路線與限制（審查）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@routing_review_router.get(
    "/{application_id}/route-plan",
    summary="取得路線規劃詳情",
    description="UC-ROUTE-03：最新 route plan 讀模型；尚無規劃時回 200 且 data 為 null（承辦可改按「重新規劃」）。",
    responses=combine_responses(
        success_response(
            RoutePlanDetailDTO(
                route_plan_id=_EX_RP,
                application_id=_EX_APP,
                route_request_id=_EX_RR,
                status="candidates_ready",
                planning_version="plan-example",
                map_version="2026.1",
                selected_candidate_id=None,
                candidates=[],
                no_route=None,
            ).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_route_plan(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_get_route_plan(svc, application_id)
        if out is None:
            return routing_api_response(None, request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_review_router.post(
    "/{application_id}/route-plan/select-candidate",
    summary="選定候選路線",
    description="UC-ROUTE-04。",
    responses=combine_responses(
        success_response(
            RoutePlanDetailDTO(
                route_plan_id=_EX_RP,
                application_id=_EX_APP,
                route_request_id=_EX_RR,
                status="candidate_selected",
                planning_version="plan-example",
                map_version="2026.1",
                selected_candidate_id=_EX_CAND,
                candidates=[],
                no_route=None,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(400, "RoutingValidationAppError", "Invalid", "候選不屬於本案"),
        error_response(409, "RoutingConflictAppError", "Conflict", "狀態不允許"),
    ),
)
async def post_select_candidate(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: SelectCandidateInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_select_candidate(svc, application_id, body)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_review_router.post(
    "/{application_id}/route-plan/override",
    summary="人工改線",
    description="UC-ROUTE-05：寫入 officer override 並更新計畫狀態。",
    responses=combine_responses(
        success_response(
            RoutePlanDetailDTO(
                route_plan_id=_EX_RP,
                application_id=_EX_APP,
                route_request_id=_EX_RR,
                status="officer_adjusted",
                planning_version="plan-example",
                map_version="2026.1",
                selected_candidate_id=None,
                candidates=[],
                no_route=None,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(400, "RoutingValidationAppError", "Invalid WKT", "幾何或輸入錯誤"),
    ),
)
async def post_route_plan_override(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: OfficerOverrideInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
    officer_user_id: UUID = Depends(get_applicant_user_id),
):
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_officer_override(svc, application_id, body, officer_user_id)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_review_router.post(
    "/{application_id}/route-plan/replan",
    summary="重新自動規劃",
    description="再執行 UC-ROUTE-02；回傳新 route_plan_id。",
    responses=combine_responses(
        success_response(
            RoutePlanCreatedOutputDTO(route_plan_id=_EX_RP).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "無法規劃"),
    ),
)
async def post_route_plan_replan(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        rid = _core_review_replan(svc, application_id)
        return routing_api_response(RoutePlanCreatedOutputDTO(route_plan_id=rid), request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_review_router.get(
    "/{application_id}/route-plan/rule-hits",
    summary="規則命中列表",
    description="最新計畫下各候選之規則命中彙整；尚無計畫時回 200 且 data 為 null。",
    responses=combine_responses(
        success_response(
            RouteRuleHitQueryDTO(route_plan_id=_EX_RP, hits=[]).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_route_plan_rule_hits(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_rule_hits(svc, application_id)
        if out is None:
            return routing_api_response(None, request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


# ---------------------------------------------------------------------------
# 管理端（6.4 Admin）
# ---------------------------------------------------------------------------

routing_admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["路線與限制（管理）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@routing_admin_router.get(
    "/restrictions/rules",
    summary="列出限制規則",
    responses=combine_responses(
        success_response(
            [
                RestrictionRuleListItemDTO(
                    rule_id=_EX_RR,
                    layer_id=_EX_APP,
                    rule_name="範例",
                    rule_type="forbidden_zone",
                    weight_limit_ton=None,
                    priority=100,
                    is_active=True,
                    updated_at=_EX_TS,
                ).model_dump(mode="json")
            ],
            "成功",
        ),
    ),
)
async def get_admin_restrictions_rules(
    request: Request,
    layer_id: UUID | None = Query(None, description="篩選圖資 layer"),
    is_active: bool | None = Query(None, description="篩選是否啟用"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_admin_list_rules(svc, layer_id, is_active)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.get(
    "/restrictions/rules/{rule_id}",
    summary="取得單筆限制規則",
    responses=combine_responses(
        success_response(
            RestrictionRuleDetailDTO(
                rule_id=_EX_RR,
                layer_id=_EX_APP,
                rule_name="範例",
                rule_type="forbidden_zone",
                weight_limit_ton=None,
                direction=None,
                time_rule_text=None,
                effective_from=None,
                effective_to=None,
                priority=100,
                is_active=True,
                created_at=_EX_TS,
                updated_at=_EX_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "規則不存在"),
    ),
)
async def get_admin_restriction_rule(
    request: Request,
    rule_id: UUID = Path(..., description="規則 UUID（規格：ruleId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path, rule_id=str(rule_id))
        out = _core_admin_get_rule(svc, rule_id)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("規則不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.post(
    "/restrictions/rules",
    summary="建立限制規則",
    responses=combine_responses(
        success_response(
            RestrictionRuleDetailDTO(
                rule_id=_EX_RR,
                layer_id=_EX_APP,
                rule_name="新規則",
                rule_type="warning_zone",
                weight_limit_ton=None,
                direction=None,
                time_rule_text=None,
                effective_from=None,
                effective_to=None,
                priority=100,
                is_active=True,
                created_at=_EX_TS,
                updated_at=_EX_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(422, "RoutingAppError", "Unprocessable", "建立失敗"),
    ),
)
async def post_admin_restriction_rule(
    request: Request,
    body: CreateRestrictionRuleInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path)
        out = _core_admin_create_rule(svc, body)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.patch(
    "/restrictions/rules/{rule_id}",
    summary="部分更新限制規則",
    responses=combine_responses(
        success_response(
            RestrictionRuleDetailDTO(
                rule_id=_EX_RR,
                layer_id=_EX_APP,
                rule_name="更新後",
                rule_type="forbidden_zone",
                weight_limit_ton=None,
                direction=None,
                time_rule_text="備註",
                effective_from=None,
                effective_to=None,
                priority=99,
                is_active=True,
                created_at=_EX_TS,
                updated_at=_EX_TS2,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "規則不存在"),
    ),
)
async def patch_admin_restriction_rule(
    request: Request,
    rule_id: UUID = Path(..., description="規則 UUID（規格：ruleId）"),
    body: PatchRestrictionRuleInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("PATCH", request.url.path, rule_id=str(rule_id))
        out = _core_admin_patch_rule(svc, rule_id, body)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("規則不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.post(
    "/restrictions/rules/{rule_id}/activate",
    summary="啟用限制規則",
    responses=combine_responses(
        success_response(
            RestrictionRuleDetailDTO(
                rule_id=_EX_RR,
                layer_id=_EX_APP,
                rule_name="範例",
                rule_type="forbidden_zone",
                weight_limit_ton=None,
                direction=None,
                time_rule_text=None,
                effective_from=None,
                effective_to=None,
                priority=100,
                is_active=True,
                created_at=_EX_TS,
                updated_at=_EX_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "規則不存在"),
    ),
)
async def post_admin_rule_activate(
    request: Request,
    rule_id: UUID = Path(..., description="規則 UUID（規格：ruleId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path, rule_id=str(rule_id))
        out = _core_admin_activate_rule(svc, rule_id)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("規則不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.post(
    "/restrictions/rules/{rule_id}/deactivate",
    summary="停用限制規則",
    responses=combine_responses(
        success_response(
            RestrictionRuleDetailDTO(
                rule_id=_EX_RR,
                layer_id=_EX_APP,
                rule_name="範例",
                rule_type="forbidden_zone",
                weight_limit_ton=None,
                direction=None,
                time_rule_text=None,
                effective_from=None,
                effective_to=None,
                priority=100,
                is_active=False,
                created_at=_EX_TS,
                updated_at=_EX_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "規則不存在"),
    ),
)
async def post_admin_rule_deactivate(
    request: Request,
    rule_id: UUID = Path(..., description="規則 UUID（規格：ruleId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path, rule_id=str(rule_id))
        out = _core_admin_deactivate_rule(svc, rule_id)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("規則不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.get(
    "/map-layers",
    summary="列出圖資 layer",
    responses=combine_responses(
        success_response(
            [
                MapLayerListItemDTO(
                    layer_id=_EX_APP,
                    layer_code="demo",
                    layer_name="示範",
                    version_no="1.0",
                    is_active=False,
                    published_at=None,
                ).model_dump(mode="json")
            ],
            "成功",
        ),
    ),
)
async def get_admin_map_layers(
    request: Request,
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_admin_list_layers(svc)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.post(
    "/map-imports/kml",
    summary="請求 KML 匯入",
    description="UC-ROUTE-06：同步建立 ops.import_jobs 並寫入 map_layers／restriction_rules／geometries。",
    responses=combine_responses(
        success_response(
            MapImportJobStatusDTO(
                import_job_id=_EX_RR,
                status="succeeded",
                message='{"layer_id":"…"}',
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(400, "RoutingValidationAppError", "Bad request", "來源無效或匯入失敗"),
    ),
)
async def post_admin_map_import_kml(
    request: Request,
    body: RequestKmlImportInputDTO = Body(...),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path)
        out = _core_admin_request_kml(svc, body)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.get(
    "/map-imports/{import_job_id}",
    summary="查詢匯入作業狀態",
    responses=combine_responses(
        success_response(
            MapImportJobStatusDTO(
                import_job_id=_EX_RR,
                status="pending",
                message=None,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "作業不存在"),
    ),
)
async def get_admin_map_import_job(
    request: Request,
    import_job_id: UUID = Path(..., description="匯入作業 UUID（規格：importJobId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("GET", request.url.path, import_job_id=str(import_job_id))
        out = _core_admin_get_import_job(svc, import_job_id)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("匯入作業不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)


@routing_admin_router.post(
    "/map-layers/{layer_id}/publish",
    summary="發布圖資 layer",
    responses=combine_responses(
        success_response(
            MapLayerListItemDTO(
                layer_id=_EX_APP,
                layer_code="demo",
                layer_name="示範",
                version_no="1.0",
                is_active=True,
                published_at=_EX_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "RoutingNotFoundAppError", "Not found", "layer 不存在"),
    ),
)
async def post_admin_map_layer_publish(
    request: Request,
    layer_id: UUID = Path(..., description="圖資 layer UUID（規格：layerId）"),
    svc: RoutingApplicationService = Depends(get_routing_application_service),
):
    try:
        logger.api_info("POST", request.url.path, layer_id=str(layer_id))
        out = _core_admin_publish_layer(svc, layer_id)
        if out is None:
            return routing_api_response(RoutingNotFoundAppError("圖資 layer 不存在", None), request)
        return routing_api_response(out, request)
    except Exception as e:
        return routing_api_response(e, request)
