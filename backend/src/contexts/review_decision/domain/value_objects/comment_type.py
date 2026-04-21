"""
CommentType — 評論類型值物件。

責任：落實「評論分 internal / supplement / decision_note」之領域分類，
對應 review.review_comments.comment_type。
"""

from __future__ import annotations

from enum import Enum


class CommentType(str, Enum):
    """
    評論類型枚舉。

    責任：
    - **INTERNAL**：內部承辦註記，不對申請人公開（由 App／API 授權控制是否暴露）。
    - **SUPPLEMENT**：與補件溝通相關之說明。
    - **DECISION_NOTE**：決策說明／附註（可與 decision.reason 並存但語意不同：評論為時間序列紀錄）。
    """

    INTERNAL = "internal"
    SUPPLEMENT = "supplement"
    DECISION_NOTE = "decision_note"
