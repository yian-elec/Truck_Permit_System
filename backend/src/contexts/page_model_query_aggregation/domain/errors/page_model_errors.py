"""
Page_Model_Query_Aggregation 領域錯誤。

責任：表達「畫面模型組版」違反不變條件時的語意化例外（重複區塊順序、缺少前置區塊、未知區塊代碼等）。
僅繼承共用 `DomainError`；不依賴 Infra / App / API。
"""

from __future__ import annotations

from typing import Any

from shared.errors.domain_error import DomainError


class PageModelDomainError(DomainError):
    """
    Page Model 領域錯誤基底。

    責任：統一本 context 內與區塊目錄、聚合不變條件相關之業務違例父類型。
    """


class InvalidPageModelCompositionError(PageModelDomainError):
    """
    聚合內區塊集合整體不符合領域不變條件（泛用）。

    責任：當違規無法細分為更具體子類型時使用；偏好拋出具體子類以利 App 層對應訊息。
    """


class UnknownSectionCodeError(PageModelDomainError):
    """
    使用了目錄未登記的區塊代碼。

    責任：防止任意字串成為區塊識別，維持與 `PageModelSectionCatalog` 之封閉集合一致。

    注意：`BaseError` 已提供唯讀屬性 `code`（錯誤類別名稱），故未登記之區塊代碼改存於
    `details["unknown_section_code"]`，並以 `offending_section_code` 讀取。
    """

    def __init__(self, message: str, *, code: str | None = None) -> None:
        details: dict[str, Any] = {}
        if code is not None:
            details["unknown_section_code"] = code
        super().__init__(message, details if details else None)

    @property
    def offending_section_code(self) -> str | None:
        """目錄中找不到的 `PageSectionCode.value`（若建立時有傳入）。"""
        if not self.details:
            return None
        raw = self.details.get("unknown_section_code")
        return str(raw) if raw is not None else None


class DuplicateSectionOrderError(PageModelDomainError):
    """
    同一 Page Model 內出現重複的排序序號。

    責任：確保前端能以穩定順序渲染區塊；序號在聚合內必須唯一。
    """

    def __init__(self, message: str, *, sort_order: int | None = None) -> None:
        super().__init__(message)
        self.sort_order = sort_order


class PrerequisiteSectionMissingError(PageModelDomainError):
    """
    某區塊宣告了前置區塊，但該前置區塊未包含於同一聚合之區塊列表中。

    責任：表達「資料載入／渲染依賴順序」在領域上的完整性；App 層應依此前後關聯決定查詢順序。
    """

    def __init__(
        self,
        message: str,
        *,
        section: str | None = None,
        missing_prerequisite: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.section = section
        self.missing_prerequisite = missing_prerequisite
        self.details = details or {}
