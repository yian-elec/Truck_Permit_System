"""
SupplementItem — 補件項目值物件。

責任：描述單一補件要求（代碼、名稱、要求動作、選填說明），由 SupplementRequest 聚合持有；
不可變更時複製替換（immutable dataclass），以維護聚合內集合的一致性。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.review_decision.domain.errors import ReviewInvalidValueError
from src.contexts.review_decision.domain.value_objects.required_action import (
    SupplementRequiredAction,
)


@dataclass(frozen=True)
class SupplementItem:
    """
    補件項目（對應 review.supplement_items 一列的領域語意，不含 supplement_item_id）。

    責任：
    - 驗證 item_code／item_name 非空白與長度上限（與 DB varchar 對齊）。
    - 綁定 **SupplementRequiredAction**，避免未註冊之動作字串。
    """

    item_code: str
    item_name: str
    required_action: SupplementRequiredAction
    note: str | None = None

    def __post_init__(self) -> None:
        code = (self.item_code or "").strip()
        name = (self.item_name or "").strip()
        if not code:
            raise ReviewInvalidValueError("item_code must be non-empty")
        if len(code) > 50:
            raise ReviewInvalidValueError("item_code exceeds max length 50")
        if not name:
            raise ReviewInvalidValueError("item_name must be non-empty")
        if len(name) > 100:
            raise ReviewInvalidValueError("item_name exceeds max length 100")
        if self.note is not None and len(self.note) > 10_000:
            raise ReviewInvalidValueError("note exceeds reasonable max length")
        object.__setattr__(self, "item_code", code)
        object.__setattr__(self, "item_name", name)
