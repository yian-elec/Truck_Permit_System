"""
RouteGeometry — 領域層幾何表示（不含 PostGIS／Shapely）。

責任：以頂點序列描述線段或環，供規則與路線在領域內傳遞；實際空間相交計算由 Infra Adapter
實作後，將結果以 RuleHit 等形式回灌領域服務。此處僅校驗結構合法性（點數、閉合等）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence, Tuple

from .geo_point import GeoPoint
from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


class GeometryKind(StrEnum):
    """幾何類別：線段路徑或面狀區域（外環＋可選內洞）。"""

    LINESTRING = "linestring"
    POLYGON = "polygon"


@dataclass(frozen=True)
class RouteGeometry:
    """
    路線或限制區域之幾何（WGS84 頂點序列）。

    責任：
    - **LINESTRING**：至少兩個點，表示候選路線或例外路段中心線。
    - **POLYGON**：`rings[0]` 為外環（至少 4 個點且首尾閉合），其餘為洞；用於 forbidden_zone 等。

    不負責：與資料庫 geometry 欄位互轉（屬 Infra）。
    """

    kind: GeometryKind
    rings: Tuple[Tuple[GeoPoint, ...], ...]

    def __post_init__(self) -> None:
        if not self.rings:
            raise RoutingInvalidValueError("RouteGeometry.rings must not be empty")
        if self.kind == GeometryKind.LINESTRING:
            if len(self.rings) != 1:
                raise RoutingInvalidValueError(
                    "LINESTRING geometry must have exactly one ring"
                )
            line = self.rings[0]
            if len(line) < 2:
                raise RoutingInvalidValueError(
                    "LINESTRING must contain at least two distinct vertices"
                )
        elif self.kind == GeometryKind.POLYGON:
            for i, ring in enumerate(self.rings):
                if len(ring) < 4:
                    raise RoutingInvalidValueError(
                        f"Polygon ring {i} must have at least 4 positions (closed ring)"
                    )
                if ring[0] != ring[-1]:
                    raise RoutingInvalidValueError(
                        f"Polygon ring {i} must be closed (first == last point)"
                    )

    @classmethod
    def linestring(cls, points: Sequence[GeoPoint]) -> RouteGeometry:
        """建立 LineString 幾何之工廠方法。"""
        return cls(GeometryKind.LINESTRING, (tuple(points),))

    @classmethod
    def polygon_outer_ring(cls, outer: Sequence[GeoPoint]) -> RouteGeometry:
        """建立僅含外環之 Polygon。"""
        return cls(GeometryKind.POLYGON, (tuple(outer),))
