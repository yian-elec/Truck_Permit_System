"""
RestrictionRule — 限制規則聚合根。

責任：封裝單筆限制規則之身份、類型、重量／方向／時段／生效期間／優先級與空間幾何集合；
維持「啟用規則應具備可評估之幾何」等不變條件，並提供是否適用於給定車輛與日期之查詢。
與 RoutePlan 分屬不同聚合：規則為參考資料邊界，透過 ID 與候選之 RuleHit 關聯。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Sequence, Tuple
from uuid import UUID

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError
from src.contexts.routing_restriction.domain.value_objects.effective_date_range import (
    EffectiveDateRange,
)
from src.contexts.routing_restriction.domain.value_objects.restriction_window import (
    RestrictionWindow,
)
from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    RoutingDirection,
    RuleType,
)
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)


@dataclass
class RestrictionRule:
    """
    限制規則（對應 routing.restriction_rules + rule_geometries + rule_time_windows 之領域聚合）。

    責任：
    - **rule_type**：驅動檢核語意（禁區／禁路／例外路等）。
    - **geometries**：同一規則可對應多個面或線（MultiGeometry 匯入）；空間運算在 Infra，領域保存結構。
    - **time_windows / effective_range**：時間維度；完整「是否命中」需結合出發時間由領域服務協調。
    - **priority**：數值越小越優先（或越大越優先由產品定義；本類提供比較輔助）。
    """

    rule_id: UUID
    layer_id: UUID
    rule_name: str
    rule_type: RuleType
    priority: int
    is_active: bool = True
    weight_limit_ton: Decimal | None = None
    direction: RoutingDirection = RoutingDirection.ANY
    time_rule_text: str | None = None
    time_windows: Tuple[RestrictionWindow, ...] = field(default_factory=tuple)
    effective_range: EffectiveDateRange = field(
        default_factory=EffectiveDateRange
    )
    geometries: Tuple[RouteGeometry, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not (self.rule_name or "").strip():
            raise RoutingInvalidValueError("rule_name must be non-empty")
        if self.priority < 0:
            raise RoutingInvalidValueError("priority must be non-negative")

    def assert_evaluable_when_active(self) -> None:
        """
        啟用中之規則在納入檢核前應具幾何（例外：純文字政策規則可於 App 層另案處理）。

        責任：防止未轉檔完畢之規則進入引擎造成靜默略過。
        """
        if self.is_active and len(self.geometries) == 0:
            raise RoutingInvalidValueError(
                f"Active rule {self.rule_id} must have at least one geometry"
            )

    def applies_by_vehicle_weight(self, vehicle: VehicleConstraint) -> bool:
        """
        依車重判斷本規則是否可能適用（僅重量維度）。

        責任：無 weight_limit_ton 時視為與車重無關；有閾值時使用 VehicleConstraint 之語意比較。
        """
        if self.weight_limit_ton is None:
            return True
        return vehicle.is_heavier_or_equal_than(self.weight_limit_ton)

    def applies_on_calendar_date(self, d: date) -> bool:
        """規則在該曆日是否處於生效區間。"""
        return self.effective_range.contains(d)

    def applies_at_departure(
        self,
        departure: datetime,
        *,
        is_public_holiday: bool,
    ) -> bool:
        """
        規則是否於給定出發時間點適用（曆日 + 時間窗 OR 語意）。

        責任：先確認 `effective_range`；若無任何結構化 **time_windows**，視為該曆日全日適用；
        若有，則**任一時間窗**命中即視為時間維度適用（與多段禁行描述一致）。
        """
        if not self.applies_on_calendar_date(departure.date()):
            return False
        if not self.time_windows:
            return True
        return any(
            w.applies_at(departure, is_public_holiday=is_public_holiday)
            for w in self.time_windows
        )

    def deactivate(self) -> None:
        """將規則標為停用（不刪除歷史資料）。"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """重新啟用；呼叫端應先確保幾何與版本發布流程已完成。"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def replace_geometries(self, geometries: Sequence[RouteGeometry]) -> None:
        """更新與規則連結之幾何集合（匯入或編修後）。"""
        self.geometries = tuple(geometries)
        self.updated_at = datetime.utcnow()

    def replace_time_windows(self, windows: Sequence[RestrictionWindow]) -> None:
        """更新結構化時間窗。"""
        self.time_windows = tuple(windows)
        self.updated_at = datetime.utcnow()
