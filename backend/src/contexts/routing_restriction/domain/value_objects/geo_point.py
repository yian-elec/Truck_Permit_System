"""
GeoPoint — WGS84 經緯度值物件。

責任：封裝單一點位並校驗合法範圍（緯度 [-90,90]、經度 [-180,180]），供路線幾何、
起訖點與規則多邊形頂點使用；不可變以避免座標在傳遞中被意外修改。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass(frozen=True)
class GeoPoint:
    """
    單一地理座標點（SRID 4326 語意，單位：度）。

    責任：作為 RouteGeometry 與 geocode 結果之基本單位；KML 之 lon,lat 順序在匯入層轉為本 VO 之 lat/lon 欄位。
    """

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise RoutingInvalidValueError(
                f"latitude out of range [-90, 90]: {self.latitude!r}"
            )
        if not (-180.0 <= self.longitude <= 180.0):
            raise RoutingInvalidValueError(
                f"longitude out of range [-180, 180]: {self.longitude!r}"
            )
