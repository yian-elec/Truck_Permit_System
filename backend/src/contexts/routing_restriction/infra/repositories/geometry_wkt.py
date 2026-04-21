"""
geometry_wkt — WGS84 WKT 與領域 GeoPoint／RouteGeometry 之輕量轉換。

責任：不依賴 Shapely，以正則解析 POINT、LINESTRING；寫入 PostGIS 前組 WKT 字串。
僅供 Infra repository 使用。
"""

from __future__ import annotations

import re
from typing import List

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.route_geometry import (
    GeometryKind,
    RouteGeometry,
)

_PAIR_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)")


def geo_point_to_point_wkt(p: GeoPoint) -> str:
    """產生 SRID 4326 語意之 POINT WKT（順序：經度 緯度）。"""
    return f"POINT({p.longitude} {p.latitude})"


def route_geometry_linestring_to_wkt(g: RouteGeometry) -> str:
    """將領域 LINESTRING 轉 WKT。"""
    if g.kind != GeometryKind.LINESTRING:
        raise RoutingInvalidValueError("Expected LINESTRING for route line persistence")
    ring = g.rings[0]
    coords = ", ".join(f"{pt.longitude} {pt.latitude}" for pt in ring)
    return f"LINESTRING({coords})"


def parse_point_wkt(wkt: str) -> GeoPoint:
    """自資料庫 ST_AsText 結果解析 POINT。"""
    m = re.search(
        r"POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)",
        wkt.strip(),
        re.IGNORECASE,
    )
    if not m:
        raise RoutingInvalidValueError(f"Unrecognized POINT WKT: {wkt!r}")
    lon, lat = float(m.group(1)), float(m.group(2))
    return GeoPoint(latitude=lat, longitude=lon)


def parse_linestring_wkt(wkt: str) -> RouteGeometry:
    """自 ST_AsText 解析 LINESTRING → RouteGeometry。"""
    m = re.search(
        r"LINESTRING\s*\(\s*(.+)\s*\)",
        wkt.strip(),
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        raise RoutingInvalidValueError(f"Unrecognized LINESTRING WKT: {wkt!r}")
    inner = m.group(1)
    pairs: List[tuple[float, float]] = []
    for lon_s, lat_s in _PAIR_RE.findall(inner):
        pairs.append((float(lon_s), float(lat_s)))
    if len(pairs) < 2:
        raise RoutingInvalidValueError("LINESTRING must have at least two vertices")
    points = tuple(GeoPoint(latitude=lat, longitude=lon) for lon, lat in pairs)
    return RouteGeometry.linestring(points)
