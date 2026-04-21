"""
PostGIS 實作 SpatialRuleHitPort：候選路段與 rule_geometries 做 ST_Intersects。
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import List, Sequence
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.sql import func as sa_func

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.routing_restriction.app.services.ports.outbound import SpatialRuleHitPort
from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.domain.value_objects.route_geometry import GeometryKind, RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.rule_hit import RuleHit
from src.contexts.routing_restriction.domain.value_objects.routing_enums import HitSeverity, RuleType
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import VehicleConstraint
from src.contexts.routing_restriction.infra.repositories.map_layers_repository import MapLayersRepository
from src.contexts.routing_restriction.infra.routing.applicable_restriction_rules import (
    load_applicable_rules_context,
)
from src.contexts.routing_restriction.infra.schema.rule_geometries import RuleGeometries


def _linestring_wkt_from_route_geometry(g: RouteGeometry) -> str:
    if g.kind != GeometryKind.LINESTRING:
        raise ValueError("segment geometry must be LINESTRING for hit test")
    pts = g.rings[0]
    body = ",".join(f"{p.longitude} {p.latitude}" for p in pts)
    return f"LINESTRING({body})"


def _severity_for_rule_type(rt: str) -> HitSeverity:
    try:
        t = RuleType(rt)
    except ValueError:
        return HitSeverity.WARNING
    if t in (RuleType.FORBIDDEN_ZONE, RuleType.FORBIDDEN_ROAD):
        return HitSeverity.FORBIDDEN
    return HitSeverity.WARNING


class PostgisSpatialRuleHitPort(SpatialRuleHitPort):
    """
    以最新已發布 map layer 之規則幾何與候選路段做相交測試。

    時間窗細節可後續補齊；目前僅用 effective 日期與車重閾值篩選規則。
    """

    def __init__(self, *, map_layers: MapLayersRepository | None = None) -> None:
        self._layers = map_layers or MapLayersRepository()

    def attach_rule_hits(
        self,
        candidates: Sequence[RouteCandidate],
        *,
        vehicle: VehicleConstraint,
        departure_at: datetime | None,
    ) -> List[RouteCandidate]:
        layer = self._layers.get_latest_published_layer()
        if layer is None:
            logger.info(
                "attach_rule_hits: no published map layer, skipping ST_Intersects",
                context="Routing",
                candidates=len(candidates),
            )
            return list(candidates)

        layer_id = layer.layer_id

        with get_session() as session:
            ctx = load_applicable_rules_context(
                session,
                layer_id=layer_id,
                vehicle=vehicle,
                departure_at=departure_at,
            )
            applicable = ctx.applicable_rules
            if not applicable:
                logger.info(
                    "attach_rule_hits: no rules apply after date/vehicle filter",
                    context="Routing",
                    layer_id=str(layer_id),
                )
                return list(candidates)

            rule_ids = [r.rule_id for r in applicable]
            rule_meta = {r.rule_id: r for r in applicable}
            geoms_by_rule = ctx.geoms_by_rule
            geom_rows = [g for gs in geoms_by_rule.values() for g in gs]

            logger.info(
                "attach_rule_hits: ST_Intersects segment vs rule geometries",
                context="Routing",
                layer_id=str(layer_id),
                applicable_rule_count=len(applicable),
                geometry_row_count=len(geom_rows),
                candidate_count=len(candidates),
            )

            out: List[RouteCandidate] = []
            for cand in candidates:
                hits: List[RuleHit] = []
                seen: set[tuple[UUID, int]] = set()
                for seg_idx, seg in enumerate(cand.segments):
                    try:
                        wkt = _linestring_wkt_from_route_geometry(seg.geometry)
                    except ValueError:
                        continue
                    seg_el = WKTElement(wkt, srid=4326)
                    for rid in rule_ids:
                        meta = rule_meta[rid]
                        try:
                            rt_enum = RuleType(meta.rule_type)
                        except ValueError:
                            rt_enum = RuleType.FORBIDDEN_ZONE
                        for rg in geoms_by_rule.get(rid, []):
                            g_row = session.get(RuleGeometries, rg.geometry_id)
                            if g_row is None:
                                continue
                            inter = session.scalar(
                                select(sa_func.ST_Intersects(seg_el, g_row.geom))
                            )
                            if inter:
                                key = (rid, seg_idx)
                                if key in seen:
                                    continue
                                seen.add(key)
                                sev = _severity_for_rule_type(meta.rule_type)
                                hits.append(
                                    RuleHit(
                                        rule_id=rid,
                                        rule_type=rt_enum,
                                        severity=sev,
                                        segment_index=seg_idx,
                                        detail_text=(meta.rule_name or "")[:500],
                                    )
                                )
                merged = replace(cand, rule_hits=list(cand.rule_hits) + hits)
                out.append(merged)
                n_forbidden = sum(1 for h in hits if h.severity == HitSeverity.FORBIDDEN)
                n_warning = sum(1 for h in hits if h.severity == HitSeverity.WARNING)
                logger.info(
                    "attach_rule_hits: candidate segment checks done",
                    context="Routing",
                    candidate_rank=cand.candidate_rank,
                    segments=len(cand.segments),
                    new_hits=len(hits),
                    forbidden=n_forbidden,
                    warning=n_warning,
                )
            return out
