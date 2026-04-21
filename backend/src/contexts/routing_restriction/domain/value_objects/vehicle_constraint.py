"""
VehicleConstraint — 路線申請所攜車輛條件（值物件）。

責任：對應 route_requests 之 vehicle_weight_ton、vehicle_kind；供規則比對 weight_limit_ton
與未來車種維度擴充。不可變；建立後由 RouteRequest 持有。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass(frozen=True)
class VehicleConstraint:
    """
    申請路線時宣告之車重／車種（語意對齊聚合欄位 vehicle_profile）。

    責任：
    - **weight_ton**：總重或允許重，與規則之 weight_limit_ton 比較（語意由產品定義 ≥ 或 ＞）。
    - **kind**：如 heavy_truck、連結車等，字串封閉集合由匯入與政策約定。
    """

    weight_ton: Optional[Decimal] = None
    kind: Optional[str] = None

    def __post_init__(self) -> None:
        if self.weight_ton is not None and self.weight_ton < 0:
            raise RoutingInvalidValueError("weight_ton must be non-negative when set")

    def is_heavier_or_equal_than(self, limit_ton: Optional[Decimal]) -> bool:
        """
        是否觸及重量閾值（預設語意：申請車重 >= 規則閾值 則規則適用）。

        責任：當申請未填車重時，採保守策略（視為觸及限制）由呼叫端決定；此處若 weight 缺失回傳 True。
        """
        if limit_ton is None:
            return False
        if self.weight_ton is None:
            return True
        return self.weight_ton >= limit_ton
