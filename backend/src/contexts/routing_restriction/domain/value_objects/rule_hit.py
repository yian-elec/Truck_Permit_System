"""
RuleHit — 單次規則命中結果（值物件）。

責任：記錄哪條規則、以何嚴重度命中、與候選路線哪個路段相關、以及人類可讀細節；
供排序（forbidden 優先）、例外路段覆蓋後篩選與分數加權。不可變。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from .routing_enums import HitSeverity, RuleType
from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass(frozen=True)
class RuleHit:
    """
    規則檢核產出之一筆命中。

    責任：
    - **rule_id / rule_type**：辨識規則與類型，供 exception_road 覆蓋邏輯判斷。
    - **severity**：對應持久化 **hit_type**（forbidden／warning 等）；FORBIDDEN 通常導致候選不可行
      （除非被例外路段覆蓋）；WARNING 僅影響分數或提示。Infra 對照欄位時應與 `HitSeverity` 值一致。
    - **segment_index**：對應 RouteCandidate.segments 的序位（0-based），映射至 DB 之 segment_id 由 App/Infra 解析；
      None 表示全線或無法歸段。
    - **detail_text**：給使用者／承辦之說明（可含規則名稱摘要）。
    """

    rule_id: UUID
    rule_type: RuleType
    severity: HitSeverity
    segment_index: Optional[int] = None
    detail_text: Optional[str] = None

    def __post_init__(self) -> None:
        if self.segment_index is not None and self.segment_index < 0:
            raise RoutingInvalidValueError("segment_index must be >= 0 when set")
