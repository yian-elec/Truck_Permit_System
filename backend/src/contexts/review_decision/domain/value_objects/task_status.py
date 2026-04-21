"""
ReviewTaskStatus — 審查任務狀態值物件。

責任：表達 ReviewTask 生命週期（對應 review.review_tasks.status），
與 UC-REV-01 建立任務、UC-REV-04/05 關閉任務等流程銜接。
"""

from __future__ import annotations

from enum import Enum


class ReviewTaskStatus(str, Enum):
    """
    審查任務狀態枚舉。

    責任：
    - **PENDING**：已建立、尚未分派或尚未開始實質審查。
    - **IN_REVIEW**：進行中，可指派承辦與載入審核頁模型。
    - **CLOSED**：已關閉（核准／駁回／流程結束後）；不可再轉回進行中（除非另開新任務，由 App 協調）。
    """

    PENDING = "pending"
    IN_REVIEW = "in_review"
    CLOSED = "closed"
