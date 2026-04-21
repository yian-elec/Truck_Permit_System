"""
UC-ROUTE-02：候選產出後附加行政區路名序列（查 PostGIS 區界 + 純函式格式化）。
"""

from __future__ import annotations

from dataclasses import replace

from shared.core.config import settings
from shared.core.db.connection import get_session

from src.contexts.routing_restriction.app.services.route_area_road_formatter import (
    format_area_road_sequence,
)
from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.infra.spatial.area_boundary_lookup import (
    lookup_area_names_for_segments,
)


class RouteAreaEnrichmentService:
    """以路段幾何查區界並寫入 `area_road_sequence`。"""

    def enrich_candidates(self, candidates: list[RouteCandidate]) -> list[RouteCandidate]:
        if not candidates:
            return candidates
        fb = settings.osm_road_name_fallback
        out: list[RouteCandidate] = []
        with get_session() as session:
            for cand in candidates:
                segs = sorted(cand.segments, key=lambda s: s.seq_no)
                areas = lookup_area_names_for_segments(session, [s.geometry for s in segs])
                pairs: list[tuple[str | None, str | None]] = [
                    (s.road_name, areas[i]) for i, s in enumerate(segs)
                ]
                seq = format_area_road_sequence(pairs, unnamed_label=fb)
                out.append(replace(cand, area_road_sequence=seq))
        return out
