"""
ReviewComment — 評論內容值物件。

責任：封裝「誰、以何種評論類型、寫了什麼」之不可變快照，供 UC-REV-06 寫入
review.review_comments 前通過領域驗證；**不包含** comment_id（由 Infra 指派）。

說明：規格將 ReviewComment 列為 Value Object；持久化主鍵與時間戳由 App/Infra 在通過驗證後補齊。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.contexts.review_decision.domain.errors import ReviewInvalidValueError
from src.contexts.review_decision.domain.value_objects.comment_type import CommentType


@dataclass(frozen=True)
class ReviewComment:
    """
    評論值物件（內容 + 類型 + 建立者）。

    責任：
    - **comment_type**：必須為 internal / supplement / decision_note 之一。
    - **content**：不可空白；長度合理上限避免濫用。
    - **author_user_id**：所有評論必須綁定人員（對應「所有決策必須留理由與人員」之「人員」延伸至評論）。
    """

    comment_type: CommentType
    content: str
    author_user_id: UUID

    def __post_init__(self) -> None:
        text = (self.content or "").strip()
        if not text:
            raise ReviewInvalidValueError("comment content must be non-empty")
        if len(text) > 50_000:
            raise ReviewInvalidValueError("comment content exceeds max length")
        object.__setattr__(self, "content", text)
