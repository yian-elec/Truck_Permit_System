"""
Page_Model_Query_Aggregation — HTTP 路由（規格 11 畫面專用 Page Model API）。

規範對照（API 層）：
- **shared.api**：OpenAPI 範例僅透過 `combine_responses`／`success_response`／`error_response`；
  執行時回應經 **page_model_api_response** → `shared.api.api_response_with_logging`，信封為 `{data, error}`。
- **shared.decorators.error_handler**：用例本體置於掛 `@handle_api_errors` 之 `_core_*` 同步函式。
- **應用層 DTO**：輸入以 Path／Query 組裝 **app.dtos** 已定義之 dataclass；回傳型別為 **PageModelQueryResultDTO**，
  本檔不另建 Pydantic 請求／回應模型取代 DTO 結構。
- **路徑**：`applicationId` 於 `Path(description=…)` 註明與 OpenAPI 之對應；Python 參數為 snake_case `application_id`。
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Request

from src.contexts.page_model_query_aggregation.api.dependencies import (
    get_page_model_admin_user_id,
    get_page_model_applicant_user_id,
    get_page_model_officer_user_id,
    get_page_model_query_application_service,
)
from src.contexts.page_model_query_aggregation.api.response_utils import page_model_api_response
from src.contexts.page_model_query_aggregation.app.dtos.page_model_dtos import (
    AdminDashboardPageInputDTO,
    ApplicantApplicationEditorInputDTO,
    ApplicantApplicationHomeInputDTO,
    PageModelQueryResultDTO,
    ReviewApplicationPageInputDTO,
)
from src.contexts.page_model_query_aggregation.app.services import PageModelQueryApplicationService
from shared.api import combine_responses, error_response, success_response
from shared.core.logger.logger import logger
from shared.decorators import handle_api_errors

# ---------------------------------------------------------------------------
# OpenAPI 範例（結構與 app DTO 欄位一致，供 Swagger 由 shared/api 統一產生）
# ---------------------------------------------------------------------------

_EX_APP = UUID("11111111-1111-4111-8111-111111111101")


def _example_section(code: str, order: int, required: bool, roles: list[str]) -> dict:
    return {
        "section_code": code,
        "sort_order": order,
        "is_required_for_render": required,
        "feed_roles": roles,
        "prerequisite_section_codes": [],
    }


def _example_home_page_model_dict() -> dict:
    return {
        "page_kind": "applicant_application_home",
        "contract_version_major": 1,
        "application_id": None,
        "sections": [
            _example_section("applicant.home.service_overview", 0, True, ["public_service_copy"]),
            _example_section("applicant.home.user_account", 1, True, ["user_account_summary"]),
            _example_section("applicant.home.my_applications", 2, True, ["my_applications_summary"]),
            _example_section("applicant.home.ops_activity_snapshot", 3, False, ["ops_activity_feed"]),
        ],
        "payload_by_section": {},
    }


def _example_editor_page_model_dict() -> dict:
    return {
        "page_kind": "applicant_application_editor",
        "contract_version_major": 1,
        "application_id": str(_EX_APP),
        "sections": [
            _example_section("applicant.editor.case_core", 0, True, ["application_case_core"]),
            _example_section("applicant.editor.vehicles", 1, True, ["application_vehicles"]),
            _example_section("applicant.editor.attachments", 2, True, ["application_attachments"]),
            _example_section("applicant.editor.routing", 3, True, ["routing_request_and_plans"]),
        ],
        "payload_by_section": {},
    }


def _example_review_page_model_dict() -> dict:
    return {
        "page_kind": "review_application",
        "contract_version_major": 1,
        "application_id": str(_EX_APP),
        "sections": [
            _example_section("review.application.case_readonly", 0, True, ["application_case_core"]),
            _example_section("review.application.routing_readonly", 1, True, ["routing_request_and_plans"]),
            _example_section("review.application.review_workspace", 2, True, ["review_tasks_and_decisions"]),
            _example_section("review.application.permit_readonly", 3, False, ["permit_documents"]),
        ],
        "payload_by_section": {},
    }


def _example_admin_dashboard_dict() -> dict:
    return {
        "page_kind": "admin_dashboard",
        "contract_version_major": 1,
        "application_id": None,
        "sections": [
            _example_section("admin.dashboard.metrics", 0, True, ["admin_metrics_aggregate"]),
            _example_section("admin.dashboard.ops_feed", 1, True, ["ops_activity_feed"]),
        ],
        "payload_by_section": {},
    }


# ---------------------------------------------------------------------------
# 同步核心（@handle_api_errors）— 回傳應用層 DTO
# ---------------------------------------------------------------------------


@handle_api_errors
def _core_get_applicant_application_home_model(
    svc: PageModelQueryApplicationService,
    *,
    actor_user_id: UUID,
) -> PageModelQueryResultDTO:
    return svc.get_applicant_application_home_model(
        ApplicantApplicationHomeInputDTO(actor_user_id=actor_user_id),
    )


@handle_api_errors
def _core_get_applicant_application_editor_model(
    svc: PageModelQueryApplicationService,
    *,
    actor_user_id: UUID,
    application_id: UUID,
    lifecycle_phase: str,
    has_active_route_plan: bool,
    has_pending_supplement_request: bool,
    has_issued_permit_documents: bool,
) -> PageModelQueryResultDTO:
    return svc.get_applicant_application_editor_model(
        ApplicantApplicationEditorInputDTO(
            actor_user_id=actor_user_id,
            application_id=application_id,
            lifecycle_phase=lifecycle_phase,
            has_active_route_plan=has_active_route_plan,
            has_pending_supplement_request=has_pending_supplement_request,
            has_issued_permit_documents=has_issued_permit_documents,
        ),
    )


@handle_api_errors
def _core_get_review_application_page_model(
    svc: PageModelQueryApplicationService,
    *,
    actor_user_id: UUID,
    application_id: UUID,
    include_permit_section: bool,
) -> PageModelQueryResultDTO:
    return svc.get_review_application_page_model(
        ReviewApplicationPageInputDTO(
            actor_user_id=actor_user_id,
            application_id=application_id,
            include_permit_section=include_permit_section,
        ),
    )


@handle_api_errors
def _core_get_admin_dashboard_page_model(
    svc: PageModelQueryApplicationService,
    *,
    actor_user_id: UUID,
) -> PageModelQueryResultDTO:
    return svc.get_admin_dashboard_page_model(
        AdminDashboardPageInputDTO(actor_user_id=actor_user_id),
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

page_model_applicant_router = APIRouter(
    prefix="/api/v1/applicant/pages",
    tags=["畫面 Page Model（申請人）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@page_model_applicant_router.get(
    "/application-home-model",
    summary="申請人首頁 Page Model",
    description="聚合首頁所需區塊契約（服務導覽、帳號、我的案件、Ops 摘要等），減少前端多次請求。",
    responses=combine_responses(
        success_response(_example_home_page_model_dict(), "成功"),
        error_response(400, "BadRequest", "Invalid", "參數錯誤"),
        error_response(401, "Unauthorized", "Unauthorized", "未授權"),
        error_response(422, "UnprocessableEntity", "Unprocessable", "處理失敗"),
    ),
)
async def get_applicant_application_home_model(
    request: Request,
    actor_user_id: UUID = Depends(get_page_model_applicant_user_id),
    svc: PageModelQueryApplicationService = Depends(get_page_model_query_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_get_applicant_application_home_model(svc, actor_user_id=actor_user_id)
        return page_model_api_response(out, request)
    except Exception as e:
        return page_model_api_response(e, request)


@page_model_applicant_router.get(
    "/applications/{application_id}/editor-model",
    summary="申請人案件編輯器 Page Model",
    description="依案件識別與生命週期快照組出編輯器區塊契約；lifecycle 等查詢參數須與 Application 狀態對齊。",
    responses=combine_responses(
        success_response(_example_editor_page_model_dict(), "成功"),
        error_response(400, "BadRequest", "Invalid", "參數錯誤"),
        error_response(401, "Unauthorized", "Unauthorized", "未授權"),
        error_response(422, "UnprocessableEntity", "Unprocessable", "處理失敗"),
    ),
)
async def get_applicant_application_editor_model(
    request: Request,
    application_id: UUID = Path(
        ...,
        description="申請案件識別（規格路徑參數 **applicationId**）",
    ),
    lifecycle_phase: str = Query(
        ...,
        description="申請生命週期階段（對應 Application 狀態字串，如 draft、supplement_required）",
    ),
    has_active_route_plan: bool = Query(False, description="是否已有可展示之路線方案"),
    has_pending_supplement_request: bool = Query(False, description="是否有待處理補件"),
    has_issued_permit_documents: bool = Query(False, description="是否已有許可／文件關聯"),
    actor_user_id: UUID = Depends(get_page_model_applicant_user_id),
    svc: PageModelQueryApplicationService = Depends(get_page_model_query_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_get_applicant_application_editor_model(
            svc,
            actor_user_id=actor_user_id,
            application_id=application_id,
            lifecycle_phase=lifecycle_phase,
            has_active_route_plan=has_active_route_plan,
            has_pending_supplement_request=has_pending_supplement_request,
            has_issued_permit_documents=has_issued_permit_documents,
        )
        return page_model_api_response(out, request)
    except Exception as e:
        return page_model_api_response(e, request)


page_model_review_router = APIRouter(
    prefix="/api/v1/review/pages",
    tags=["畫面 Page Model（審查）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@page_model_review_router.get(
    "/applications/{application_id}/review-model",
    summary="審查員案件審查 Page Model",
    description="聚合審查工作臺所需唯讀案件、路徑、審查工作區與可選許可區塊契約。",
    responses=combine_responses(
        success_response(_example_review_page_model_dict(), "成功"),
        error_response(400, "BadRequest", "Invalid", "參數錯誤"),
        error_response(401, "Unauthorized", "Unauthorized", "未授權"),
        error_response(422, "UnprocessableEntity", "Unprocessable", "處理失敗"),
    ),
)
async def get_review_application_page_model(
    request: Request,
    application_id: UUID = Path(
        ...,
        description="申請案件識別（規格路徑參數 **applicationId**）",
    ),
    include_permit_section: bool = Query(
        True,
        description="是否包含許可／文件唯讀區塊（核准前可為空 payload）",
    ),
    actor_user_id: UUID = Depends(get_page_model_officer_user_id),
    svc: PageModelQueryApplicationService = Depends(get_page_model_query_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_get_review_application_page_model(
            svc,
            actor_user_id=actor_user_id,
            application_id=application_id,
            include_permit_section=include_permit_section,
        )
        return page_model_api_response(out, request)
    except Exception as e:
        return page_model_api_response(e, request)


page_model_admin_router = APIRouter(
    prefix="/api/v1/admin/pages",
    tags=["畫面 Page Model（管理）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@page_model_admin_router.get(
    "/dashboard-model",
    summary="管理者儀表板 Page Model",
    description="聚合儀表板指標與 Ops 活動區塊契約；實際數值由後續 orchestration 填入 payload_by_section。",
    responses=combine_responses(
        success_response(_example_admin_dashboard_dict(), "成功"),
        error_response(401, "Unauthorized", "Unauthorized", "未授權"),
        error_response(422, "UnprocessableEntity", "Unprocessable", "處理失敗"),
    ),
)
async def get_admin_dashboard_page_model(
    request: Request,
    actor_user_id: UUID = Depends(get_page_model_admin_user_id),
    svc: PageModelQueryApplicationService = Depends(get_page_model_query_application_service),
):
    try:
        logger.api_info("GET", request.url.path)
        out = _core_get_admin_dashboard_page_model(svc, actor_user_id=actor_user_id)
        return page_model_api_response(out, request)
    except Exception as e:
        return page_model_api_response(e, request)
