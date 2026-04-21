"""
iam_errors.py — IAM Context 領域錯誤

定義身分與存取管理在領域規則違反時拋出的錯誤，供 App 層對應 HTTP／日誌。
"""

from typing import Any, Dict, Optional

from shared.errors.domain_error import DomainError


class IamDomainError(DomainError):
    """IAM 領域錯誤基底；所有 IAM 業務規則例外皆繼承此類別。"""

    pass


class InvalidUserStateError(IamDomainError):
    """使用者狀態不允許執行該操作（例如已停用仍嘗試登入相關假設）。"""

    def __init__(
        self,
        message: str = "User is not in a valid state for this operation",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class OfficerAdminRequiresRoleError(IamDomainError):
    """承辦（officer）或管理者（admin）必須至少擁有一筆角色指派（核心規則）。"""

    def __init__(
        self,
        message: str = "Officer and admin accounts must have at least one role assignment",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class OfficerAdminRequiresMfaError(IamDomainError):
    """承辦與管理者強制啟用 MFA（核心規則）。"""

    def __init__(
        self,
        message: str = "Officer and admin accounts must have MFA enabled",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class InvalidCredentialInvariantError(IamDomainError):
    """密碼與外部身分欄位組合違反不變條件（須至少一種可驗證身分來源）。"""

    def __init__(
        self,
        message: str = "User must have password hash or external identity reference",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)


class InvalidDisplayNameError(IamDomainError):
    """顯示名稱為必填且不可為空白。"""

    pass


class SessionNotActiveError(IamDomainError):
    """Session 已撤銷或過期，不可再視為有效連線。"""

    pass


class MfaChallengeExpiredError(IamDomainError):
    """MFA 挑戰已超過有效期限。"""

    pass


class MfaChallengeAlreadyVerifiedError(IamDomainError):
    """MFA 挑戰已完成驗證，不可重複驗證。"""

    pass


class InvalidIamIdError(IamDomainError):
    """UUID 型識別欄位格式不合法（UserId、SessionId 等）。"""

    pass


class InvalidIamCodeFormatError(IamDomainError):
    """RoleCode／PermissionCode 等代碼字串違反長度或非空約束。"""

    pass


class InvalidAssignmentScopePairError(IamDomainError):
    """角色指派範圍 scope_type 與 scope_id 未成對（僅能皆空或皆有值）。"""

    pass


class SessionInvariantViolationError(IamDomainError):
    """Session 聚合不變條件違反（例如 JTI 為空、過期時間不晚於簽發時間）。"""

    pass


class MfaChallengeInvariantViolationError(IamDomainError):
    """MfaChallenge 聚合不變條件違反（例如 code_hash 為空、效期不合法）。"""

    pass
