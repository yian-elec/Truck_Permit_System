"""
Page_Model_Query_Aggregation 應用層錯誤型別與領域例外映射。

責任：
- 定義 App 層可辨識之錯誤類別與 HTTP 語意（status_code）；
- 將 Domain `PageModelDomainError` 映射為適當 App 錯誤，供 API／Controller 統一包裝回應。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from shared.errors.base_error.base_error import BaseError

T = TypeVar("T")


class PageModelAppError(BaseError):
    """
    Page Model 應用層錯誤基底。

    責任：預設對應 HTTP 422；子類覆寫 `status_code` 以對齊 REST 語意。
    """

    @property
    def status_code(self) -> int:
        return 422


class PageModelValidationAppError(PageModelAppError):
    """
    輸入參數或前置條件不合法（例如生命週期階段字串無法解析）。

    責任：對應 400 Bad Request，提示呼叫端修正查詢參數或 body。
    """

    @property
    def status_code(self) -> int:
        return 400


class PageModelConflictAppError(PageModelAppError):
    """
    與目前狀態或資源約束衝突（例如快取鍵寫入衝突，於擴充交易時使用）。

    責任：對應 409 Conflict。
    """

    @property
    def status_code(self) -> int:
        return 409


class PageModelInternalAppError(PageModelAppError):
    """
    組版或目錄發生預期外之領域不變條件違反（多為程式／設定錯誤）。

    責任：對應 500；實際產品可再細分是否對外遮蔽細節。
    """

    @property
    def status_code(self) -> int:
        return 500


def map_page_model_domain_exception_to_app(exc: BaseException) -> PageModelAppError:
    """
    將 Page Model 領域例外映射為 App 層錯誤。

    責任：維持 API 邊界不直接洩漏 Domain 型別，仍保留 message／details 供記錄與除錯。
    """
    from src.contexts.page_model_query_aggregation.domain.errors import (
        DuplicateSectionOrderError,
        InvalidPageModelCompositionError,
        PageModelDomainError,
        PrerequisiteSectionMissingError,
        UnknownSectionCodeError,
    )

    details: dict[str, Any] | None = getattr(exc, "details", None)
    if not isinstance(details, dict):
        details = None

    if isinstance(exc, UnknownSectionCodeError):
        return PageModelInternalAppError(
            exc.message,
            {"unknown_section_code": exc.offending_section_code, **(details or {})},
        )
    if isinstance(exc, DuplicateSectionOrderError):
        return PageModelInternalAppError(exc.message, details)
    if isinstance(exc, PrerequisiteSectionMissingError):
        return PageModelInternalAppError(exc.message, details)
    if isinstance(exc, InvalidPageModelCompositionError):
        return PageModelValidationAppError(exc.message, details)
    if isinstance(exc, PageModelDomainError):
        return PageModelAppError(exc.message, details)
    return PageModelAppError(str(exc), None)


def raise_page_model_domain_as_app(fn: Callable[[], T]) -> T:
    """
    執行可能拋出 `PageModelDomainError` 的呼叫，並轉譯為 App 層錯誤。

    責任：集中 try/except，避免每個用例方法重複包裝。
    """
    from src.contexts.page_model_query_aggregation.domain.errors import PageModelDomainError

    try:
        return fn()
    except PageModelDomainError as e:
        raise map_page_model_domain_exception_to_app(e) from e
