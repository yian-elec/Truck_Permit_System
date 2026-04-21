"""
依適用之 forbidden 規則幾何，標記本批 road_edges 中須整條 osm_way_id 排除者。
"""

from __future__ import annotations

from typing import Set
from uuid import UUID

from sqlalchemy import exists, literal, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func as sa_func

from src.contexts.routing_restriction.domain.value_objects.routing_enums import RuleType
from src.contexts.routing_restriction.infra.routing.applicable_restriction_rules import (
    ApplicableRulesContext,
)
from src.contexts.routing_restriction.infra.schema.road_edges import RoadEdges
from src.contexts.routing_restriction.infra.schema.rule_geometries import RuleGeometries


def blocked_osm_way_ids_for_batch(
    session: Session,
    batch_id: UUID,
    ctx: ApplicableRulesContext,
) -> Set[int]:
    """
    若 road_edges.geom 與任一 applicable forbidden_zone／forbidden_road 之 rule_geometries.geom
    相交，則該 osm_way_id 列入 blocked（整 way 自圖移除）。
    """
    forbidden_ids = [
        r.rule_id
        for r in ctx.applicable_rules
        if r.rule_type in (RuleType.FORBIDDEN_ZONE.value, RuleType.FORBIDDEN_ROAD.value)
    ]
    if not forbidden_ids:
        return set()

    intersects = exists(
        select(literal(1))
        .select_from(RuleGeometries)
        .where(
            RuleGeometries.rule_id.in_(forbidden_ids),
            sa_func.ST_Intersects(RoadEdges.geom, RuleGeometries.geom),
        )
    )

    stmt = (
        select(RoadEdges.osm_way_id)
        .distinct()
        .where(RoadEdges.batch_id == batch_id)
        .where(intersects)
    )
    rows = session.scalars(stmt).all()
    return {int(x) for x in rows}
