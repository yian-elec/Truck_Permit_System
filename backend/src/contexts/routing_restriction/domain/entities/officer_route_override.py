"""
OfficerRouteOverride — 承辦人工改線實體。

責任：封裝 UC-ROUTE-05 寫入之覆蓋路徑幾何、原因與建立者；與 `RoutePlan` 分屬不同一致性邊界
（以 application_id 關聯案件），後續由 App 觸發對覆蓋線重新執行規則檢核並更新計畫狀態。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError
from src.contexts.routing_restriction.domain.value_objects.route_geometry import (
    GeometryKind,
    RouteGeometry,
)


@dataclass
class OfficerRouteOverride:
    """
    人工改線紀錄（對應 routing.officer_route_overrides）。

    責任：
    - **override_geom** 必須為 LineString 語意（承辦手動路徑）。
    - **override_reason** 不可空白，滿足稽核與對外說明。
    - **base_candidate_id** 可為空（例如自無候選狀態強制畫線）。
    """

    override_id: UUID
    application_id: UUID
    override_geom: RouteGeometry
    override_reason: str
    created_by: UUID
    base_candidate_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not (self.override_reason or "").strip():
            raise RoutingInvalidValueError("override_reason must be non-empty")
        if self.override_geom.kind != GeometryKind.LINESTRING:
            raise RoutingInvalidValueError(
                "override_geom must be a LINESTRING for officer override"
            )
