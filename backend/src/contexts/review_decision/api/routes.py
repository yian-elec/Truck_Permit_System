"""
Review_Decision — HTTP 路由（規格 7.4）。

規範對照（API 層審查）：
- **shared.api**：Swagger 範例僅透過 `combine_responses`／`success_response`／`error_response`（`shared.api.responses`）；
  執行時回應一律經 `review_api_response` → `shared.api.api_response_with_logging`，信封為 `{data, error}`。
- **shared.decorators.error_handler**：業務用例同步函式皆掛 `@handle_api_errors`（`handle_api_errors` 定義於
  `shared/decorators/error_handler.py`）；路由層 `try/except` 將例外再交 `review_api_response` 與專案其他 context 一致。
- **應用層 DTO**：`Body`／回傳型別僅引用 `review_decision.app.dtos`；跨 context 之附件預覽輸出沿用
  `application.app.dtos.DownloadUrlOutputDTO`，本檔不另建輸入輸出模型。
- **路徑**：REST 路徑與 7.4 一致（`/api/v1/review/...`）；Python 參數為 snake_case，`Path(description=…)` 標註規格 `applicationId` 等。

說明：GET `/applications/{application_id}` 之 200 回應體為信封內 `data`＝`ReviewPageOutputDTO`；OpenAPI 僅標示常見錯誤範例，
  避免在文件中嵌入過大巢狀範例（與 Application 路由未使用 `response_model` 之做法一致）。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, Request

from src.contexts.application.app.dtos import DownloadUrlOutputDTO
from src.contexts.permit_document.api.dependencies import (
    PermitApiBundle,
    get_permit_api_bundle,
)
from src.contexts.permit_document.app.dtos.permit_command_dtos import CreatePermitInputDTO
from src.contexts.permit_document.app.errors import PermitConflictAppError
from src.contexts.review_decision.api.dependencies import (
    ReviewApiBundle,
    get_officer_user_id,
    get_review_api_bundle,
)
from src.contexts.review_decision.api.response_utils import review_api_response
from src.contexts.review_decision.app.dtos import (
    AddCommentInputDTO,
    AddCommentOutputDTO,
    ApproveApplicationInputDTO,
    ApproveApplicationOutputDTO,
    AssignReviewTaskInputDTO,
    AssignReviewTaskOutputDTO,
    AuditTrailEntryDTO,
    CommentSummaryDTO,
    DecisionSummaryDTO,
    RejectApplicationInputDTO,
    RejectApplicationOutputDTO,
    RequestSupplementInputDTO,
    RequestSupplementOutputDTO,
    ReviewDashboardDTO,
    ReviewOcrSummaryDTO,
    ReviewPageOutputDTO,
    ReviewTaskSummaryDTO,
)
from shared.api import combine_responses, error_response, success_response
from shared.core.logger.logger import logger
from shared.decorators import handle_api_errors

# ---------------------------------------------------------------------------
# OpenAPI 範例用常數（與 seed 無關之占位 UUID）
# ---------------------------------------------------------------------------

_EX_APP = UUID("11111111-1111-4111-8111-111111111101")
_EX_TASK = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa01")
_EX_COMMENT = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05")
_TS = datetime(2026, 4, 7, 0, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 同步核心（@handle_api_errors）
# ---------------------------------------------------------------------------


@handle_api_errors
def _core_list_tasks(bundle: ReviewApiBundle, *, limit: int, offset: int) -> list[ReviewTaskSummaryDTO]:
    return bundle.r_q.list_tasks(limit=limit, offset=offset)


@handle_api_errors
def _core_dashboard(bundle: ReviewApiBundle) -> ReviewDashboardDTO:
    return bundle.r_q.get_dashboard()


@handle_api_errors
def _core_review_page(bundle: ReviewApiBundle, application_id: UUID) -> ReviewPageOutputDTO:
    return bundle.r_q.get_review_page(application_id)


@handle_api_errors
def _core_assign(
    bundle: ReviewApiBundle,
    application_id: UUID,
    body: AssignReviewTaskInputDTO,
) -> AssignReviewTaskOutputDTO:
    return bundle.r_cmd.assign_task_for_application(application_id, body)


@handle_api_errors
def _core_add_comment(
    bundle: ReviewApiBundle,
    application_id: UUID,
    body: AddCommentInputDTO,
    author_user_id: UUID,
) -> AddCommentOutputDTO:
    return bundle.r_cmd.add_comment(application_id, body, author_user_id=author_user_id)


@handle_api_errors
def _core_list_comments(
    bundle: ReviewApiBundle,
    application_id: UUID,
) -> list[CommentSummaryDTO]:
    return bundle.r_q.list_comments(application_id)


@handle_api_errors
def _core_attachment_preview(
    bundle: ReviewApiBundle,
    application_id: UUID,
    attachment_id: UUID,
) -> DownloadUrlOutputDTO:
    return bundle.app_cmd.get_attachment_download_url(
        application_id,
        attachment_id,
        applicant_user_id=None,
    )


@handle_api_errors
def _core_ocr_summary(bundle: ReviewApiBundle, application_id: UUID) -> ReviewOcrSummaryDTO:
    return bundle.r_q.get_ocr_summary_for_application(application_id)


@handle_api_errors
def _core_supplement(
    bundle: ReviewApiBundle,
    application_id: UUID,
    body: RequestSupplementInputDTO,
    officer_user_id: UUID,
) -> RequestSupplementOutputDTO:
    return bundle.r_cmd.request_supplement(application_id, body, officer_user_id=officer_user_id)


@handle_api_errors
def _core_approve(
    bundle: ReviewApiBundle,
    application_id: UUID,
    body: ApproveApplicationInputDTO,
    officer_user_id: UUID,
) -> ApproveApplicationOutputDTO:
    return bundle.r_cmd.approve_application(application_id, body, officer_user_id=officer_user_id)


@handle_api_errors
def _core_reject(
    bundle: ReviewApiBundle,
    application_id: UUID,
    body: RejectApplicationInputDTO,
    officer_user_id: UUID,
) -> RejectApplicationOutputDTO:
    return bundle.r_cmd.reject_application(application_id, body, officer_user_id=officer_user_id)


@handle_api_errors
def _core_list_decisions(
    bundle: ReviewApiBundle,
    application_id: UUID,
) -> list[DecisionSummaryDTO]:
    return bundle.r_q.list_decisions(application_id)


@handle_api_errors
def _core_audit_trail(
    bundle: ReviewApiBundle,
    application_id: UUID,
) -> list[AuditTrailEntryDTO]:
    return bundle.r_q.get_audit_trail(application_id)


# ---------------------------------------------------------------------------
# 路由器（7.4）
# ---------------------------------------------------------------------------

review_decision_router = APIRouter(
    prefix="/api/v1/review",
    tags=["審查與決策"],
    responses=error_response(
        500,
        "InternalServerError",
        "Internal server error",
        "內部伺服器錯誤",
    ),
)


@review_decision_router.get(
    "/tasks",
    summary="審查任務列表",
    description="UC 對應承辦工作台：分頁列出審查任務。",
    responses=combine_responses(
        success_response(
            [
                ReviewTaskSummaryDTO(
                    review_task_id=_EX_TASK,
                    application_id=_EX_APP,
                    stage="initial",
                    status="pending",
                    assignee_user_id=None,
                    due_at=None,
                    created_at=_TS,
                    updated_at=_TS,
                ).model_dump(mode="json")
            ],
            "成功",
        ),
        error_response(400, "ReviewValidationAppError", "Invalid", "參數錯誤"),
    ),
)
async def list_review_tasks(
    request: Request,
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
    limit: int = Query(50, ge=1, le=500, description="每頁筆數"),
    offset: int = Query(0, ge=0, description="位移"),
):
    """GET /api/v1/review/tasks"""
    try:
        logger.api_info("GET", request.url.path, limit=str(limit), offset=str(offset))
        out = _core_list_tasks(bundle, limit=limit, offset=offset)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/dashboard",
    summary="審查儀表板",
    description="彙總開放任務、待分派、審查中與視窗內已關閉任務筆數（初版實作）。",
    responses=combine_responses(
        success_response(
            ReviewDashboardDTO(
                total_open_tasks=1,
                pending_assignment_tasks=0,
                in_review_tasks=1,
                closed_tasks_in_window=0,
            ).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_review_dashboard(
    request: Request,
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/dashboard"""
    try:
        logger.api_info("GET", request.url.path)
        out = _core_dashboard(bundle)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}",
    summary="審核頁聚合模型",
    description="UC-REV-02：案件明細、路線快照、決策／評論／補件歷史等。",
    responses=combine_responses(
        error_response(404, "ApplicationNotFoundAppError", "Not found", "案件不存在"),
        error_response(422, "ApplicationAppError", "Unprocessable", "讀取模型失敗"),
    ),
)
async def get_review_application_page(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/applications/{applicationId}"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_review_page(bundle, application_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.post(
    "/applications/{application_id}/assign",
    summary="分派審查任務",
    description="將該案件目前開放中之審查任務指派給承辦人員。",
    responses=combine_responses(
        success_response(
            AssignReviewTaskOutputDTO(
                review_task_id=_EX_TASK,
                assignee_user_id=_EX_APP,
                status="in_review",
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "ReviewNotFoundAppError", "No open task", "無開放中任務"),
    ),
)
async def assign_review_task(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: AssignReviewTaskInputDTO = Body(...),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """POST /api/v1/review/applications/{applicationId}/assign"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_assign(bundle, application_id, body)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.post(
    "/applications/{application_id}/comments",
    summary="新增審查評論",
    description="UC-REV-06：internal／supplement／decision_note；權限由 JWT 與後續政策擴充。",
    responses=combine_responses(
        success_response(
            AddCommentOutputDTO(
                comment_id=_EX_COMMENT,
                application_id=_EX_APP,
                comment_type="internal",
                created_at=_TS,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(400, "ReviewValidationAppError", "Invalid", "輸入不合法"),
    ),
)
async def post_review_comment(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: AddCommentInputDTO = Body(...),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
    officer_user_id: UUID = Depends(get_officer_user_id),
):
    """POST /api/v1/review/applications/{applicationId}/comments"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_add_comment(bundle, application_id, body, officer_user_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}/comments",
    summary="列出審查評論",
    description="依時間序回傳該案件之評論。",
    responses=combine_responses(
        success_response(
            [
                CommentSummaryDTO(
                    comment_id=_EX_COMMENT,
                    application_id=_EX_APP,
                    comment_type="internal",
                    content="（範例）",
                    created_by=_EX_APP,
                    created_at=_TS,
                ).model_dump(mode="json")
            ],
            "成功",
        ),
    ),
)
async def list_review_comments(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/applications/{applicationId}/comments"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_list_comments(bundle, application_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}/attachments/{attachment_id}/preview",
    summary="附件預覽下載網址",
    description="委派 Application 用例產生限期下載 URL（承辦讀取，不校驗申請人）。",
    responses=combine_responses(
        success_response(
            DownloadUrlOutputDTO(
                download_url="https://storage.example.invalid/preview",
                expires_at=None,
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(404, "ApplicationNotFoundAppError", "Not found", "附件不存在"),
    ),
)
async def get_attachment_preview_url(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    attachment_id: UUID = Path(..., description="附件 UUID（規格：attachmentId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET …/attachments/{attachmentId}/preview"""
    try:
        logger.api_info(
            "GET",
            request.url.path,
            application_id=str(application_id),
            attachment_id=str(attachment_id),
        )
        out = _core_attachment_preview(bundle, application_id, attachment_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}/ocr-summary",
    summary="OCR 彙總",
    description="回傳與審核頁一致之 OCR 摘要欄位（初版可為空物件）。",
    responses=combine_responses(
        success_response(
            ReviewOcrSummaryDTO(application_id=_EX_APP, ocr_summary={}).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def get_ocr_summary(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/applications/{applicationId}/ocr-summary"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_ocr_summary(bundle, application_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.post(
    "/applications/{application_id}/supplement",
    summary="發出補件",
    description="UC-REV-03：補件請求、決策紀錄、案件狀態、評論與通知。",
    responses=combine_responses(
        success_response(
            RequestSupplementOutputDTO(
                supplement_request_id=_EX_COMMENT,
                decision_id=_EX_TASK,
                application_status="supplement_required",
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(409, "ReviewConflictAppError", "Conflict", "狀態或歷史衝突"),
    ),
)
async def post_supplement_request(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: RequestSupplementInputDTO = Body(...),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
    officer_user_id: UUID = Depends(get_officer_user_id),
):
    """POST /api/v1/review/applications/{applicationId}/supplement"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_supplement(bundle, application_id, body, officer_user_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.post(
    "/applications/{application_id}/approve",
    summary="核准案件",
    description="UC-REV-04：校驗路線與核准期間、寫入決策、更新案件、關閉任務並發布事件。",
    responses=combine_responses(
        success_response(
            ApproveApplicationOutputDTO(
                decision_id=_EX_TASK,
                application_status="approved",
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(422, "ReviewAppError", "Rule violation", "規則不符"),
    ),
)
async def post_approve_application(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: ApproveApplicationInputDTO = Body(...),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
    permit_bundle: PermitApiBundle = Depends(get_permit_api_bundle),
    officer_user_id: UUID = Depends(get_officer_user_id),
):
    """POST /api/v1/review/applications/{applicationId}/approve"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_approve(bundle, application_id, body, officer_user_id)
        try:
            permit_bundle.p_cmd.create_permit_after_application_approved(
                CreatePermitInputDTO(application_id=application_id)
            )
        except PermitConflictAppError:
            # 已核發過（重試／重送）時略過，仍回傳核准結果
            pass
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.post(
    "/applications/{application_id}/reject",
    summary="駁回案件",
    description="UC-REV-05：駁回決策、更新案件、關閉任務與通知。",
    responses=combine_responses(
        success_response(
            RejectApplicationOutputDTO(
                decision_id=_EX_TASK,
                application_status="rejected",
            ).model_dump(mode="json"),
            "成功",
        ),
    ),
)
async def post_reject_application(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    body: RejectApplicationInputDTO = Body(...),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
    officer_user_id: UUID = Depends(get_officer_user_id),
):
    """POST /api/v1/review/applications/{applicationId}/reject"""
    try:
        logger.api_info("POST", request.url.path, application_id=str(application_id))
        out = _core_reject(bundle, application_id, body, officer_user_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}/decisions",
    summary="決策歷史",
    description="列出該案件之審查決策紀錄。",
    responses=combine_responses(
        success_response(
            [
                DecisionSummaryDTO(
                    decision_id=_EX_TASK,
                    application_id=_EX_APP,
                    decision_type="supplement",
                    selected_candidate_id=None,
                    override_id=None,
                    approved_start_at=None,
                    approved_end_at=None,
                    reason="（範例）",
                    decided_by=_EX_APP,
                    decided_at=_TS,
                    created_at=_TS,
                ).model_dump(mode="json")
            ],
            "成功",
        ),
    ),
)
async def list_application_decisions(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/applications/{applicationId}/decisions"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_list_decisions(bundle, application_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)


@review_decision_router.get(
    "/applications/{application_id}/audit-trail",
    summary="稽核軌跡",
    description="合併決策、評論與案件狀態歷程，依時間排序。",
    responses=combine_responses(
        success_response(
            [
                AuditTrailEntryDTO(
                    entry_type="decision",
                    occurred_at=_TS,
                    payload={"decision_id": str(_EX_TASK)},
                ).model_dump(mode="json")
            ],
            "成功",
        ),
    ),
)
async def get_application_audit_trail(
    request: Request,
    application_id: UUID = Path(..., description="案件 UUID（規格：applicationId）"),
    bundle: ReviewApiBundle = Depends(get_review_api_bundle),
):
    """GET /api/v1/review/applications/{applicationId}/audit-trail"""
    try:
        logger.api_info("GET", request.url.path, application_id=str(application_id))
        out = _core_audit_trail(bundle, application_id)
        return review_api_response(out, request)
    except Exception as e:
        return review_api_response(e, request)
