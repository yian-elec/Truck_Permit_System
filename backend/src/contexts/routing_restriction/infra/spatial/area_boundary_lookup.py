"""
行政區界查詢：依路段幾何中點（ST_LineInterpolatePoint 0.5）判斷所在區名。
"""

from __future__ import annotations

from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
    route_geometry_linestring_to_wkt,
)
from src.contexts.routing_restriction.infra.schema.area_boundaries import AreaBoundaries


def lookup_area_name_for_segment_geometry(session: Session, geometry: RouteGeometry) -> str | None:
    """以路段線段中點查詢 `routing.area_boundaries`；多區命中取面積最小者。"""
    wkt = route_geometry_linestring_to_wkt(geometry)
    seg_geom = sa_func.ST_GeomFromText(wkt, 4326)
    pt = sa_func.ST_LineInterpolatePoint(seg_geom, 0.5)
    stmt = (
        select(AreaBoundaries.area_name)
        .where(
            AreaBoundaries.is_active.is_(True),
            sa_func.ST_Contains(AreaBoundaries.geom, pt),
        )
        .order_by(sa_func.ST_Area(AreaBoundaries.geom).asc())
        .limit(1)
    )
    return session.scalars(stmt).first()


def lookup_area_names_for_segments(
    session: Session, geometries: list[RouteGeometry]
) -> list[str | None]:
    """依序查每段幾何之區名（單一 session，仍為每段一筆查詢）。"""
    return [lookup_area_name_for_segment_geometry(session, g) for g in geometries]
