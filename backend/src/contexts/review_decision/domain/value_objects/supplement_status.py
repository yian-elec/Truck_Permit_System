"""
SupplementRequestStatus — 補件請求狀態值物件。

責任：表達 SupplementRequest 聚合之狀態（對應 review.supplement_requests.status），
與申請人送件／補件回覆之 App 流程銜接（本層只維護合法轉移）。
"""

from __future__ import annotations

from enum import Enum


class SupplementRequestStatus(str, Enum):
    """
    補件請求狀態枚舉。

    責任：
    - **OPEN**：已發出，等待申請人回應。
    - **FULFILLED**：已視為完成（由 App 依 Application 狀態或人工標記驅動）。
    - **CANCELLED**：作廢（例如案件駁回後不再等待補件）。
    """

    OPEN = "open"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
