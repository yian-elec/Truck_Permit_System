"""
頁面區塊規格（Entity）。

責任：描述 Page Model 中單一邏輯區塊的**身分**（`PageSectionCode`）、**排序**、**是否必填**、
**需由哪些上游角色餵資料**，以及**前置區塊**（載入／渲染順序依賴）。
同一區塊規格由聚合根持有並維護與其他區塊之圖不變條件。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import InvalidPageModelCompositionError
from ..value_objects import PageSectionCode, UpstreamFeedRole


@dataclass(frozen=True)
class PageModelSectionSpec:
    """
    聚合內實體：單一 Page Model 區塊之領域規格。

    責任：
    - `section_code`：區塊唯一識別（於聚合內不可重複）
    - `sort_order`：渲染／資料填充建議順序（聚合內唯一）
    - `is_required_for_render`：若為 True，App 層應保證對應 payload 非空或明確占位
    - `feed_roles`：一個或多個上游角色標籤（可對應多來源合併）
    - `prerequisite_section_codes`：必須先出現於同一 Page Model 之區塊代碼集合
    """

    section_code: PageSectionCode
    sort_order: int
    is_required_for_render: bool
    feed_roles: frozenset[UpstreamFeedRole]
    prerequisite_section_codes: frozenset[PageSectionCode] = frozenset()

    def __post_init__(self) -> None:
        if self.sort_order < 0:
            raise InvalidPageModelCompositionError("sort_order must be non-negative")
        if not self.feed_roles:
            raise InvalidPageModelCompositionError("feed_roles must be non-empty")

    def primary_feed_role(self) -> UpstreamFeedRole:
        """
        供除錯／日誌用之「主要」餵入角色（取最小枚舉字串排序第一個）。

        責任：不影響業務；多角色區塊仍應以完整 `feed_roles` 為準。
        """
        return sorted(self.feed_roles, key=lambda r: r.value)[0]
