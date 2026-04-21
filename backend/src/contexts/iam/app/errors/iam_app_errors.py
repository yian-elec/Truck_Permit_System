"""
iam_app_errors — IAM Application 層錯誤集中定義。

將用例失敗對應到 HTTP 語意，供 API 層統一轉換；不承載領域規則本身。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from shared.errors.app_error.conflict_error import ConflictError
from shared.errors.app_error.forbidden_error import ForbiddenError
from shared.errors.domain_error.not_found_error import NotFoundError
from shared.errors.domain_error.validation_error import ValidationError
from shared.errors.system_error.auth_error import AuthError


class IamEmailAlreadyRegisteredError(ConflictError):
    """UC-IAM-01：Email 已被註冊。"""

    def __init__(self, message: str = "Email already registered", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamMobileAlreadyRegisteredError(ConflictError):
    """UC-IAM-01：手機號碼已被註冊。"""

    def __init__(self, message: str = "Mobile number already registered", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamUserNotFoundError(NotFoundError):
    """查無 IAM 使用者（登入、指派角色等）。"""

    def __init__(self, message: str = "User not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamInvalidCredentialsError(AuthError):
    """UC-IAM-02／03：密碼錯誤、OTP 錯誤或憑證不足。"""

    def __init__(self, message: str = "Invalid credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamAccountNotAllowedError(AuthError):
    """帳戶狀態不允許登入（停用、鎖定、待審等）。"""

    def __init__(self, message: str = "Account cannot authenticate", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamMfaChallengeInvalidError(AuthError):
    """MFA 挑戰不存在、已過期或已使用。"""

    def __init__(self, message: str = "MFA challenge invalid or expired", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamRoleNotFoundError(NotFoundError):
    """UC-IAM-04：角色代碼不存在於 iam.roles。"""

    def __init__(self, message: str = "Role not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamAssignRoleForbiddenError(ForbiddenError):
    """操作者缺少 iam.assign_roles（或等效）權限。"""

    def __init__(self, message: str = "Not allowed to assign roles", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class IamInputValidationError(ValidationError):
    """用例層輸入與領域前置條件不符（顯示名稱、密碼政策等）。"""

    pass


class IamExternalLoginNotSupportedError(ValidationError):
    """外部 IdP 登入尚未於此用例接線（預留）。"""

    pass


class IamRefreshTokenInvalidError(AuthError):
    """Refresh token 無效、已撤銷、已過期或工作階段未啟用 refresh。"""

    def __init__(
        self,
        message: str = "Invalid or expired refresh token",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class IamSessionNotFoundError(NotFoundError):
    """登出時找不到工作階段，或工作階段不屬於當前使用者。"""

    def __init__(self, message: str = "Session not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
