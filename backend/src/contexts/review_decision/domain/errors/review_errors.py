"""
Review_Decision context 專屬領域錯誤。

責任：表達審查任務狀態、決策不變條件、補件聚合、評論內容等違例；供 App 層對應 HTTP／錯誤碼。
僅依賴 shared 的 DomainError 基底，不依賴 Infra、App、API。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from shared.errors.domain_error import DomainError


class ReviewDomainError(DomainError):
    """
    Review_Decision 領域錯誤基底。

    責任：統一本 bounded context 內業務規則違例的父類型。
    """

    pass


class ReviewInvalidValueError(ReviewDomainError):
    """
    值物件或欄位不符合領域約束（空白理由、非法枚舉、期間顛倒等）。

    責任：在 VO／聚合建構或狀態轉移時立即失敗，避免不合法資料進入持久化流程。
    """

    pass


class InvalidReviewTaskStateError(ReviewDomainError):
    """
    審查任務當前狀態不允許所請求的領域行為。

    責任：例如已關閉之任務仍嘗試分派、未開啟即關閉等。
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


class ReviewDecisionRuleError(ReviewDomainError):
    """
    決策相關不變條件違反（核准前路由條件、互斥流程、缺理由／決策者等）。

    責任：與 InvalidReviewTaskStateError 分離，便於 App 層區分「任務狀態」與「決策規則」錯誤。
    """

    pass


class ReviewDecisionConflictError(ReviewDecisionRuleError):
    """
    與歷史決策序列衝突（例如已駁回後仍核准、已核准後再補件決策等）。

    責任：落實「核准／駁回／補件」在案件生命週期內的互斥與順序規則（由 ReviewWorkflowPolicy 觸發）。
    """

    pass


class InvalidSupplementRequestStateError(ReviewDomainError):
    """
    補件請求當前狀態不允許變更（例如已結案後修改項目）。

    責任：保護 SupplementRequest 聚合的不變條件。
    """

    pass
