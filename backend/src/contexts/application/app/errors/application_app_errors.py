"""
Application App 層錯誤型別。

責任：將領域例外、儲存層 LookupError、驗證失敗等轉為 API 可對應之統一錯誤物件；
繼承 `shared.errors.base_error.BaseError`，與專案既有錯誤序列化格式一致。
"""

from __future__ import annotations

from shared.errors.base_error.base_error import BaseError


class ApplicationAppError(BaseError):
    """
    Application 應用層錯誤基底。

    責任：預設對應 HTTP 422（無法處理的業務規則）；子類可覆寫 status_code。
    """

    @property
    def status_code(self) -> int:
        return 422


class ApplicationNotFoundAppError(ApplicationAppError):
    """案件或子資源不存在（對應 404）。"""

    @property
    def status_code(self) -> int:
        return 404


class ApplicationValidationAppError(ApplicationAppError):
    """輸入格式／值域不符合領域約束（對應 400）。"""

    @property
    def status_code(self) -> int:
        return 400


class ApplicationConflictAppError(ApplicationAppError):
    """與目前狀態或資源約束衝突（對應 409）。"""

    @property
    def status_code(self) -> int:
        return 409


class ApplicationSubmissionBlockedAppError(ApplicationAppError):
    """
    送件或補件條件未滿足。

    責任：對應 UC-APP-05／UC-APP-06 缺漏清單；details 可含 missing_reason_codes。
    """

    @property
    def status_code(self) -> int:
        return 422


def map_domain_exception_to_app(exc: BaseException) -> ApplicationAppError:
    """
    將 Application 領域例外映射為 App 層錯誤。

    責任：服務層捕捉 `ApplicationDomainError` 後呼叫，保留 cause 與結構化 details。
    """
    from src.contexts.application.domain.errors import (
        ApplicationDomainError,
        CoreDataNotEditableError,
        InvalidApplicationStateError,
        InvalidDomainValueError,
        SubmissionRequirementsNotMetError,
        VehicleLimitExceededError,
    )

    if isinstance(exc, InvalidDomainValueError):
        return ApplicationValidationAppError(exc.message, exc.details)
    if isinstance(exc, VehicleLimitExceededError):
        return ApplicationConflictAppError(exc.message, exc.details)
    if isinstance(exc, CoreDataNotEditableError):
        return ApplicationConflictAppError(exc.message, exc.details)
    if isinstance(exc, InvalidApplicationStateError):
        return ApplicationConflictAppError(exc.message, exc.details)
    if isinstance(exc, SubmissionRequirementsNotMetError):
        return ApplicationSubmissionBlockedAppError(exc.message, exc.details)
    if isinstance(exc, ApplicationDomainError):
        return ApplicationAppError(exc.message, exc.details)
    return ApplicationAppError(str(exc), None)


def wrap_lookup_error(exc: LookupError) -> ApplicationNotFoundAppError:
    """將儲存層 LookupError（找不到聚合／附件）轉為 404 App 錯誤。"""
    return ApplicationNotFoundAppError(
        str(exc),
        details={"kind": "lookup_error"},
    )


def rethrow_if_app_error(exc: BaseException) -> ApplicationAppError | None:
    """
    若已是 App 層錯誤則直接回傳以供重新拋出。

    責任：避免重複包裝。
    """
    if isinstance(exc, ApplicationAppError):
        return exc
    return None


def to_app_error(exc: BaseException) -> ApplicationAppError:
    """
    統一入口：LookupError → 404；ApplicationDomainError → 映射；其餘 → 通用 App 錯誤。
    """
    existing = rethrow_if_app_error(exc)
    if existing is not None:
        return existing
    if isinstance(exc, LookupError):
        return wrap_lookup_error(exc)
    from src.contexts.application.domain.errors import ApplicationDomainError

    if isinstance(exc, ApplicationDomainError):
        return map_domain_exception_to_app(exc)
    details = getattr(exc, "details", None)
    if isinstance(details, dict):
        return ApplicationAppError(str(exc), details)
    return ApplicationAppError(str(exc), None)
