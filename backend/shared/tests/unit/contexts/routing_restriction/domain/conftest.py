"""
Routing_Restriction Domain 單元測試 — 共用工廠與固定時間。

隔離：僅標準庫與 `src.contexts.routing_restriction.domain`，無 DB／網路／檔案。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.route_geometry import (
    RouteGeometry,
)

pytestmark = pytest.mark.unit

UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC)


def taipei_like_naive_noon() -> datetime:
    """與 RestrictionWindow.applies_at 搭配之固定牆上時間（naive）。"""
    return datetime(2026, 4, 7, 12, 0, 0)


def point_a() -> GeoPoint:
    return GeoPoint(latitude=25.03, longitude=121.50)


def point_b() -> GeoPoint:
    return GeoPoint(latitude=25.04, longitude=121.51)


def simple_line() -> RouteGeometry:
    return RouteGeometry.linestring([point_a(), point_b()])


def closed_square_polygon() -> RouteGeometry:
    p0 = GeoPoint(25.0, 121.0)
    p1 = GeoPoint(25.01, 121.0)
    p2 = GeoPoint(25.01, 121.01)
    p3 = GeoPoint(25.0, 121.01)
    return RouteGeometry.polygon_outer_ring((p0, p1, p2, p3, p0))


def new_ids() -> tuple[UUID, UUID]:
    return uuid4(), uuid4()
