"""
Integration_Operations — Ops 唯讀 API 路由（對應規格 9.4）。

審查要點（與專案規範對齊）：
- **shared/api**：回應包裝僅使用 `api_response_with_logging`；OpenAPI 範例僅使用
  `success_response` / `error_response` / `combine_responses`（由 `shared.api` 統一匯出）。
- **shared.decorators.error_handler**：實際讀取邏輯置於同步函式，並以 `handle_api_errors`
  統一攔截非 `BaseError` 之例外並轉為 `SystemError`；`BaseError` 維持原樣上拋，
  再由路由層 `api_response_with_logging` 轉成 JSON 信封（與 User API 一致）。
- **應用層 DTO**：請求／回應資料模型僅來自 `app.dtos`；本檔另含 `OpsListPagination`
  僅作 HTTP 分頁查詢參數聚合，非業務輸入輸出 DTO。
- **路徑命名**：URL 採 kebab-case（`/ocr-jobs`）；路徑變數為 snake_case（`ocr_job_id`），
  與 OpenAPI／Python 慣例一致；規格中的 `ocrJobId`／`importJobId` 於 `Path(description=…)` 註明對應關係。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Request

from src.contexts.integration_operations.app.dtos import (
    AuditLogListItemDTO,
    ImportJobDetailDTO,
    ImportJobListItemDTO,
    NotificationJobListItemDTO,
    OcrJobDetailDTO,
    OcrJobListItemDTO,
)
from src.contexts.integration_operations.app.services import OpsQueryApplicationService
from src.contexts.integration_operations.infra.repositories import OpsReadRepositoryImpl
from shared.api import (
    api_response_with_logging,
    combine_responses,
    error_response,
    success_response,
)
from shared.core.logger.logger import logger
from shared.decorators import handle_api_errors


def get_ops_query_application_service() -> OpsQueryApplicationService:
    """注入唯讀查詢應用服務（實際環境可改由 DI 容器提供）。"""
    return OpsQueryApplicationService(OpsReadRepositoryImpl())


@dataclass(frozen=True)
class OpsListPagination:
    """
    HTTP 列表分頁查詢參數（非應用層 DTO）。

    僅供路由層聚合 `limit`／`offset`，避免六個端點重複宣告相同 Query。
    """

    limit: int
    offset: int


def get_ops_list_pagination(
    limit: int = Query(50, ge=1, le=200, description="每頁筆數（1–200）"),
    offset: int = Query(0, ge=0, description="略過筆數"),
) -> OpsListPagination:
    return OpsListPagination(limit=limit, offset=offset)


def _serialize_dto_list(items: list[Any]) -> list[dict[str, Any]]:
    return [m.model_dump(mode="json") for m in items]


def _serialize_dto(item: Any) -> dict[str, Any]:
    return item.model_dump(mode="json")


# ---------------------------------------------------------------------------
# 讀取核心（同步 + handle_api_errors）：與 decorators/error_handler 規範一致
# ---------------------------------------------------------------------------


@handle_api_errors
def _core_list_ocr_jobs(svc: OpsQueryApplicationService, pag: OpsListPagination) -> list[dict[str, Any]]:
    rows = svc.list_ocr_jobs(limit=pag.limit, offset=pag.offset)
    return _serialize_dto_list(rows)


@handle_api_errors
def _core_get_ocr_job(svc: OpsQueryApplicationService, ocr_job_id: UUID) -> dict[str, Any]:
    detail = svc.get_ocr_job(ocr_job_id)
    return _serialize_dto(detail)


@handle_api_errors
def _core_list_notification_jobs(svc: OpsQueryApplicationService, pag: OpsListPagination) -> list[dict[str, Any]]:
    rows = svc.list_notification_jobs(limit=pag.limit, offset=pag.offset)
    return _serialize_dto_list(rows)


@handle_api_errors
def _core_list_import_jobs(svc: OpsQueryApplicationService, pag: OpsListPagination) -> list[dict[str, Any]]:
    rows = svc.list_import_jobs(limit=pag.limit, offset=pag.offset)
    return _serialize_dto_list(rows)


@handle_api_errors
def _core_get_import_job(svc: OpsQueryApplicationService, import_job_id: UUID) -> dict[str, Any]:
    detail = svc.get_import_job(import_job_id)
    return _serialize_dto(detail)


@handle_api_errors
def _core_list_audit_logs(svc: OpsQueryApplicationService, pag: OpsListPagination) -> list[dict[str, Any]]:
    rows = svc.list_audit_logs(limit=pag.limit, offset=pag.offset)
    return _serialize_dto_list(rows)


router = APIRouter(
    prefix="/api/v1/ops",
    tags=["作業整合（Ops）"],
    responses=error_response(500, "InternalServerError", "Internal server error", "內部伺服器錯誤"),
)


def _ops_json_response(request: Request, payload_or_error: Any):
    """統一成功資料或例外 → JSONResponse（信封格式由 shared.api 定義）。"""
    return api_response_with_logging(payload_or_error, request)


@router.get(
    "/ocr-jobs",
    summary="列出 OCR 作業",
    description="分頁列出 `ops.ocr_jobs`；回傳結構與 `OcrJobListItemDTO` 一致。",
    response_description="data 為 OCR 作業摘要陣列",
    responses=combine_responses(
        success_response(
            [
                OcrJobListItemDTO(
                    ocr_job_id=UUID("00000000-0000-4000-8000-000000000001"),
                    attachment_id=UUID("00000000-0000-4000-8000-000000000002"),
                    provider_code="example",
                    status="pending",
                    started_at=None,
                    finished_at=None,
                    error_message=None,
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-01T00:00:00Z",
                ).model_dump(mode="json")
            ],
            "查詢成功",
        ),
        error_response(422, "ValidationError", "Invalid query parameters", "查詢參數驗證失敗"),
    ),
)
async def list_ocr_jobs(
    request: Request,
    pag: OpsListPagination = Depends(get_ops_list_pagination),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/ocr-jobs"""
    try:
        logger.api_info("GET", "/api/v1/ops/ocr-jobs", limit=str(pag.limit), offset=str(pag.offset))
        return _ops_json_response(request, _core_list_ocr_jobs(svc, pag))
    except Exception as e:
        return _ops_json_response(request, e)


@router.get(
    "/ocr-jobs/{ocr_job_id}",
    summary="取得單筆 OCR 作業詳情",
    description="含同附件之辨識結果列表；回傳 `OcrJobDetailDTO`。",
    responses=combine_responses(
        success_response(
            OcrJobDetailDTO(
                job=OcrJobListItemDTO(
                    ocr_job_id=UUID("00000000-0000-4000-8000-000000000001"),
                    attachment_id=UUID("00000000-0000-4000-8000-000000000002"),
                    provider_code="example",
                    status="succeeded",
                    started_at="2026-01-01T00:00:00Z",
                    finished_at="2026-01-01T00:01:00Z",
                    error_message=None,
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-01T00:01:00Z",
                ),
                results=[],
            ).model_dump(mode="json"),
            "查詢成功",
        ),
        error_response(404, "OpsResourceNotFoundError", "OCR job not found", "作業不存在"),
    ),
)
async def get_ocr_job(
    request: Request,
    ocr_job_id: UUID = Path(..., description="OCR 作業 UUID（規格路徑參數名：ocrJobId）"),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/ocr-jobs/{ocrJobId}"""
    try:
        logger.api_info("GET", f"/api/v1/ops/ocr-jobs/{ocr_job_id}")
        return _ops_json_response(request, _core_get_ocr_job(svc, ocr_job_id))
    except Exception as e:
        return _ops_json_response(request, e)


@router.get(
    "/notification-jobs",
    summary="列出通知作業",
    description="分頁列出 `ops.notification_jobs`；元素型別為 `NotificationJobListItemDTO`。",
    responses=combine_responses(
        success_response(
            [
                NotificationJobListItemDTO(
                    notification_job_id=UUID("00000000-0000-4000-8000-000000000003"),
                    channel="email",
                    recipient="user@example.com",
                    template_code="permit_submitted",
                    status="pending",
                    sent_at=None,
                    error_message=None,
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-01T00:00:00Z",
                ).model_dump(mode="json")
            ],
            "查詢成功",
        ),
        error_response(422, "ValidationError", "Invalid query parameters", "查詢參數驗證失敗"),
    ),
)
async def list_notification_jobs(
    request: Request,
    pag: OpsListPagination = Depends(get_ops_list_pagination),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/notification-jobs"""
    try:
        logger.api_info("GET", "/api/v1/ops/notification-jobs", limit=str(pag.limit), offset=str(pag.offset))
        return _ops_json_response(request, _core_list_notification_jobs(svc, pag))
    except Exception as e:
        return _ops_json_response(request, e)


@router.get(
    "/import-jobs",
    summary="列出匯入作業",
    description="分頁列出 `ops.import_jobs`；元素型別為 `ImportJobListItemDTO`。",
    responses=combine_responses(
        success_response(
            [
                ImportJobListItemDTO(
                    import_job_id=UUID("00000000-0000-4000-8000-000000000004"),
                    job_type="holiday",
                    source_name="gov_tw",
                    source_ref="2026Q1",
                    status="succeeded",
                    started_at="2026-01-01T00:00:00Z",
                    finished_at="2026-01-01T00:05:00Z",
                    result_summary="42 rows",
                    error_message=None,
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-01T00:05:00Z",
                ).model_dump(mode="json")
            ],
            "查詢成功",
        ),
        error_response(422, "ValidationError", "Invalid query parameters", "查詢參數驗證失敗"),
    ),
)
async def list_import_jobs(
    request: Request,
    pag: OpsListPagination = Depends(get_ops_list_pagination),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/import-jobs"""
    try:
        logger.api_info("GET", "/api/v1/ops/import-jobs", limit=str(pag.limit), offset=str(pag.offset))
        return _ops_json_response(request, _core_list_import_jobs(svc, pag))
    except Exception as e:
        return _ops_json_response(request, e)


@router.get(
    "/import-jobs/{import_job_id}",
    summary="取得單筆匯入作業詳情",
    description="回傳 `ImportJobDetailDTO`（目前為列表欄位之詳情包裝）。",
    responses=combine_responses(
        success_response(
            ImportJobDetailDTO(
                job=ImportJobListItemDTO(
                    import_job_id=UUID("00000000-0000-4000-8000-000000000004"),
                    job_type="holiday",
                    source_name="gov_tw",
                    source_ref=None,
                    status="pending",
                    started_at=None,
                    finished_at=None,
                    result_summary=None,
                    error_message=None,
                    created_at="2026-01-01T00:00:00Z",
                    updated_at="2026-01-01T00:00:00Z",
                )
            ).model_dump(mode="json"),
            "查詢成功",
        ),
        error_response(404, "OpsResourceNotFoundError", "import job not found", "作業不存在"),
    ),
)
async def get_import_job(
    request: Request,
    import_job_id: UUID = Path(..., description="匯入作業 UUID（規格路徑參數名：importJobId）"),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/import-jobs/{importJobId}"""
    try:
        logger.api_info("GET", f"/api/v1/ops/import-jobs/{import_job_id}")
        return _ops_json_response(request, _core_get_import_job(svc, import_job_id))
    except Exception as e:
        return _ops_json_response(request, e)


@router.get(
    "/audit-logs",
    summary="列出稽核紀錄",
    description="分頁列出 `ops.audit_logs`；元素型別為 `AuditLogListItemDTO`。",
    responses=combine_responses(
        success_response(
            [
                AuditLogListItemDTO(
                    audit_log_id=UUID("00000000-0000-4000-8000-000000000005"),
                    actor_user_id=None,
                    actor_type="system",
                    action_code="permit.submit",
                    resource_type="permit_application",
                    resource_id="pa-1",
                    before_json=None,
                    after_json={"status": "submitted"},
                    client_ip=None,
                    created_at="2026-01-01T00:00:00Z",
                ).model_dump(mode="json")
            ],
            "查詢成功",
        ),
        error_response(422, "ValidationError", "Invalid query parameters", "查詢參數驗證失敗"),
    ),
)
async def list_audit_logs(
    request: Request,
    pag: OpsListPagination = Depends(get_ops_list_pagination),
    svc: OpsQueryApplicationService = Depends(get_ops_query_application_service),
):
    """GET /api/v1/ops/audit-logs"""
    try:
        logger.api_info("GET", "/api/v1/ops/audit-logs", limit=str(pag.limit), offset=str(pag.offset))
        return _ops_json_response(request, _core_list_audit_logs(svc, pag))
    except Exception as e:
        return _ops_json_response(request, e)
