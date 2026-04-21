"""
Application context 專屬領域錯誤。

責任：表達申請案件狀態機、送件條件、可編輯性等違反不變條件時的語意化例外。
僅依賴 shared 的 DomainError 基底，不依賴 Infra / App / API。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from shared.errors.domain_error import DomainError


class ApplicationDomainError(DomainError):
    """
    Application 領域錯誤基底。

    責任：統一此 context 內業務規則違例的父類型，供 App 層捕捉並對應 HTTP／錯誤碼。
    """

    pass


class InvalidDomainValueError(ApplicationDomainError):
    """
    值物件或欄位格式／範圍不符合領域約束。

    責任：例如車牌格式非法、許可期間終早於起、狀態字串不在白名單等。
    """

    pass


class InvalidApplicationStateError(ApplicationDomainError):
    """
    案件狀態不允許執行所請求的領域行為。

    責任：例如在已送件狀態下仍嘗試以「草稿更新」路徑改寫核心欄位。
    """

    def __init__(
        self,
        message: str,
        *,
        current_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        d = dict(details or {})
        if current_status is not None:
            d["current_status"] = current_status
        super().__init__(message, d if d else None)


class CoreDataNotEditableError(ApplicationDomainError):
    """
    當前狀態下不允許直接覆寫核心申請資料。

    責任：對應「submitted 後不可直接覆寫核心資料」；補件應走 supplement_required 與專用流程。
    """

    def __init__(self, message: str, *, current_status: Optional[str] = None) -> None:
        details: Dict[str, Any] = {}
        if current_status is not None:
            details["current_status"] = current_status
        super().__init__(message, details if details else None)


class SubmissionRequirementsNotMetError(ApplicationDomainError):
    """
    送件前檢查未通過（必備附件、車輛、同意條款等）。

    責任：UC-APP-05／UC-APP-06 中「缺漏清單」的領域層表達；可附結構化缺漏原因。
    """

    def __init__(
        self,
        message: str,
        *,
        missing_reason_codes: Optional[list[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        d = dict(details or {})
        if missing_reason_codes:
            d["missing_reason_codes"] = list(missing_reason_codes)
        super().__init__(message, d if d else None)


class VehicleLimitExceededError(ApplicationDomainError):
    """
    超過單一申請案件可綁定的車輛數量上限。

    責任：由領域常數或政策注入之上限在 add_vehicle 時強制檢查。
    """

    pass


class ConsentRequiredError(SubmissionRequirementsNotMetError):
    """
    送件前尚未完成同意條款（consent）之確認。

    責任：對應 consent_accepted_at 必須已設定才可送件之規則。
    """

    pass


class RouteRequestMissingError(SubmissionRequirementsNotMetError):
    """
    送件前檢查要求之路線申請（route request）不存在或未關聯。

    責任：UC-APP-05 明確要求檢查 route request；領域層僅依布林或存在性由 App 層傳入。
    """

    pass
