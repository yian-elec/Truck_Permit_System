"""
Application context — HTTP 路由（公開服務 + 申請人案件 API）。

責任：
- 路徑與動詞對齊規格 5.4；請求／回應本體**僅使用** `app.dtos` 已定義之 Pydantic 模型
- 呼叫 `ApplicationCommandService`／`PublicHeavyTruckPermitService`，不寫業務規則
- 回應經 `application_api_response`（內部呼叫 `shared.api.api_response_with_logging`）包裝為 `{data, error}`；
  成功時 Pydantic 以 `model_dump(mode="json")` 確保 UUID 等可 JSON 序列化

錯誤處理：各端點以 try/except 捕獲例外後交 `application_api_response` 序列化（與 User API 相同之 try/except 模式）。
**規範對照**：`integration_operations/api/routes` 另將同步呼叫包在 `@handle_api_errors` 之 `_core_*` 函式，
使非 `BaseError` 先轉為 `SystemError`；本模組尚未採用該模式，若需與 Ops 完全一致可再重構。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.contexts.application.app.dtos import (
    AddVehicleInputDTO,
    ApplicationDetailDTO,
    ApplicationEditModelDTO,
    ApplicationSummaryDTO,
    ApplicationSummaryListDTO,
    AttachmentListDTO,
    CompleteAttachmentUploadInputDTO,
    CreateDraftApplicationInputDTO,
    CreateDraftApplicationOutputDTO,
    DeleteAckDTO,
    DownloadUrlOutputDTO,
    PatchApplicationRequestDTO,
    PatchVehicleInputDTO,
    PresignedUploadUrlOutputDTO,
    RequestUploadUrlInputDTO,
    SubmissionCheckResultDTO,
    SubmitApplicationOutputDTO,
    SupplementRequestListDTO,
    SupplementResponseInputDTO,
    SupplementResponseOutputDTO,
    TimelineListDTO,
    VehicleListDTO,
)
from src.contexts.application.app.dtos.public_service_dtos import (
    ConsentLatestDTO,
    HandlingUnitsListDTO,
    HeavyTruckPermitServiceOverviewDTO,
    RequiredDocumentsListDTO,
)
from src.contexts.application.app.errors import ApplicationNotFoundAppError
from src.contexts.application.app.services import (
    ApplicationCommandService,
    PublicHeavyTruckPermitService,
)
from src.contexts.application.api.dependencies import (
    get_application_command_service,
    get_applicant_user_id,
)
from shared.api.responses import combine_responses, error_response, success_response
from shared.core.logger.logger import logger

from src.contexts.application.api.response_utils import application_api_response

# ---------------------------------------------------------------------------
# 公開 API（無需 JWT；中介軟體已排除 /api/v1/public）
# ---------------------------------------------------------------------------

public_heavy_truck_router = APIRouter(
    prefix="/api/v1/public/services/heavy-truck-permit",
    tags=["重型貨車通行證（公開）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@public_heavy_truck_router.get(
    "",
    summary="重型貨車通行證服務總覽",
    description="公開服務說明與代碼，供入口頁／導覽使用。",
    responses=combine_responses(
        success_response(
            HeavyTruckPermitServiceOverviewDTO().model_dump(mode="json"),
            "成功",
        ),
        error_response(422, "ValidationError", "Invalid", "參數錯誤"),
    ),
)
async def get_heavy_truck_permit_overview(request: Request) -> object:
    """GET /api/v1/public/services/heavy-truck-permit"""
    try:
        logger.api_info("GET", request.url.path)
        data = PublicHeavyTruckPermitService.get_service_overview()
        return application_api_response(data, request)
    except Exception as e:
        logger.api_error("PublicHeavyTruckOverviewError", str(e))
        return application_api_response(e, request)


@public_heavy_truck_router.get(
    "/consent/latest",
    summary="最新同意條款摘要",
    description="回傳目前生效之條款版本與摘要；全文由前端另載。",
    responses=combine_responses(
        success_response(
            ConsentLatestDTO(
                version="2026-04-01",
                effective_at="2026-04-01",
                summary="（範例）",
                must_accept_before_submit=True,
            ).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_consent_latest(request: Request) -> object:
    """GET .../consent/latest"""
    try:
        logger.api_info("GET", request.url.path)
        return application_api_response(
            PublicHeavyTruckPermitService.get_consent_latest(),
            request,
        )
    except Exception as e:
        logger.api_error("ConsentLatestError", str(e))
        return application_api_response(e, request)


@public_heavy_truck_router.get(
    "/required-documents",
    summary="必備文件清單",
    description="與申請草稿 checklist 範本一致之必備項目代碼與名稱。",
    responses=combine_responses(
        success_response(
            RequiredDocumentsListDTO().model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_required_documents(request: Request) -> object:
    """GET .../required-documents"""
    try:
        logger.api_info("GET", request.url.path)
        return application_api_response(
            PublicHeavyTruckPermitService.list_required_documents(),
            request,
        )
    except Exception as e:
        logger.api_error("RequiredDocumentsError", str(e))
        return application_api_response(e, request)


@public_heavy_truck_router.get(
    "/handling-units",
    summary="受理單位資訊",
    description="公開之承辦／受理窗口聯絡方式（示範資料）。",
    responses=combine_responses(
        success_response(
            HandlingUnitsListDTO().model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_handling_units(request: Request) -> object:
    """GET .../handling-units"""
    try:
        logger.api_info("GET", request.url.path)
        return application_api_response(
            PublicHeavyTruckPermitService.list_handling_units(),
            request,
        )
    except Exception as e:
        logger.api_error("HandlingUnitsError", str(e))
        return application_api_response(e, request)


# ---------------------------------------------------------------------------
# 申請人 API（需 JWT；路徑與 5.4 Applicant 對齊）
# ---------------------------------------------------------------------------

applicant_applications_router = APIRouter(
    prefix="/api/v1/applicant/applications",
    tags=["重型貨車通行證（申請人）"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@applicant_applications_router.post(
    "",
    summary="建立草稿案件",
    description="UC-APP-01：建立 status=draft、初始化 checklist。",
    responses=combine_responses(
        success_response(
            CreateDraftApplicationOutputDTO(
                application_id=UUID("00000000-0000-4000-8000-000000000001"),
                application_no="HTP-EXAMPLE",
                status="draft",
            ).model_dump(mode="json"),
            "建立成功",
        ),
        error_response(422, "ApplicationAppError", "Business rule violation", "業務規則錯誤"),
    ),
)
async def post_create_application(
    request: Request,
    body: CreateDraftApplicationInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """POST /api/v1/applicant/applications"""
    try:
        logger.api_info("POST", request.url.path)
        out = svc.create_draft(body, applicant_user_id=applicant_user_id)
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("CreateApplicationError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "",
    summary="我的申請案件列表",
    responses=combine_responses(
        success_response(
            ApplicationSummaryListDTO(
                applications=[
                    ApplicationSummaryDTO(
                        application_id=UUID("00000000-0000-4000-8000-000000000001"),
                        application_no="HTP-EXAMPLE",
                        status="draft",
                        applicant_type="individual",
                        updated_at=datetime(
                            2026, 4, 7, 12, 0, 0, tzinfo=timezone.utc
                        ),
                    ),
                ],
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(401, "MissingTokenError", "Unauthorized", "未授權"),
    ),
)
async def get_my_applications(
    request: Request,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
    limit: int = 100,
) -> object:
    """GET /api/v1/applicant/applications"""
    try:
        logger.api_info("GET", request.url.path)
        rows = svc.list_applications_for_applicant(applicant_user_id, limit=limit)
        return application_api_response(
            ApplicationSummaryListDTO(applications=rows),
            request,
        )
    except Exception as e:
        logger.api_error("ListApplicationsError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}",
    summary="取得單一案件明細",
    responses=combine_responses(
        error_response(404, "ApplicationNotFoundAppError", "Not found", "案件不存在"),
    ),
)
async def get_application_detail(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """GET /api/v1/applicant/applications/{applicationId}"""
    try:
        logger.api_info("GET", request.url.path)
        out: ApplicationDetailDTO = svc.get_application(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("GetApplicationError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/edit-model",
    summary="取得編輯用模型",
    description="與明細結構對齊，供表單綁定。",
)
async def get_application_edit_model(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """GET .../edit-model"""
    try:
        logger.api_info("GET", request.url.path)
        return application_api_response(
            svc.get_edit_model(application_id, applicant_user_id=applicant_user_id),
            request,
        )
    except Exception as e:
        logger.api_error("GetEditModelError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.patch(
    "/{application_id}",
    summary="更新草稿／可編輯資料",
    description="UC-APP-02：可併送主表 patch 與申請人／公司 profiles。",
)
async def patch_application(
    request: Request,
    application_id: UUID,
    body: PatchApplicationRequestDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """PATCH /api/v1/applicant/applications/{applicationId}"""
    try:
        logger.api_info("PATCH", request.url.path)
        out = svc.update_draft_application(
            application_id,
            patch=body.patch,
            profiles=body.profiles,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("PatchApplicationError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/consent",
    summary="記錄已同意條款",
)
async def post_consent(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """POST .../consent"""
    try:
        logger.api_info("POST", request.url.path)
        return application_api_response(
            svc.record_consent(application_id, applicant_user_id=applicant_user_id),
            request,
        )
    except Exception as e:
        logger.api_error("RecordConsentError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/vehicles",
    summary="新增車輛",
    description="UC-APP-03",
)
async def post_vehicle(
    request: Request,
    application_id: UUID,
    body: AddVehicleInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """POST .../vehicles"""
    try:
        logger.api_info("POST", request.url.path)
        vehicles = svc.add_vehicle(
            application_id,
            body,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(VehicleListDTO(vehicles=vehicles), request)
    except Exception as e:
        logger.api_error("AddVehicleError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.patch(
    "/{application_id}/vehicles/{vehicle_id}",
    summary="更新車輛",
)
async def patch_vehicle(
    request: Request,
    application_id: UUID,
    vehicle_id: UUID,
    body: PatchVehicleInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """PATCH .../vehicles/{vehicleId}"""
    try:
        logger.api_info("PATCH", request.url.path)
        vehicles = svc.update_vehicle(
            application_id,
            vehicle_id,
            body,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(VehicleListDTO(vehicles=vehicles), request)
    except Exception as e:
        logger.api_error("UpdateVehicleError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.delete(
    "/{application_id}/vehicles/{vehicle_id}",
    summary="刪除車輛",
)
async def delete_vehicle(
    request: Request,
    application_id: UUID,
    vehicle_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    """DELETE .../vehicles/{vehicleId}"""
    try:
        logger.api_info("DELETE", request.url.path)
        svc.remove_vehicle(
            application_id,
            vehicle_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(DeleteAckDTO(), request)
    except Exception as e:
        logger.api_error("RemoveVehicleError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/attachments/upload-url",
    summary="取得附件上傳 Presigned URL",
    description="UC-APP-04：取得上傳網址與 object_key。",
)
async def post_attachment_upload_url(
    request: Request,
    application_id: UUID,
    body: RequestUploadUrlInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("POST", request.url.path)
        out = svc.create_attachment_upload_url(
            application_id,
            body,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("AttachmentUploadUrlError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/attachments/complete",
    summary="附件上傳完成回報",
    description="寫入 stored_files 與 application.attachments。",
)
async def post_attachment_complete(
    request: Request,
    application_id: UUID,
    body: CompleteAttachmentUploadInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("POST", request.url.path)
        out = svc.complete_attachment_upload(
            application_id,
            body,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("AttachmentCompleteError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/attachments",
    summary="附件列表",
)
async def get_attachments(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("GET", request.url.path)
        items = svc.list_attachments(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(
            AttachmentListDTO(attachments=items),
            request,
        )
    except Exception as e:
        logger.api_error("ListAttachmentsError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/attachments/{attachment_id}",
    summary="取得單一附件摘要",
)
async def get_one_attachment(
    request: Request,
    application_id: UUID,
    attachment_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("GET", request.url.path)
        items = svc.list_attachments(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        match = next((a for a in items if a.attachment_id == attachment_id), None)
        if match is None:
            return application_api_response(
                ApplicationNotFoundAppError(
                    "附件不存在",
                    details={"attachment_id": str(attachment_id)},
                ),
                request,
            )
        return application_api_response(match, request)
    except Exception as e:
        logger.api_error("GetAttachmentError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.delete(
    "/{application_id}/attachments/{attachment_id}",
    summary="刪除附件",
)
async def delete_attachment(
    request: Request,
    application_id: UUID,
    attachment_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("DELETE", request.url.path)
        svc.delete_attachment(
            application_id,
            attachment_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(DeleteAckDTO(), request)
    except Exception as e:
        logger.api_error("DeleteAttachmentError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/attachments/{attachment_id}/download-url",
    summary="取得附件下載 Presigned URL",
)
async def post_attachment_download_url(
    request: Request,
    application_id: UUID,
    attachment_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("POST", request.url.path)
        out: DownloadUrlOutputDTO = svc.get_attachment_download_url(
            application_id,
            attachment_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("AttachmentDownloadUrlError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/submission-check",
    summary="送件前檢查",
    description="UC-APP-05",
)
async def get_submission_check(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("GET", request.url.path)
        out: SubmissionCheckResultDTO = svc.submission_check(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("SubmissionCheckError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/submit",
    summary="送件",
    description="UC-APP-06；未通過檢查時回傳業務錯誤。",
)
async def post_submit(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("POST", request.url.path)
        out: SubmitApplicationOutputDTO = svc.submit_application(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("SubmitApplicationError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/supplement-requests",
    summary="補件要求列表",
)
async def get_supplement_requests(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("GET", request.url.path)
        items = svc.list_supplement_requests(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(
            SupplementRequestListDTO(items=items),
            request,
        )
    except Exception as e:
        logger.api_error("ListSupplementRequestsError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.post(
    "/{application_id}/supplement-response",
    summary="回覆補件",
    description="UC-APP-07",
)
async def post_supplement_response(
    request: Request,
    application_id: UUID,
    body: SupplementResponseInputDTO,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("POST", request.url.path)
        out: SupplementResponseOutputDTO = svc.supplement_response(
            application_id,
            body,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(out, request)
    except Exception as e:
        logger.api_error("SupplementResponseError", str(e))
        return application_api_response(e, request)


@applicant_applications_router.get(
    "/{application_id}/timeline",
    summary="案件時間軸",
    description="狀態歷程列表。",
)
async def get_timeline(
    request: Request,
    application_id: UUID,
    svc: ApplicationCommandService = Depends(get_application_command_service),
    applicant_user_id: UUID = Depends(get_applicant_user_id),
) -> object:
    try:
        logger.api_info("GET", request.url.path)
        entries = svc.get_timeline(
            application_id,
            applicant_user_id=applicant_user_id,
        )
        return application_api_response(
            TimelineListDTO(entries=entries),
            request,
        )
    except Exception as e:
        logger.api_error("TimelineError", str(e))
        return application_api_response(e, request)
