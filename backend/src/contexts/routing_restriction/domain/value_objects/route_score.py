"""
RouteScore — 候選路線分數（值物件）。

責任：封裝數值化分數與可選分解因子（距離、時間、風險加權等），供排序候選；
保持不可變；調整分數時應建立新實例。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Optional

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass(frozen=True)
class RouteScore:
    """
    候選路線綜合分數（越高越好或越低越好由產品定義；此處僅儲存數值與後設）。

    責任：**value** 為主排序鍵；**breakdown** 可記錄各項加扣分以便除錯與 UI 呈現。
    """

    value: Decimal
    breakdown: Optional[Mapping[str, Decimal]] = None

    def __post_init__(self) -> None:
        if self.breakdown is not None and not isinstance(self.breakdown, Mapping):
            raise RoutingInvalidValueError("breakdown must be a mapping when set")
