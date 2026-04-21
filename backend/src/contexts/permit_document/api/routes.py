"""
Permit_Document — HTTP 路由（規格 8.4）。

規範對照（API 層）：
- **shared.api**：OpenAPI 範例僅透過 `combine_responses`／`success_response`／`error_response`（`shared.api.responses`）；
  執行時回應經 **permit_api_response** → `shared.api.api_response_with_logging`，信封為 `{data, error}`。
- **shared.decorators.error_handler**：用例本體置於掛 `@handle_api_errors` 之 `_core_*` 同步函式，與 Review／Routing 等 context 一致。
- **應用層 DTO**：`Path`／`Body`／回傳型別僅引用 `permit_document.app.dtos`，本檔不另建 Pydantic 請求／回應模型。
- **路徑**：與 8.4 一致；Python 參數為 snake_case，`Path(description=…)` 標註規格 **applicationId**／**permitId**／**documentId**。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Request

from src.contexts.permit_document.api.dependencies import (
    PermitApiBundle,
    get_permit_actor_user_id,
    get_permit_api_bundle,
)
from src.contexts.permit_document.api.response_utils import permit_api_response
from src.contexts.permit_document.app.dtos import (
    ApplicantPermitDocumentDownloadBodyDTO,
    CreateDocumentDownloadUrlInputDTO,
    CreateDocumentDownloadUrlOutputDTO,
    GetPermitByApplicationQueryDTO,
    GetPermitByIdQueryDTO,
    ListPermitDocumentsOutputDTO,
    ListPermitDocumentsQueryDTO,
    PermitSummaryDTO,
    RequestDocumentRegenerationInputDTO,
    RequestDocumentRegenerationOutputDTO,
    RequestPermitDocumentDownloadByApplicationDTO,
)
from src.contexts.permit_document.app.errors import PermitNotFoundAppError
from shared.api import combine_responses, error_response, success_response
from shared.core.logger.logger import logger
from shared.decorators import handle_api_errors

# ---------------------------------------------------------------------------
# OpenAPI 範例常數（占位 UUID，與 seed 可對齊便於閱讀）
# ---------------------------------------------------------------------------

_EX_APP = UUID("11111111-1111-4111-8111-111111111101")
_EX_PERMIT = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01")
_EX_DOC = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddd01")
_TS_START = datetime(2026, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
_TS_END = datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc)


def _example_permit_summary_dict() -> dict:
    return {
        "permit_id": str(_EX_PERMIT),
        "permit_no": "P-SEED-00001",
        "application_id": str(_EX_APP),
        "status": "pending_generation",
        "approved_start_at": _TS_START.isoformat(),
        "approved_end_at": _TS_END.isoformat(),
        "route_summary_text": "（範例）正式路線摘要",
        "issued_at": None,
    }


def _example_document_row_dict() -> dict:
    return {
        "document_id": str(_EX_DOC),
        "permit_id": str(_EX_PERMIT),
        "application_id": str(_EX_APP),
        "document_type": "permit_certificate_pdf",
        "file_id": str(UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeee01")),
        "template_code": "permit_default_v1",
        "version_no": 1,
        "status": "pending",
    }


# ---------------------------------------------------------------------------
# 同步核心（@handle_api_errors）
# ---------------------------------------------------------------------------


@handle_api_errors
def _core_get_permit_by_application(
    bundle: PermitApiBundle,
    *,
    application_id: UUID,
    actor_user_id: UUID,
) -> PermitSummaryDTO:
    return bundle.p_qry.get_permit_by_application(
        GetPermitByApplicationQueryDTO(
            application_id=application_id,
            actor_user_id=actor_user_id,
        )
    )


@handle_api_errors
def _core_post_applicant_permit_download_url(
    bundle: PermitApiBundle,
    *,
    application_id: UUID,
    body: ApplicantPermitDocumentDownloadBodyDTO,
    actor_user_id: UUID,
) -> CreateDocumentDownloadUrlOutputDTO:
    return bundle.p_qry.create_document_download_url_by_application(
        RequestPermitDocumentDownloadByApplicationDTO(
            application_id=application_id,
            document_id=body.document_id,
            actor_user_id=actor_user_id,
        )
    )


@handle_api_errors
def _core_get_permit_by_id(
    bundle: PermitApiBundle,
    *,
    permit_id: UUID,
    actor_user_id: UUID,
) -> PermitSummaryDTO:
    return bundle.p_qry.get_permit_by_id(
        GetPermitByIdQueryDTO(permit_id=permit_id, actor_user_id=actor_user_id)
    )


@handle_api_errors
def _core_list_permit_documents(
    bundle: PermitApiBundle,
    *,
    permit_id: UUID,
    actor_user_id: UUID,
) -> ListPermitDocumentsOutputDTO:
    return bundle.p_qry.list_documents(
        ListPermitDocumentsQueryDTO(permit_id=permit_id, actor_user_id=actor_user_id)
    )


@handle_api_errors
def _core_post_permit_document_download_url(
    bundle: PermitApiBundle,
    *,
    permit_id: UUID,
    document_id: UUID,
    actor_user_id: UUID,
) -> CreateDocumentDownloadUrlOutputDTO:
    return bundle.p_qry.create_document_download_url(
        CreateDocumentDownloadUrlInputDTO(
            permit_id=permit_id,
            document_id=document_id,
            actor_user_id=actor_user_id,
        )
    )


@handle_api_errors
def _core_post_regenerate(
    bundle: PermitApiBundle,
    *,
    application_id: UUID,
    actor_user_id: UUID,
) -> RequestDocumentRegenerationOutputDTO:
    return bundle.p_cmd.request_document_regeneration(
        RequestDocumentRegenerationInputDTO(
            application_id=application_id,
            actor_user_id=actor_user_id,
        )
    )


# ---------------------------------------------------------------------------
# 路由器（8.4）
# ---------------------------------------------------------------------------

permit_applicant_router = APIRouter(
    prefix="/api/v1/applicant/applications",
    tags=["許可證與文件（申請人）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@permit_applicant_router.get(
    "/{application_id}/permit",
    summary="依申請案取得許可證摘要",
    description=(
        "UC-PERMIT-03：申請人讀取與其案件綁定之許可證摘要；"
        "若尚未建立許可則回 200 且 data 為 null（空狀態不當成 HTTP 錯誤）。"
    ),
    responses=combine_responses(
        success_response(_example_permit_summary_dict(), "成功"),
        error_response(403, "PermitForbiddenAppError", "Forbidden", "無權存取該申請"),
    ),
)
async def get_applicant_application_permit(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """GET /api/v1/applicant/applications/{applicationId}/permit"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_get_permit_by_application(
            bundle,
            application_id=application_id,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except PermitNotFoundAppError:
        return permit_api_response(None, request)
    except Exception as e:
        return permit_api_response(e, request)


@permit_applicant_router.post(
    "/{application_id}/permit/download-url",
    summary="申請人：請求許可文件下載網址",
    description=(
        "UC-PERMIT-03：依申請案定位許可後，為指定文件產生短期下載 URL。"
        "請求體可省略 document_id，將自動選定預設可下載文件（優先通行證主檔）。"
        "若文件尚在產製（pending）則回 400，而非簽發無效網址。"
    ),
    responses=combine_responses(
        success_response(
            {
                "download_url": "http://127.0.0.1:8000/api/v1/stored-files/{fileId}/download?expires=…&sig=…",
                "expires_at": _TS_END.isoformat(),
            },
            "成功",
        ),
        error_response(400, "PermitValidationAppError", "Not ready", "文件產製中或尚不可下載"),
        error_response(404, "PermitNotFoundAppError", "Not found", "許可或文件不存在"),
        error_response(403, "PermitForbiddenAppError", "Forbidden", "無權下載"),
    ),
)
async def post_applicant_application_permit_download_url(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: ApplicantPermitDocumentDownloadBodyDTO = Body(default_factory=ApplicantPermitDocumentDownloadBodyDTO),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """POST /api/v1/applicant/applications/{applicationId}/permit/download-url"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_post_applicant_permit_download_url(
            bundle,
            application_id=application_id,
            body=body,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except Exception as e:
        return permit_api_response(e, request)


permit_resource_router = APIRouter(
    prefix="/api/v1/permits",
    tags=["許可證與文件（資源）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@permit_resource_router.get(
    "/{permit_id}",
    summary="依許可識別取得摘要",
    description="UC-PERMIT-03：讀取單一許可證摘要（需通過授權埠校驗）。",
    responses=combine_responses(
        success_response(_example_permit_summary_dict(), "成功"),
        error_response(404, "PermitNotFoundAppError", "Not found", "許可證不存在"),
        error_response(403, "PermitForbiddenAppError", "Forbidden", "無權存取該許可"),
    ),
)
async def get_permit_by_id(
    request: Request,
    permit_id: UUID = Path(..., description="許可證 UUID（規格：permitId）"),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """GET /api/v1/permits/{permitId}"""
    try:
        logger.api_info("GET", request.url.path, permit_id=str(permit_id))
        out = _core_get_permit_by_id(
            bundle,
            permit_id=permit_id,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except Exception as e:
        return permit_api_response(e, request)


@permit_resource_router.get(
    "/{permit_id}/documents",
    summary="列出許可底下文件版本",
    description="UC-PERMIT-03：回傳 **ListPermitDocumentsOutputDTO**（含文件列清單）。",
    responses=combine_responses(
        success_response(
            {
                "permit_id": str(_EX_PERMIT),
                "documents": [_example_document_row_dict()],
            },
            "成功",
        ),
        error_response(404, "PermitNotFoundAppError", "Not found", "許可證不存在"),
    ),
)
async def list_permit_documents(
    request: Request,
    permit_id: UUID = Path(..., description="許可證 UUID（規格：permitId）"),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """GET /api/v1/permits/{permitId}/documents"""
    try:
        logger.api_info("GET", request.url.path, permit_id=str(permit_id))
        out = _core_list_permit_documents(
            bundle,
            permit_id=permit_id,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except Exception as e:
        return permit_api_response(e, request)


@permit_resource_router.post(
    "/{permit_id}/documents/{document_id}/download-url",
    summary="請求單一文件之短期下載 URL",
    description="UC-PERMIT-03：校驗文件隸屬該許可後，經物件儲存埠簽發下載鏈結。",
    responses=combine_responses(
        success_response(
            {
                "download_url": "http://127.0.0.1:8000/api/v1/stored-files/{fileId}/download?expires=…&sig=…",
                "expires_at": _TS_END.isoformat(),
                "file_name": "P-SEED-00001_v1.pdf",
            },
            "成功",
        ),
        error_response(404, "PermitNotFoundAppError", "Not found", "文件不存在或不屬於該許可"),
    ),
)
async def post_permit_document_download_url(
    request: Request,
    permit_id: UUID = Path(..., description="許可證 UUID（規格：permitId）"),
    document_id: UUID = Path(..., description="文件列 UUID（規格：documentId）"),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """POST /api/v1/permits/{permitId}/documents/{documentId}/download-url"""
    try:
        logger.api_info(
            "POST",
            request.url.path,
            permit_id=str(permit_id),
            document_id=str(document_id),
        )
        out = _core_post_permit_document_download_url(
            bundle,
            permit_id=permit_id,
            document_id=document_id,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except Exception as e:
        return permit_api_response(e, request)


permit_application_regenerate_router = APIRouter(
    prefix="/api/v1/applications",
    tags=["許可證與文件（申請／補產）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@permit_application_regenerate_router.post(
    "/{application_id}/permit/regenerate",
    summary="請求重產許可相關文件",
    description="觸發文件重產工作單；已核發時標示待補產狀態（詳見領域規則）。",
    responses=combine_responses(
        success_response(
            {
                "permit_id": str(_EX_PERMIT),
                "new_document_job_id": str(UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa01")),
                "permit_status": "issued_pending_document_regen",
            },
            "成功",
        ),
        error_response(404, "PermitNotFoundAppError", "Not found", "此申請尚無許可證"),
        error_response(409, "PermitConflictAppError", "Conflict", "目前狀態不允許重產"),
    ),
)
async def post_application_permit_regenerate(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    actor_user_id: UUID = Depends(get_permit_actor_user_id),
):
    """POST /api/v1/applications/{applicationId}/permit/regenerate"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_post_regenerate(
            bundle,
            application_id=application_id,
            actor_user_id=actor_user_id,
        )
        return permit_api_response(out, request)
    except Exception as e:
        return permit_api_response(e, request)
