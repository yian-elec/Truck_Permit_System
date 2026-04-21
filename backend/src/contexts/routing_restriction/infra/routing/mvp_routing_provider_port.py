"""
MVP 路網候選：自 Overpass/OSM 取得區域內道路，組無向圖最短路徑，產出 RouteCandidate／RouteSegment。

責任：不處理單行道、不保證可駕駛；僅供 UC-ROUTE-02 後續 KML／PostGIS 規則檢核使用。

輸入／輸出與 MVP 前置完整規格見：``docs/mvp_routing_provider_contract.md``（相對於 ``routing_restriction`` context 根目錄；章節 §0–§12）。
"""

from __future__ import annotations

import heapq
import json
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

import httpx

from shared.core.config import settings
from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.domain.entities.route_segment import RouteSegment
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import VehicleConstraint
from src.contexts.routing_restriction.infra.repositories.map_layers_repository import MapLayersRepository
from src.contexts.routing_restriction.infra.road_data.osm_road_naming import (
    road_name_from_osm_tags,
    way_has_osm_name_or_ref,
)
from src.contexts.routing_restriction.infra.routing.applicable_restriction_rules import (
    load_applicable_rules_context,
)
from src.contexts.routing_restriction.infra.routing.blocked_osm_way_ids import (
    blocked_osm_way_ids_for_batch,
)
from src.contexts.routing_restriction.infra.routing.mvp_highway_cost import (
    mvp_edge_routing_cost_meters,
)
from src.contexts.routing_restriction.infra.road_data.osm_road_ingest_service import (
    OsmRoadIngestService,
    load_overpass_elements_for_batch,
)
from src.contexts.routing_restriction.infra.road_data.overpass_query import (
    build_overpass_highway_query,
)

def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(min(1.0, math.sqrt(a)))
    return r * c


def _road_display_name(tags: Mapping[str, Any]) -> str:
    return road_name_from_osm_tags(tags)


def _osm_tag_preview(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return str(v)


def _log_mvp_segment_osm_tags_for_naming_audit(
    *,
    seq_no: int,
    osm_way_id: int,
    tags: Mapping[str, Any],
    resolved_road_name: str,
) -> None:
    """
    除錯用：列出與路名解析相關之 OSM 欄位（含系統未用於顯示之 name:zh 等）及完整 tags JSON。
    顯示邏輯仍僅 name → ref → fallback，見 road_name_from_osm_tags。
    """
    try:
        tags_obj = dict(tags)
        tags_json = json.dumps(tags_obj, ensure_ascii=False, sort_keys=True)
    except TypeError:
        tags_json = str(tags)
    max_len = 4000
    if len(tags_json) > max_len:
        tags_json = tags_json[:max_len] + "…(truncated)"
    fb = settings.osm_road_name_fallback
    logger.info(
        "MVP segment OSM tags (naming audit)",
        context="Routing",
        seq_no=seq_no,
        osm_way_id=osm_way_id,
        resolved_road_name=resolved_road_name,
        is_fallback_name=(resolved_road_name == fb),
        fallback_configured=fb,
        tag_name=_osm_tag_preview(tags.get("name")),
        tag_ref=_osm_tag_preview(tags.get("ref")),
        tag_name_zh=_osm_tag_preview(tags.get("name:zh")),
        tag_name_en=_osm_tag_preview(tags.get("name:en")),
        tag_highway=_osm_tag_preview(tags.get("highway")),
        all_tag_keys=",".join(sorted(str(k) for k in tags)),
        tags_json=tags_json,
    )


def _bbox_pad(
    origin: GeoPoint,
    destination: GeoPoint,
    *,
    pad_deg: float = 0.02,
) -> Tuple[float, float, float, float]:
    south = min(origin.latitude, destination.latitude) - pad_deg
    north = max(origin.latitude, destination.latitude) + pad_deg
    west = min(origin.longitude, destination.longitude) - pad_deg
    east = max(origin.longitude, destination.longitude) + pad_deg
    return south, west, north, east


@dataclass(frozen=True)
class _DirectedEdge:
    way_id: int
    tags: Mapping[str, Any]
    points: Tuple[GeoPoint, ...]


def _collect_node_coordinates(elements: Sequence[Mapping[str, Any]]) -> Dict[int, Tuple[float, float]]:
    coords: Dict[int, Tuple[float, float]] = {}
    for el in elements:
        if el.get("type") == "node" and "lat" in el and "lon" in el:
            coords[int(el["id"])] = (float(el["lat"]), float(el["lon"]))
    for el in elements:
        if el.get("type") != "way":
            continue
        nodes = el.get("nodes") or []
        geom = el.get("geometry") or []
        for i, nid in enumerate(nodes):
            if nid in coords:
                continue
            if i < len(geom) and "lat" in geom[i] and "lon" in geom[i]:
                coords[int(nid)] = (float(geom[i]["lat"]), float(geom[i]["lon"]))
    return coords


def _build_graph_and_edges(
    elements: Sequence[Mapping[str, Any]],
    coords: Mapping[int, Tuple[float, float]],
) -> Tuple[
    Dict[int, List[Tuple[int, float]]],
    Dict[Tuple[int, int], _DirectedEdge],
]:
    """無向邊權重為「幾何公尺 × highway × readability」（見 mvp_highway_cost）；雙向皆記於 edge_meta。"""
    adj: Dict[int, List[Tuple[int, float]]] = {}
    edge_meta: Dict[Tuple[int, int], _DirectedEdge] = {}

    def add_adj(u: int, v: int, w: float) -> None:
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))

    for el in elements:
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        hw = tags.get("highway")
        if hw is None or not str(hw).strip():
            continue
        if settings.mvp_routing_require_way_name_or_ref and not way_has_osm_name_or_ref(tags):
            continue
        way_id = int(el["id"])
        nodes = [int(n) for n in (el.get("nodes") or [])]
        geom = el.get("geometry") or []
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            if a not in coords or b not in coords:
                continue
            la, lo = coords[a]
            lb, lo2 = coords[b]
            dist = _haversine_m(la, lo, lb, lo2)
            w = mvp_edge_routing_cost_meters(dist, tags)
            if w is None or w <= 0:
                continue
            pts: List[GeoPoint] = []
            if i < len(geom) and "lat" in geom[i]:
                pts.append(GeoPoint(latitude=float(geom[i]["lat"]), longitude=float(geom[i]["lon"])))
            else:
                pts.append(GeoPoint(latitude=la, longitude=lo))
            if i + 1 < len(geom) and "lat" in geom[i + 1]:
                pts.append(
                    GeoPoint(
                        latitude=float(geom[i + 1]["lat"]),
                        longitude=float(geom[i + 1]["lon"]),
                    )
                )
            else:
                pts.append(GeoPoint(latitude=lb, longitude=lo2))
            if len(pts) < 2:
                pts = [GeoPoint(latitude=la, longitude=lo), GeoPoint(latitude=lb, longitude=lo2)]
            meta = _DirectedEdge(way_id=way_id, tags=tags, points=tuple(pts))
            add_adj(a, b, w)
            edge_meta[(a, b)] = meta
            edge_meta[(b, a)] = meta

    return adj, edge_meta


def _walkable_nodes_from_adj(adj: Mapping[int, List[Tuple[int, float]]]) -> Set[int]:
    s: Set[int] = set(adj.keys())
    for nbrs in adj.values():
        for v, _ in nbrs:
            s.add(v)
    return s


def _nearest_node(
    lat: float,
    lon: float,
    coords: Mapping[int, Tuple[float, float]],
    *,
    allowed_node_ids: Optional[Set[int]] = None,
) -> Optional[int]:
    best: Optional[Tuple[float, int]] = None
    for nid, (clat, clon) in coords.items():
        if allowed_node_ids is not None and nid not in allowed_node_ids:
            continue
        d = _haversine_m(lat, lon, clat, clon)
        if best is None or d < best[0]:
            best = (d, nid)
    return best[1] if best else None


def _filter_elements_drop_blocked_ways(
    elements: Sequence[Mapping[str, Any]],
    blocked_osm_way_ids: Set[int],
) -> List[Mapping[str, Any]]:
    if not blocked_osm_way_ids:
        return list(elements)
    out: List[Mapping[str, Any]] = []
    for el in elements:
        if el.get("type") == "way" and int(el["id"]) in blocked_osm_way_ids:
            continue
        out.append(el)
    return out


def _dijkstra(
    adj: Mapping[int, List[Tuple[int, float]]],
    start: int,
    goal: int,
) -> Optional[List[int]]:
    if start == goal:
        return [start]
    dist: Dict[int, float] = {start: 0.0}
    prev: Dict[int, int] = {}
    pq: List[Tuple[float, int]] = [(0.0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        if u == goal:
            break
        for v, w in adj.get(u, ()):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if goal not in dist:
        return None
    path: List[int] = []
    cur = goal
    while cur != start:
        path.append(cur)
        p = prev.get(cur)
        if p is None:
            return None
        cur = p
    path.append(start)
    path.reverse()
    return path


def _merge_path_to_segments(
    path: Sequence[int],
    edge_meta: Mapping[Tuple[int, int], _DirectedEdge],
) -> List[Tuple[_DirectedEdge, ...]]:
    """將路徑依連續同 way_id 合併為路段群。"""
    if len(path) < 2:
        return []
    groups: List[List[_DirectedEdge]] = []
    current: List[_DirectedEdge] = []
    last_way: Optional[int] = None
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        edge = edge_meta.get((a, b))
        if edge is None:
            return []
        if last_way is None or edge.way_id != last_way:
            if current:
                groups.append(current)
            current = [edge]
            last_way = edge.way_id
        else:
            current.append(edge)
    if current:
        groups.append(current)
    out: List[Tuple[_DirectedEdge, ...]] = []
    for g in groups:
        out.append(tuple(g))
    return out


def _combine_edge_points(group: Sequence[_DirectedEdge]) -> RouteGeometry:
    pts: List[GeoPoint] = []
    for j, edge in enumerate(group):
        ep = list(edge.points)
        if j == 0:
            pts.extend(ep)
        else:
            pts.extend(ep[1:])
    return RouteGeometry.linestring(pts)


def parse_overpass_response_for_routing(
    payload: Mapping[str, Any],
) -> Tuple[Dict[int, List[Tuple[int, float]]], Dict[Tuple[int, int], _DirectedEdge], Dict[int, Tuple[float, float]]]:
    elements = list(payload.get("elements") or [])
    coords = _collect_node_coordinates(elements)
    adj, edge_meta = _build_graph_and_edges(elements, coords)
    return adj, edge_meta, coords


def mvp_candidates_from_graph(
    origin: GeoPoint,
    destination: GeoPoint,
    adj: Mapping[int, List[Tuple[int, float]]],
    edge_meta: Mapping[Tuple[int, int], _DirectedEdge],
    coords: Mapping[int, Tuple[float, float]],
) -> List[RouteCandidate]:
    if not coords:
        return []
    walkable = _walkable_nodes_from_adj(adj)
    if not walkable:
        return []
    start = _nearest_node(
        origin.latitude,
        origin.longitude,
        coords,
        allowed_node_ids=walkable,
    )
    goal = _nearest_node(
        destination.latitude,
        destination.longitude,
        coords,
        allowed_node_ids=walkable,
    )
    if start is None or goal is None:
        return []
    path = _dijkstra(adj, start, goal)
    if not path or len(path) < 2:
        return []

    from uuid import uuid4

    groups = _merge_path_to_segments(path, edge_meta)
    if not groups:
        return []

    segments: List[RouteSegment] = []
    line_points: List[GeoPoint] = []
    total_m = 0
    names: List[str] = []

    cand_id = uuid4()
    for seq, group in enumerate(groups):
        geom = _combine_edge_points(group)
        ring = geom.rings[0]
        seg_dist = 0
        for i in range(len(ring) - 1):
            seg_dist += int(
                round(_haversine_m(ring[i].latitude, ring[i].longitude, ring[i + 1].latitude, ring[i + 1].longitude))
            )
        if seg_dist < 1 and len(ring) >= 2:
            seg_dist = max(1, int(round(_haversine_m(ring[0].latitude, ring[0].longitude, ring[-1].latitude, ring[-1].longitude))))
        total_m += seg_dist
        tags = group[0].tags
        rname = road_name_from_osm_tags(tags)
        _log_mvp_segment_osm_tags_for_naming_audit(
            seq_no=seq,
            osm_way_id=group[0].way_id,
            tags=tags,
            resolved_road_name=rname,
        )
        names.append(rname)
        dur = max(1, int(seg_dist / 13.9)) if seg_dist else 1
        seg = RouteSegment(
            segment_id=uuid4(),
            candidate_id=cand_id,
            seq_no=seq,
            distance_m=seg_dist,
            duration_s=dur,
            geometry=geom,
            road_name=rname,
            instruction_text=None,
            is_exception_road=False,
        )
        segments.append(seg)
        if not line_points:
            line_points.extend(ring)
        else:
            line_points.extend(list(ring)[1:])

    line_geom = RouteGeometry.linestring(line_points)
    total_dur = max(1, sum(s.duration_s for s in segments))
    summary = " → ".join(names)

    cand = RouteCandidate(
        candidate_id=cand_id,
        route_plan_id=cand_id,
        candidate_rank=1,
        distance_m=max(1, total_m),
        duration_s=total_dur,
        line_geometry=line_geom,
        score=None,
        summary_text=summary,
        segments=segments,
        rule_hits=[],
    )
    return [cand]


class MvpRoutingProviderPort:
    """
    先經道路資料層抓取並入庫，再自 ``road_edges`` 還原 way 集合組圖；失敗時回退為空列表。

    責任：失敗或無路徑時回傳空列表（與 ROUTING_PROVIDER_EMPTY 語意相容）。
    """

    def __init__(
        self,
        *,
        overpass_url: str = "https://overpass-api.de/api/interpreter",
        timeout_s: float = 60.0,
        client: httpx.Client | None = None,
        bbox_pad_deg: float | None = None,
        ingest_service: OsmRoadIngestService | None = None,
        map_layers: MapLayersRepository | None = None,
    ) -> None:
        self._url = overpass_url
        self._timeout = timeout_s
        self._bbox_pad = (
            bbox_pad_deg if bbox_pad_deg is not None else settings.road_fetch_bbox_pad_deg
        )
        self._own_client = client is None
        self._client = client or httpx.Client(timeout=timeout_s)
        self._ingest = ingest_service or OsmRoadIngestService(
            overpass_url=overpass_url,
            timeout_s=timeout_s,
            client=self._client,
        )
        self._map_layers = map_layers or MapLayersRepository()
        self._routing_empty_hint: str | None = None

    def consume_routing_empty_hint(self) -> str | None:
        """最近一次 `fetch_candidates` 若回傳空列表，此處可取人類可讀原因（讀取後清除）。"""
        h = self._routing_empty_hint
        self._routing_empty_hint = None
        return h

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def __enter__(self) -> MvpRoutingProviderPort:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_candidates(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        *,
        vehicle: VehicleConstraint | None = None,
        departure_at: datetime | None = None,
    ) -> List[RouteCandidate]:
        vc = vehicle if vehicle is not None else VehicleConstraint()
        self._routing_empty_hint = None
        batch_id, ingest_err = self._ingest.fetch_parse_and_persist(origin, destination)
        if batch_id is None:
            self._routing_empty_hint = ingest_err or (
                "Road data ingest failed (see logs for Overpass or persistence errors)."
            )
            logger.info(
                "MVP fetch_candidates: ingest failed or no batch (Overpass error logged separately)",
                context="Routing",
                overpass_url=self._url,
                ingest_error_excerpt=(ingest_err or "")[:240],
            )
            return []

        elements = load_overpass_elements_for_batch(batch_id)
        if not elements:
            self._routing_empty_hint = (
                "No drivable OSM ways were stored for this map area (parsed batch empty). "
                "Try increasing ROAD_FETCH_BBOX_PAD_DEG or check Overpass response."
            )
            logger.info(
                "MVP fetch_candidates: no ways from road_edges for this batch",
                context="Routing",
                batch_id=str(batch_id),
            )
            return []

        blocked: Set[int] = set()
        layer = self._map_layers.get_latest_published_layer()
        if settings.mvp_routing_apply_forbidden_prefilter and layer is not None:
            with get_session() as session:
                ctx = load_applicable_rules_context(
                    session,
                    layer_id=layer.layer_id,
                    vehicle=vc,
                    departure_at=departure_at,
                )
                blocked = blocked_osm_way_ids_for_batch(session, batch_id, ctx)

        if blocked:
            filtered = _filter_elements_drop_blocked_ways(elements, blocked)
            if not filtered and settings.mvp_routing_fallback_unfiltered_when_all_blocked:
                logger.warn(
                    "MVP fetch_candidates: every way in batch matched forbidden prefilter; "
                    "falling back to unfiltered graph (attach_rule_hits still validates)",
                    context="Routing",
                    batch_id=str(batch_id),
                    blocked_way_count=len(blocked),
                    way_count_before_filter=len(elements),
                )
                filtered = list(elements)
            elif not filtered:
                self._routing_empty_hint = (
                    "All OSM ways in the request area were excluded by the forbidden-zone prefilter "
                    "and MVP_ROUTING_FALLBACK_UNFILTERED_WHEN_ALL_BLOCKED is false. "
                    "Enable fallback or adjust rules if appropriate."
                )
                logger.warn(
                    "MVP fetch_candidates: all ways excluded by forbidden prefilter and fallback disabled",
                    context="Routing",
                    batch_id=str(batch_id),
                    blocked_way_count=len(blocked),
                )
                return []
            elements = filtered
        else:
            elements = list(elements)

        if not elements:
            self._routing_empty_hint = "No way elements left to build the routing graph after filtering."
            logger.info(
                "MVP fetch_candidates: no way elements to build graph",
                context="Routing",
                batch_id=str(batch_id),
            )
            return []
        payload = {"elements": elements}
        adj, edge_meta, coords = parse_overpass_response_for_routing(payload)
        cands = mvp_candidates_from_graph(origin, destination, adj, edge_meta, coords)
        if not cands:
            self._routing_empty_hint = (
                "No route found between origin and destination on the built graph "
                "(disconnected graph, missing nodes near endpoints, or MVP_ROUTING_REQUIRE_WAY_NAME_OR_REF "
                "excluding all connecting ways)."
            )
        logger.info(
            "MVP fetch_candidates: graph built and shortest path done",
            context="Routing",
            batch_id=str(batch_id),
            blocked_way_count=len(blocked),
            require_way_name_or_ref=settings.mvp_routing_require_way_name_or_ref,
            way_elements=len(elements),
            graph_nodes=len(coords),
            candidate_count=len(cands),
        )
        return cands
