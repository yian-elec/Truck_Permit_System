"""
ReviewWorkflowPolicy — 審查決策流程領域服務。

責任：
- 落實 **核准／駁回／補件** 與歷史決策之 **互斥與順序**（同一案件在尚未進入新週期前，
  不可在已駁回後再核准、已核准後再駁回／再發補件決策等）。
- 集中校驗「所有決策必須留理由與人員」之 **理由與決策者** 欄位。

說明：本服務 **無狀態**、不依賴儲存庫；呼叫端傳入已發生之 **DecisionType** 序列（由 App 從
read model 或 repository 載入後餵入）。
"""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from src.contexts.review_decision.domain.errors import (
    ReviewDecisionConflictError,
    ReviewInvalidValueError,
)
from src.contexts.review_decision.domain.value_objects import DecisionType


class ReviewWorkflowPolicy:
    """
    審查工作流政策（Domain Service）。

    責任：表達無法自然歸屬於單一聚合之 **跨決策** 規則；與單筆 ReviewDecision 內部不變條件互補。
    """

    @staticmethod
    def require_reason_and_actor(*, reason: str, actor_user_id: UUID) -> None:
        """
        所有決策必須附理由與決策人員。

        責任：對齊規格「所有決策必須留理由與人員」；在建立 ReviewDecision 前呼叫。
        """
        r = (reason or "").strip()
        if not r:
            raise ReviewInvalidValueError("decision reason must be non-empty")
        if len(r) > 20_000:
            raise ReviewInvalidValueError("decision reason exceeds max length")
        # UUID 不為 nil 由型別保證；若專案使用 nil UUID 表示無效，可再加斷言

    @staticmethod
    def assert_new_decision_compatible_with_history(
        *,
        prior_decision_types_in_order: Sequence[DecisionType],
        new_decision: DecisionType,
    ) -> None:
        """
        新決策類型須與既有決策歷史相容（互斥與生命週期）。

        責任（規格「核准／駁回／補件互斥」之跨筆解讀）：
        - 曾 **駁回** 者，不可再 **核准**。
        - 曾 **核准** 者，不可再 **駁回**，亦不可再發 **補件** 類型之決策紀錄。
        - 曾 **駁回** 者，不可再發 **補件** 類型之決策紀錄（補件僅在尚未終結前有意義）。
        - **補件** 可多次發生；**核准／駁回** 各自至多一次且彼此排除。

        若產品允許「駁回後重新送件開新審查週期」，應由 Application 層以 **新 application 版本**
        或 **清空歷史之新 review 會話** 餵入空序列，而非在本政策中硬編開例外。
        """
        prior = list(prior_decision_types_in_order)
        prior_set = set(prior)

        if new_decision == DecisionType.APPROVE:
            if DecisionType.REJECT in prior_set:
                raise ReviewDecisionConflictError(
                    "cannot approve after the application was rejected"
                )
            if DecisionType.APPROVE in prior_set:
                raise ReviewDecisionConflictError("application already has an approval decision")

        if new_decision == DecisionType.REJECT:
            if DecisionType.APPROVE in prior_set:
                raise ReviewDecisionConflictError(
                    "cannot reject after the application was approved"
                )
            if DecisionType.REJECT in prior_set:
                raise ReviewDecisionConflictError("application already has a rejection decision")

        if new_decision == DecisionType.SUPPLEMENT:
            if DecisionType.APPROVE in prior_set:
                raise ReviewDecisionConflictError(
                    "cannot record supplement decision after approval"
                )
            if DecisionType.REJECT in prior_set:
                raise ReviewDecisionConflictError(
                    "cannot record supplement decision after rejection"
                )
