"""
routes.py — IAM Context API 層（對應規格 4.4）。

責任：
- 僅做 HTTP 邊界與依賴注入；請求／回應結構一律使用應用層 DTO。
- 成功與錯誤回應經 `shared.api.wrapper.api_response_with_logging` 包裝為統一信封 `{data, error}`。
- 成功回應經 `wrap_iam_use_case_response`：Pydantic 以 `model_dump(mode="json")` 再交 `api_response_with_logging`。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from shared.api.responses import combine_responses, error_response, success_response
from shared.core.logger.logger import logger
from shared.errors.system_error.auth_error import MissingTokenError

from src.contexts.iam.api.response_utils import wrap_iam_use_case_response

from src.contexts.iam.app.dtos.assign_role_dto import (
    AssignRoleInputDTO,
    AssignRoleOutputDTO,
    AssignRoleRequestBodyDTO,
)
from src.contexts.iam.app.dtos.auth_logout_dto import (
    IamLogoutInputDTO,
    IamLogoutOutputDTO,
    IamLogoutRequestBodyDTO,
)
from src.contexts.iam.app.dtos.auth_me_dto import IamMeOutputDTO
from src.contexts.iam.app.dtos.auth_permissions_dto import IamPermissionsOutputDTO
from src.contexts.iam.app.dtos.auth_refresh_dto import IamRefreshInputDTO, IamRefreshOutputDTO
from src.contexts.iam.app.dtos.login_iam_dto import LoginIamInputDTO, LoginIamOutputDTO
from src.contexts.iam.app.dtos.mfa_verify_dto import MfaVerifyInputDTO, MfaVerifyOutputDTO
from src.contexts.iam.app.dtos.register_applicant_dto import (
    RegisterApplicantInputDTO,
    RegisterApplicantOutputDTO,
)
from src.contexts.iam.app.errors import IamInputValidationError
from src.contexts.iam.app.services.service_factory import IamServiceFactory


router = APIRouter(
    prefix="/api/v1",
    tags=["IAM 認證與授權"],
    responses=error_response(500, "InternalServerError", "Internal server error", "內部伺服器錯誤"),
)


def get_iam_service_factory() -> IamServiceFactory:
    """FastAPI Depends：提供 IAM 用例工廠（可於此改為注入真實 MfaSender／JWT）。"""
    return IamServiceFactory()


def _jwt_user_id_to_uuid(request: Request) -> UUID:
    """自 `AuthMiddleware` 寫入之 `request.state.user` 解析 IAM 所需之 UUID subject。"""
    user = getattr(request.state, "user", None)
    if not user or user.get("user_id") is None:
        raise MissingTokenError("Authentication required")
    raw = user["user_id"]
    try:
        return UUID(str(raw))
    except (ValueError, TypeError) as exc:
        raise IamInputValidationError("IAM 需要 JWT sub 為 UUID 字串") from exc


def get_current_iam_user_uuid(request: Request) -> UUID:
    """Depends：當前請求對應之 IAM 使用者 UUID。"""
    return _jwt_user_id_to_uuid(request)


@router.post(
    "/auth/register",
    summary="註冊申請人（UC-IAM-01）",
    description="建立 applicant 帳戶並寫入密碼雜湊；Email／手機唯一性由應用層檢查。",
    responses=combine_responses(
        success_response(
            RegisterApplicantOutputDTO(
                user_id=UUID("00000000-0000-0000-0000-000000000001"),
                display_name="範例",
                email="user@example.com",
                mobile="0912000111",
                status="active",
            ).model_dump(mode="json"),
            "註冊成功",
        ),
        error_response(409, "IamEmailAlreadyRegisteredError", "Email already registered", "Email 已註冊"),
        error_response(409, "IamMobileAlreadyRegisteredError", "Mobile already registered", "手機已註冊"),
        error_response(422, "IamInputValidationError", "Validation failed", "輸入不符合規則"),
    ),
)
async def iam_register(
    request: Request,
    body: RegisterApplicantInputDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
):
    """申請人註冊；輸入／輸出型別為 `RegisterApplicantInputDTO`／`RegisterApplicantOutputDTO`。"""
    logger.api_info(request.method, str(request.url.path))
    return wrap_iam_use_case_response(request, lambda: factory.register_applicant.execute(body))


@router.post(
    "/auth/login",
    summary="登入（UC-IAM-02）",
    description="密碼模式；若需 MFA 則回傳 challenge_id，否則簽發 token 並建立 session。",
    responses=combine_responses(
        success_response(
            LoginIamOutputDTO(
                mfa_required=False,
                access_token="stub-access-example",
                session_id=UUID("00000000-0000-0000-0000-000000000002"),
                access_token_jti="jti-example",
                refresh_token_jti="rjti-example",
            ).model_dump(mode="json"),
            "登入成功（無 MFA）",
        ),
        error_response(401, "IamInvalidCredentialsError", "Invalid credentials", "憑證錯誤"),
        error_response(401, "IamAccountNotAllowedError", "Account cannot authenticate", "帳戶狀態不允許登入"),
    ),
)
async def iam_login(
    request: Request,
    body: LoginIamInputDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
):
    """登入；輸入／輸出為 `LoginIamInputDTO`／`LoginIamOutputDTO`。"""
    logger.api_info(request.method, str(request.url.path))
    return wrap_iam_use_case_response(request, lambda: factory.login_iam.execute(body))


@router.post(
    "/auth/mfa/verify",
    summary="驗證 MFA（UC-IAM-03）",
    description="比對 OTP、標記 challenge 已驗證並簽發 token／session。",
    responses=combine_responses(
        success_response(
            MfaVerifyOutputDTO(
                access_token="stub-access-example",
                session_id=UUID("00000000-0000-0000-0000-000000000002"),
                access_token_jti="jti-example",
                expires_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ).model_dump(mode="json"),
            "MFA 驗證成功",
        ),
        error_response(401, "IamInvalidCredentialsError", "Invalid MFA code", "驗證碼錯誤"),
        error_response(401, "IamMfaChallengeInvalidError", "MFA challenge invalid", "挑戰無效或過期"),
    ),
)
async def iam_mfa_verify(
    request: Request,
    body: MfaVerifyInputDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
):
    """MFA 驗證；輸入／輸出為 `MfaVerifyInputDTO`／`MfaVerifyOutputDTO`。"""
    logger.api_info(request.method, str(request.url.path))
    return wrap_iam_use_case_response(request, lambda: factory.verify_mfa.execute(body))


@router.post(
    "/auth/refresh",
    summary="更新存取權杖",
    description="以登入／MFA 回傳之 refresh_token 輪替 access／refresh；更新 `iam.sessions`。",
    responses=combine_responses(
        success_response(
            IamRefreshOutputDTO(
                access_token="stub-access-example",
                refresh_token="stub-refresh-example",
                session_id=UUID("00000000-0000-0000-0000-000000000002"),
                access_token_jti="jti-new",
                refresh_token_jti="rjti-new",
                expires_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ).model_dump(mode="json"),
            "成功",
        ),
        error_response(401, "IamRefreshTokenInvalidError", "Invalid refresh", "Refresh 無效或已過期"),
        error_response(422, "IamInputValidationError", "Validation failed", "輸入驗證失敗"),
    ),
)
async def iam_refresh(
    request: Request,
    body: IamRefreshInputDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
):
    """Refresh；輸入為 `IamRefreshInputDTO`（實作完成前拋出應用層 501 錯誤）。"""
    logger.api_info(request.method, str(request.url.path))
    return wrap_iam_use_case_response(request, lambda: factory.refresh.execute(body))


@router.post(
    "/auth/logout",
    summary="登出（撤銷工作階段）",
    description="需 Bearer JWT；本文帶入登入時取得之 `session_id`。",
    responses=combine_responses(
        success_response(
            IamLogoutOutputDTO(
                session_id=UUID("00000000-0000-0000-0000-000000000002"),
                revoked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ).model_dump(mode="json"),
            "已撤銷",
        ),
        error_response(401, "MissingTokenError", "Authentication required", "未認證"),
        error_response(404, "IamSessionNotFoundError", "Session not found", "找不到工作階段"),
    ),
)
async def iam_logout(
    request: Request,
    body: IamLogoutRequestBodyDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
    current_user_id: UUID = Depends(get_current_iam_user_uuid),
):
    """登出；HTTP 本文為 `IamLogoutRequestBodyDTO`，用例輸入為 `IamLogoutInputDTO`。"""
    logger.api_info(request.method, str(request.url.path), user_id=str(current_user_id))
    dto = IamLogoutInputDTO(user_id=current_user_id, session_id=body.session_id)
    return wrap_iam_use_case_response(request, lambda: factory.logout.execute(dto))


@router.get(
    "/auth/me",
    summary="目前使用者 IAM 摘要",
    description="需 Bearer JWT；回傳 iam.users 公開欄位。",
    responses=combine_responses(
        success_response(
            IamMeOutputDTO(
                user_id=UUID("00000000-0000-4000-8000-000000000001"),
                account_type="applicant",
                status="active",
                display_name="範例",
                email="a@b.com",
                mobile=None,
                mfa_enabled=False,
                username=None,
            ).model_dump(mode="json"),
            "查詢成功",
        ),
        error_response(401, "MissingTokenError", "Authentication required", "未認證"),
        error_response(404, "IamUserNotFoundError", "User not found", "使用者不存在"),
    ),
)
async def iam_me(
    request: Request,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
    current_user_id: UUID = Depends(get_current_iam_user_uuid),
):
    """GET /auth/me；回傳 `IamMeOutputDTO`。"""
    logger.api_info(request.method, str(request.url.path), user_id=str(current_user_id))
    return wrap_iam_use_case_response(request, lambda: factory.get_me.execute(current_user_id))


@router.get(
    "/auth/me/permissions",
    summary="目前使用者有效權限代碼",
    description="經角色指派與 role_permissions 展開後去重排序。",
    responses=combine_responses(
        success_response(IamPermissionsOutputDTO(permission_codes=["iam.view_self"]).model_dump(mode="json"), "查詢成功"),
        error_response(401, "MissingTokenError", "Authentication required", "未認證"),
    ),
)
async def iam_me_permissions(
    request: Request,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
    current_user_id: UUID = Depends(get_current_iam_user_uuid),
):
    """GET /auth/me/permissions；回傳 `IamPermissionsOutputDTO`。"""
    logger.api_info(request.method, str(request.url.path), user_id=str(current_user_id))
    return wrap_iam_use_case_response(request, lambda: factory.get_permissions.execute(current_user_id))


@router.post(
    "/admin/users/{userId}/roles",
    summary="指派角色（UC-IAM-04）",
    description="需 Bearer JWT；操作者須具 `iam.assign_roles`。路徑為目標使用者 UUID。",
    responses=combine_responses(
        success_response(
            AssignRoleOutputDTO(
                assignment_id=UUID("10000000-0000-4000-8000-000000000001"),
                target_user_id=UUID("00000000-0000-4000-8000-000000000002"),
                role_code="officer",
            ).model_dump(mode="json"),
            "指派成功",
        ),
        error_response(401, "MissingTokenError", "Authentication required", "未認證"),
        error_response(403, "IamAssignRoleForbiddenError", "Not allowed", "無權指派"),
        error_response(404, "IamUserNotFoundError", "User not found", "目標使用者不存在"),
        error_response(404, "IamRoleNotFoundError", "Role not found", "角色不存在"),
        error_response(422, "IamInputValidationError", "Invalid scope", "scope 不成對或其他驗證失敗"),
    ),
)
async def iam_admin_assign_role(
    request: Request,
    userId: UUID,
    body: AssignRoleRequestBodyDTO,
    factory: IamServiceFactory = Depends(get_iam_service_factory),
    operator_user_id: UUID = Depends(get_current_iam_user_uuid),
):
    """
    管理員指派角色。

    HTTP 本文為 `AssignRoleRequestBodyDTO`；組裝為 `AssignRoleInputDTO` 後呼叫用例服務。
    """
    logger.api_info(request.method, str(request.url.path), user_id=str(operator_user_id))
    inp = AssignRoleInputDTO(
        operator_user_id=operator_user_id,
        target_user_id=userId,
        role_code=body.role_code,
        assignment_id=body.assignment_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
    )
    return wrap_iam_use_case_response(request, lambda: factory.assign_role.execute(inp))
