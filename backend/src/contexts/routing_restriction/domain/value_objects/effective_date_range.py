"""
EffectiveDateRange — 規則生效日期區間（值物件）。

責任：表達 restriction rule 在何日起迄內有效（對應 effective_from / effective_to）；
與「每日時間窗」RestrictionWindow 正交，兩者皆滿足時規則才適用。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass(frozen=True)
class EffectiveDateRange:
    """
    規則生效的曆日範圍（含界與否由呼叫端與產品約定；領域僅保證 from <= to）。

    責任：若僅有單側邊界，另一側以 None 表示「開放式」。
    """

    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    def __post_init__(self) -> None:
        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_from > self.effective_to
        ):
            raise RoutingInvalidValueError(
                "effective_from must be on or before effective_to"
            )

    def contains(self, d: date) -> bool:
        """給定日期是否落在生效區間內（None 邊界視為無限）。"""
        if self.effective_from is not None and d < self.effective_from:
            return False
        if self.effective_to is not None and d > self.effective_to:
            return False
        return True
