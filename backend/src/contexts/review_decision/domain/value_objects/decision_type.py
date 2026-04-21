"""
DecisionType — 決策類型值物件。

責任：表達單筆 review.decisions 的 decision_type；與「核准／駁回／補件互斥」規則搭配，
每一筆決策紀錄僅能擇一類型。
"""

from __future__ import annotations

from enum import Enum


class DecisionType(str, Enum):
    """
    決策類型枚舉。

    責任：
    - **APPROVE**：核准；須滿足路由與候選／調線之前置條件（由聚合與政策驗證）。
    - **REJECT**：駁回；須理由與決策者。
    - **SUPPLEMENT**：補件指示；通常伴隨 SupplementRequest 與評論，須理由與決策者。
    """

    APPROVE = "approve"
    REJECT = "reject"
    SUPPLEMENT = "supplement"
