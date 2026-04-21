"""
Permit_Document 應用層錯誤型別與領域例外映射。

責任：將 Permit 領域例外轉為 HTTP 語意一致之 App 錯誤；供服務層統一 raise，
API 層可依 status_code 對應回應。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from shared.errors.base_error.base_error import BaseError

T = TypeVar("T")


class PermitAppError(BaseError):
    """
    Permit_Document 應用層錯誤基底。

    責任：預設對應 HTTP 422；子類可覆寫 status_code。
    """

    @property
    def status_code(self) -> int:
        return 422


class PermitNotFoundAppError(PermitAppError):
    """許可證或預期存在之文件／工作單不存在（404）。"""

    @property
    def status_code(self) -> int:
        return 404


class PermitValidationAppError(PermitAppError):
    """輸入不合法、前置條件未滿足、路線資料不足等（400）。"""

    @property
    def status_code(self) -> int:
        return 400


class PermitConflictAppError(PermitAppError):
    """同一申請重複建立許可或與目前狀態衝突（409）。"""

    @property
    def status_code(self) -> int:
        return 409


class PermitForbiddenAppError(PermitAppError):
    """使用者無權存取該申請／許可／文件（403）。"""

    @property
    def status_code(self) -> int:
        return 403


class PermitCertificateFontError(PermitAppError):
    """
    許可證 PDF 無法嵌入／驗證中文字型（CID），無法產出合格正式文件。

    責任：禁止靜默產出僅含 Helvetica 之不可用 PDF；對應 HTTP 500。
    """

    @property
    def status_code(self) -> int:
        return 500


def map_permit_domain_exception_to_app(exc: BaseException) -> PermitAppError:
    """
    將 Permit_Document 領域例外映射為 App 層錯誤。

    責任：區分「輸入／值物件」「建立前提」「狀態衝突」「文件／工作狀態」以利 API 對應狀態碼。
    """
    from src.contexts.permit_document.domain.errors import (
        DocumentJobStateError,
        InvalidPermitStateError,
        InvalidPermitValueError,
        PermitCreationPreconditionError,
        PermitDocumentStateError,
        PermitDomainError,
    )

    if isinstance(exc, InvalidPermitValueError):
        return PermitValidationAppError(exc.message, exc.details)
    if isinstance(exc, PermitCreationPreconditionError):
        return PermitValidationAppError(exc.message, exc.details)
    if isinstance(exc, InvalidPermitStateError):
        return PermitConflictAppError(exc.message, exc.details)
    if isinstance(exc, PermitDocumentStateError):
        return PermitConflictAppError(exc.message, exc.details)
    if isinstance(exc, DocumentJobStateError):
        return PermitConflictAppError(exc.message, exc.details)
    if isinstance(exc, PermitDomainError):
        return PermitAppError(exc.message, exc.details)
    return PermitAppError(str(exc), None)


def raise_permit_domain_as_app(fn: Callable[[], T]) -> T:
    """執行可能拋出 PermitDomainError 的呼叫，並轉為 App 層錯誤。"""
    from src.contexts.permit_document.domain.errors import PermitDomainError

    try:
        return fn()
    except PermitDomainError as e:
        raise map_permit_domain_exception_to_app(e) from e
