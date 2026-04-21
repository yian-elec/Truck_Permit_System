"""
自 Overpass element 解析單一 way → 可入庫欄位（失敗則略過並計數）。
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Sequence, Tuple

from src.contexts.routing_restriction.infra.road_data.bbox_and_signature import bbox_polygon_wkt
from src.contexts.routing_restriction.infra.road_data.osm_road_naming import (
    road_name_from_osm_tags,
    road_ref_for_column,
)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(min(1.0, math.sqrt(a)))
    return r * c


def linestring_wkt_from_overpass_geometry(
    geometry: Sequence[Mapping[str, Any]],
) -> Optional[str]:
    if len(geometry) < 2:
        return None
    parts = []
    for g in geometry:
        if "lat" not in g or "lon" not in g:
            return None
        parts.append(f"{float(g['lon'])} {float(g['lat'])}")
    return "LINESTRING(" + ",".join(parts) + ")"


def bbox_polygon_wkt_from_geometry(
    geometry: Sequence[Mapping[str, Any]],
) -> Optional[str]:
    lons = [float(g["lon"]) for g in geometry if "lon" in g and "lat" in g]
    lats = [float(g["lat"]) for g in geometry if "lon" in g and "lat" in g]
    if not lons:
        return None
    west, east = min(lons), max(lons)
    south, north = min(lats), max(lats)
    return bbox_polygon_wkt(south, west, north, east)


def approximate_length_m(geometry: Sequence[Mapping[str, Any]]) -> int:
    if len(geometry) < 2:
        return 0
    total = 0.0
    for i in range(len(geometry) - 1):
        a, b = geometry[i], geometry[i + 1]
        total += _haversine_m(
            float(a["lat"]),
            float(a["lon"]),
            float(b["lat"]),
            float(b["lon"]),
        )
    return max(1, int(round(total)))


def try_parse_way_for_road_edge(
    way: Mapping[str, Any],
) -> Tuple[Optional[dict[str, Any]], bool]:
    """
    Returns (payload dict for ORM insert sans ids/timestamps, skipped_bool).

    skipped True：無 geometry／點數不足／缺 highway／nodes 與 geometry 點數不一致。
    """
    if way.get("type") != "way":
        return None, True
    tags = dict(way.get("tags") or {})
    hw = tags.get("highway")
    if hw is None or (isinstance(hw, str) and not hw.strip()):
        return None, True
    if not isinstance(hw, str):
        hw = str(hw)
    geom = way.get("geometry")
    if not geom or not isinstance(geom, list) or len(geom) < 2:
        return None, True
    line_wkt = linestring_wkt_from_overpass_geometry(geom)
    if not line_wkt:
        return None, True
    nodes_raw = way.get("nodes") or []
    try:
        nodes = [int(n) for n in nodes_raw]
    except (TypeError, ValueError):
        return None, True
    if len(nodes) != len(geom):
        return None, True

    road_name = road_name_from_osm_tags(tags)
    ref_col = road_ref_for_column(tags)
    bbox_wkt = bbox_polygon_wkt_from_geometry(geom)
    length_m = approximate_length_m(geom)

    payload = {
        "osm_element_type": "way",
        "osm_way_id": int(way["id"]),
        "segment_index": 0,
        "road_name": road_name[:255],
        "road_ref": ref_col,
        "highway_type": hw[:100],
        "line_wkt": line_wkt,
        "bbox_wkt": bbox_wkt,
        "node_count": len(geom),
        "length_m": length_m,
        "raw_tags_json": tags,
        "raw_payload_fragment": {"nodes": nodes},
    }
    return payload, False
